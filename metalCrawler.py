import certifi
import urllib3
import os
import logging
import json
import threading
import queue
import time
import pprint
from bs4 import BeautifulSoup, NavigableString, Tag
from diagramCreator import *
import re

em_link_main = 'https://www.metal-archives.com/'
em_link_label = em_link_main + 'labels/'
bands = 'bands/'
bandsQueue = queue.Queue()
ajaxLinks = queue.Queue()

lineup_mapping = {"Current lineup": "Current", "Last known lineup": "Last known", "Past members": "past"}

# 8 might be a bit high (leaves some forbidden messages on getting the JSON
# data or the bands).
threadCount = 8


class VisitBandThread(threading.Thread):

    def __init__(self, thread_id, band_links, database, lock):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = "BandVisitor_" + thread_id
        self.bandLinks = band_links
        self.database = database
        self.logger = logging.getLogger('Crawler')
        self.logger.debug("Initializing " + self.name)
        self.lock = lock

    def run(self):
        self.logger.debug("Running " + self.name)
        while self.bandLinks.qsize() != 0:
            link_band_temp = self.bandLinks.get_nowait()
            try:
                result = crawl_band(link_band_temp)
            except Exception:
                self.logger.exception("Something bad happened while crawling.")

            # Error case: putting the link back into circulation.
            if result == -1:
                self.bandLinks.put(link_band_temp)
                continue

            temp_band_data = result[0]
            temp_artist_data = result[1]
            temp_label_data = result[2]

            self.lock.acquire()
            try:
                for artist in temp_artist_data:
                    if artist in self.database["artists"]:
                        for band in temp_artist_data[artist]["bands"]:
                            self.database["artists"][artist]["bands"][band] = temp_artist_data[artist]["bands"][band]
                    else:
                        self.database["artists"][artist] = temp_artist_data[artist]

                for band in temp_band_data:
                    self.database["bands"][band] = temp_band_data[band]
                for label in temp_label_data:
                    if label not in self.database["labels"]:
                        self.database["labels"][label]=temp_label_data[label]
            except:
                self.logger.error("Writing artists failed! This is bad.")
            finally:
                self.lock.release()


class VisitBandListThread(threading.Thread):

    def __init__(self, thread_id, country_links, band_links):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = "BandListVisitor_" + thread_id
        self.countryLinks = country_links
        self.bandLinks = band_links
        self.logger = logging.getLogger('Crawler')
        self.logger.debug("Initializing " + self.name)

    def run(self):
        self.logger.debug("Running " + self.name)
        link_counter = 0

        while self.countryLinks.qsize() != 0:
            link_country_temp = self.countryLinks.get_nowait()
            http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
            country_json = http.request('GET', link_country_temp)
            json_data_string = country_json.data.decode("utf-8")
            json_data_string = json_data_string.replace("\"sEcho\": ,", '')
            json_data = None
            self.logger.debug("  Working on:" + link_country_temp)

            try:
                json_data = json.loads(json_data_string)
            except:
                self.logger.error("  JSON error for [" + link_country_temp + "]. Putting it back in circulation...")
                self.countryLinks.put(link_country_temp)

            if json_data is not None:
                for band in json_data["aaData"]:
                    index_first_apostrophe = band[0].find("'")
                    index_second_apostrophe = band[0].find("'", index_first_apostrophe + 1)
                    band_link = band[0][index_first_apostrophe + 1:index_second_apostrophe]
                    index_first_closing_bracket = band[0].find(">")
                    index_second_opening_bracket = band[0].find("<", index_first_closing_bracket)
                    band_name = band[0][index_first_closing_bracket + 1:index_second_opening_bracket]
                    self.logger.debug("    {}: {}".format(band_name, band_link))
                    # We do not need the leading "https://www.metal-archives.com/bands/".
                    self.bandLinks.put(band_link[37:len(band_link)])
                    link_counter += 1

        self.logger.debug("Finished {} and added {} links.".format(self.name, str(link_counter)))


def display_children(c):
    if c is not None:
        print(c)
        for e in c:
            display_children(e)


def is_not_empty_string_or_live(s):
    if not s:
        return False
    elif "(live)" in s:
        if s[0:6] == "(live)":
            return False
        else:
            return True
    else:
        return True


def cut_instruments(instrument_string):
    collection = {}

    # if '1' not in instrument_string or '2' not in instrument_string:
    if not bool(re.search(r'\d', instrument_string)):
        collection[instrument_string.lstrip().rstrip()] = []
        return collection

    temp_instruments = instrument_string.split(',')
    instruments = ''
    has_found_multi_year = False
    time_spans = []

    for element in temp_instruments:
        element = element.lstrip().rstrip()

        if '(' not in element and not has_found_multi_year:
            instruments += element + ', '
        elif has_found_multi_year:
            has_closing_parenthesis = element.find(')')
            if has_closing_parenthesis is -1:
                time_spans.append(element)
            else:
                temp_time_span = element[0:has_closing_parenthesis].lstrip().rstrip()
                time_spans.append(temp_time_span)
                has_found_multi_year = False
                # Append and reset.
                collection[instruments] = time_spans
                time_spans = []
                instruments = ''
        else:
            index_parenthesis = element.find('(')
            # Test if the letter immediately after the parentheses is a number.
            is_number_after_parentheses = str.isdigit(element[index_parenthesis + 1:index_parenthesis + 2])
            # Found a year after an instrument.
            if is_number_after_parentheses:
                # Attach instrument. We now need to to get the time span(s).
                instruments += element[0:index_parenthesis]
                has_closing_parenthesis = element.find(')')
                # In this special case we must continue in next loop to extract the following parts.
                if has_closing_parenthesis is -1:
                    inner_part = element[index_parenthesis + 1:].lstrip().rstrip()
                    has_found_multi_year = True
                    time_spans.append(inner_part)
                # If we have a closing parenthesis we can append and continue.
                else:
                    inner_part = element[index_parenthesis + 1:has_closing_parenthesis].lstrip().rstrip()
                    # Append and reset.
                    time_spans.append(inner_part)
                    collection[instruments] = time_spans
                    time_spans = []
                    instruments = ''
            # Found a detail for the instrument.
            else:
                idx_opening_parenthesis_1 = element.find('(')
                idx_opening_parenthesis_2 = element.rfind('(')
                is_index_different = idx_opening_parenthesis_1 is not idx_opening_parenthesis_2
                # Instrument detail with time span. Comes in different versions:
                # Guitars (acoustic)(1989-1998); Cut, append and reset right away.
                # Guitars (acoustic)(1989-1998
                # If the second closing parenthesis is missing, the rest will be in next element.
                if idx_opening_parenthesis_1 >= 0 and is_index_different:
                    temp_instrument = element[0:idx_opening_parenthesis_2]
                    index_first_closing_parenthesis = element.find(')')
                    index_second_closing_parenthesis = element.rfind(')')
                    is_index_different = index_first_closing_parenthesis is not index_second_closing_parenthesis
                    # Guitars (acoustic)(1989-1998); Cut, append and reset right away.
                    if index_second_closing_parenthesis >= 0 and is_index_different:
                        time_span = element[idx_opening_parenthesis_2 + 1:index_second_closing_parenthesis]
                        time_span = time_span.lstrip().rstrip()
                        time_spans.append(time_span)
                        collection[temp_instrument] = time_spans
                        time_spans = []
                        instruments = ''
                    else:
                        instruments += temp_instrument
                        time_spans.append(element[idx_opening_parenthesis_2 + 1:].lstrip().rstrip())
                        has_found_multi_year = True
                # Instrument detail without time span: Guitar (acoustic)
                else:
                    instruments += element + ','

    return collection


def visit_band_list(country_link, start_index, band_links):
    logger = logging.getLogger('Crawler')
    link_country_temp = country_link + str(start_index)
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    country_json = http.request('GET', link_country_temp)
    json_data_string = country_json.data.decode("utf-8")
    json_data_string = json_data_string.replace("\"sEcho\": ,", '')
    json_data = json.loads(json_data_string)

    for band in json_data["aaData"]:
        index_first_apostrophe = band[0].find("'")
        index_second_apostrophe = band[0].find("'", index_first_apostrophe + 1)
        band_link = band[0][index_first_apostrophe + 1:index_second_apostrophe]
        logger.debug("  link: " + band_link)
        index_first_closing_bracket = band[0].find(">")
        index_second_opening_bracket = band[0].find("<", index_first_closing_bracket)
        band_name = band[0][index_first_closing_bracket + 1:index_second_opening_bracket]
        logger.debug("  name: " + band_name)
        band_links[band_name] = band_link


def crawl_country(link_country):
    logger = logging.getLogger('Crawler')
    logger.debug(">>> Crawling Country: " + link_country)
    json_data_string = ""
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    while True:
        country_json = http.request('GET', link_country)
        json_data_string = country_json.data.decode("utf-8")

        if "Forbidden." not in json_data_string:
            break
        else:
            logger.debug("  trying again...")
            time.sleep(.5)

    json_data_string = json_data_string.replace("\"sEcho\": ,", '')
    json_data = json.loads(json_data_string)

    # The total amount of entries for this country is the only data we need for now.
    amount_entries = json_data["iTotalRecords"]
    logger.debug("  Country has [{}] entries.".format(amount_entries))
    # Limit imposed by MA.
    display_constant = 500
    # Amount of runs needed.
    needed_run_count = (amount_entries // display_constant)

    # We need at least one and always one more (because of the division rounding down).
    if amount_entries % display_constant > 0:
        needed_run_count += 1

    thread_count = 8

    # Override number of threads in case we don't need all.
    if needed_run_count < thread_count:
        thread_count = needed_run_count

    logger.debug("  Setting up to do [{}] runs with [{}] threads.".format(str(needed_run_count), str(thread_count)))
    link_suffix = "json/1?sEcho=1&iDisplayStart="

    # Prepare the AJAX links for the actual run.
    for i in range(0, amount_entries, display_constant):
        ajaxLinks.put_nowait(link_country + link_suffix + str(i))
        logger.debug("    Prepping link: " + str(i))

    threads = []

    # Create threads and let them run.
    for i in range(0, thread_count):
        thread = VisitBandListThread(str(i), ajaxLinks, bandsQueue)
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    logger.debug("<<< Crawling Country")


def crawl_countries():
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    countries_page = http.request('GET', "https://www.metal-archives.com/browse/country")
    soup = BeautifulSoup(countries_page.data, "html.parser")
    s = soup.find_all(attrs={"class": "countryCol"})
    country_links = []

    for i in range(0, len(s)):
        for j in range(1, len(s[i].contents), 3):
            temp_link = s[i].contents[j].attrs["href"]
            country_short = temp_link[len(temp_link) - 2:len(temp_link)]
            country_links.append("https://www.metal-archives.com/browse/ajax-country/c/" + country_short)

    return country_links


def crawl_band(band_short_link):
    # TODO: Change your environment or this won't work!
    # The % escaped glyphs only work if the client.py in http
    # is changed in putrequest() before self._output() is called.
    # The line looks like this:
    # url = rfc3986.uri_reference(url).unsplit()
    # Needs to import rfc3986
    link_band = em_link_main + bands + band_short_link
    logger = logging.getLogger('Crawler')
    logger.debug('>>> Crawling [' + band_short_link + ']')

    # Initialize the pool manager with certificates.  There will be nasty warnings for every call if you don't.
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    while True:
        band_page = http.request('GET', link_band)
        band_data_string = band_page.data.decode("utf-8")

        if "Forbidden." not in band_data_string:
            break
        else:
            logger.debug("  trying again...")
            time.sleep(.5)

    soup = BeautifulSoup(band_page.data, "html.parser")
    # soup = BeautifulSoup(bandPage.data, "lxml")
    logger.debug("  Start scraping from actual band.")
    # Finds band name; needs to extract the ID later.
    s = soup.find_all(attrs={"class": "band_name"})

    if len(s) == 0:
        logger.fatal("  Did not find the attribute band_name for {}.".format(band_short_link))
        logger.debug("  Band page source for reference:")
        logger.debug(band_page.data)
        return -1

    # All data of a band is collected here.  Band members are referenced and collected in their own collection.
    band_data = {}
    band_id = band_short_link[band_short_link.rfind('/') + 1:]
    band_data[band_id] = {}
    band_data[band_id]["link"] = band_short_link
    band_data[band_id]["name"] = str(s[0].next_element.text)

    s = soup.find_all(attrs={"class": "float_left"})
    band_data[band_id]["country"] = s[1].contents[3].contents[0]
    country_node = s[1].contents[3].contents[0]
    country_name = country_node.contents[0]
    # Saving the country name and link in a dict.
    country_link = country_node.attrs["href"]
    band_data[band_id]["country"] = {country_name: country_link}
    location=s[1].contents[7].text

    if location != "N/A":
        location = location.split("/")

    band_data[band_id]["location"] = location
    # band_data[band_id]["location"] = s[1].contents[7].contents[0].split("/")
    band_data[band_id]["status"] = s[1].contents[11].text
    band_data[band_id]["formed"] = s[1].contents[15].text
    band_data[band_id]["active"] = []
    artist_data = {}
    s = soup.find_all(attrs={"class": "clear"})

    # Iterate over all time spans the band was (or is) active.
    for element in s[3].contents[3].contents:
        active = element
        if type(active) is NavigableString:
            active = active.replace('\t', '')
            active = active.replace('),', '')
            active = active.replace('\n', '')
            active = active.replace(' ', '')
            year_tokens = active.split(',')
            for yearToken in year_tokens:
                # TODO: Very strange case for bands which changed their name. Maybe we want to pass on that time span.
                if yearToken != ')':
                    band_data[band_id]["active"].append(yearToken)
        elif type(active) is Tag:
            previous_name = " " + active.contents[0]
            last_position = len(band_data[band_id]["active"]) - 1
            band_data[band_id]["active"][last_position] += previous_name + ")"
        else:
            logger.warning("  Found an element of type {}. This should not happen.".format(type(active)))

    s = soup.find_all(attrs={"class": "float_right"})
    band_data[band_id]["genre"] = s[3].contents[3].contents[0].split(', ')
    band_data[band_id]["theme"] = s[3].contents[7].contents[0].split(', ')
    label_node = s[3].contents[11].contents[0]

    if type(label_node) is NavigableString:
        label_name = str(s[3].contents[11].contents[0])
        if label_name is "Unsigned/independent":
            label_id = -1
        else:
            label_id = label_name
        label_link = ""
    else:
        label_name = label_node.contents[0]
        label_link = label_node.attrs["href"][len(em_link_label):]
        label_id = label_link[label_link.find('/') + 1:]

    band_data[band_id]["label"] = label_id
    label_data = {label_id: {"name": label_name, "link": label_link}}
    artists_and_bands = soup.find_all(attrs={"class": "ui-tabs-panel-content"})
    artists_and_band_element = artists_and_bands[0]
    logger.debug("  Scraping artists from actual band.")
    actual_category = artists_and_band_element.contents[1].contents
    band_data[band_id]["lineup"] = {}
    lineup_finder = soup.find_all(attrs={"href": "#band_tab_members_all"})
    is_lineup_diverse = True

    if len(lineup_finder) == 0:
        is_lineup_diverse = False

    # The elements alternate from a band member to bands or member to
    # member if it's the only band for the latter.
    # Category (like current or past) are found at index.
    for i in range(1, len(actual_category), 2):
        actual_row = actual_category[i]
        last_found_header = actual_row.attrs["class"][0]

        # Normal case.
        if last_found_header == "lineupHeaders":
            header_category = actual_row.contents[1].contents[0].rstrip().lstrip().replace('\t', '')
            logger.debug("  Found header: {}".format(header_category))
        # Special case where a band only has one line-up.
        elif last_found_header == "lineupRow":
            # If a band has only one lineup (current, last-known or past) the usual headers will be missing on the page.
            # For active bands with changing lineup we get 'Current'.
            # For a band with no lineup changes it will be empty.
            if not is_lineup_diverse:
                test_header2 = str(soup.find_all(attrs={"href": "#band_tab_members_current"})[0].contents[0])
                header_category = lineup_mapping[test_header2]
                logger.debug("  Didn't find a header. Digging deeper: {}".format(header_category))
        if header_category not in band_data[band_id]["lineup"]:
            band_data[band_id]["lineup"][header_category] = []

        # Five elements for artists.
        if len(actual_row) is 5:
            # The leading part ist not needed and stripped
            # (https://www.metal-archives.com/artists/).  It's always 39
            # letters long.
            temp_artist_link = actual_row.contents[1].contents[1].attrs["href"][39:]
            temp_artist_id = temp_artist_link[temp_artist_link.find('/') + 1:]
            temp_artist_name = str(actual_row.contents[1].contents[1].contents[0])
            logger.debug("    Recording artist data for " + temp_artist_name)
            band_data[band_id]["lineup"][header_category].append(temp_artist_id)
            # TODO: Take care of pseudonyms.
            artist_data[temp_artist_id] = {}
            artist_data[temp_artist_id]["link"] = temp_artist_link
            artist_data[temp_artist_id]["bands"] = {}
            artist_data[temp_artist_id]["bands"][band_id] = {}
            artist_data[temp_artist_id]["bands"][band_id]["pseudonym"] = temp_artist_name
            # Last replace is not a normal white space (\xa0).
            temp_instruments = actual_row.contents[3].contents[0].rstrip().lstrip().replace('\t', '').replace(' ', '')
            instruments = cut_instruments(temp_instruments)
            artist_data[temp_artist_id]["bands"][band_id][header_category] = instruments

    # pp = pprint.PrettyPrinter(indent=2)
    # # pp.pprint(band_data)
    # # pp.pprint(artist_data)
    # # pp.pprint(label_data)
    logger.debug('<<< Crawling [' + band_short_link + ']')
    return [band_data, artist_data, label_data]


def crawl_bands(file_with_band_links, database, lock):
    logger = logging.getLogger('Crawler')
    logger.debug('>>> Crawling all bands in [{}]'.format(file_with_band_links))
    is_file_available = os.path.isfile(file_with_band_links)

    if is_file_available:
        logger.info("  {} is available. Starting to crawl all available bands. This may take a very long time.".format(
            file_with_band_links))
    else:
        logger.error("  {} is not available. Run with -c first or add links by hand".format(file_with_band_links))
        logger.error("  (one band per line in this format: The_Gathering/797).")
        return -1

    local_bands_queue = queue.Queue()

    with open(file_with_band_links, "r") as bandsFile:
        for line in bandsFile:
            local_bands_queue.put_nowait(line.rstrip('\r\n'))

    threads = []

    # Create threads and let them run.
    for i in range(0, threadCount):
        thread = VisitBandThread(str(i), local_bands_queue, database, lock)
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    logger.debug('<<< Crawling all bands in [{}]'.format(file_with_band_links))


def crawlBandsOld():
    bandsToVisit = set()
    # bandsToVisit.add('http://www.metal-archives.com/bands/Bathory')
    bandsToVisit.add('https://www.metal-archives.com/bands/Obituary/165')
    # bandsToVisit.add('https://www.metal-archives.com/bands/Metallica')
    # bandsToVisit.add('http://www.metal-archives.com/bands/Haystack/116128')
    # bandsToVisit.add('http://www.metal-archives.com/bands/Entombed/7')
    bandsToVisitInNextRound = set()
    bandsVisited = set()
    searchDepth = 1
    searchLevel = 0
    graphBandToBands = dict()

    while searchLevel < searchDepth:
        # Initialize the pool manager with certificates.  There will be nasty warnings for every call if you don't.
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

        # Pop a band from the "to visit" collection and add to visited collection.
        bandCurrentlyVisiting = bandsToVisit.pop()
        bandsVisited.add(bandCurrentlyVisiting)

        website = http.request('GET', bandCurrentlyVisiting)
        soup = BeautifulSoup(website.data, "html.parser")

        # Finds band name; needs to extract link.
        s = soup.find_all(attrs={"class": "band_name"})
        actualBandName = s[0].next_element.next_element  # .encode('utf-8')
        print('Visiting [' + actualBandName + ']...')

        # Takes all bands which belong to a person.
        bandLinks = soup.find_all(attrs={"class": "lineupBandsRow"})

        print("  Found [" + str(len(bandLinks) // 2) + "] persons with connected bands in lineup.")
        graphBandNames = set()
        # print(bandLinks)

        lineup = soup.find_all(attrs={"id": "band_tab_members_all"})
        lineup2 = soup.find(attrs={"id": "band_tab_members_all"})

        #    displayChildren(lineup)

        for bandLink in bandLinks:
            link = bandLink.a

            # print(bandLink.text.strip())

            if link is None:
                # TODO: Find solution for multiple bands with no link.
                graphBandNames.add(bandLink.text.split(':')[1].rstrip().lstrip().replace("ex-", ""))
                continue
            elif "ex-" in str(bandLink.a.previous_sibling):
                firstBandIsEx = True
            else:
                firstBandIsEx = False

            # Loop through all bands in person lineup.
            while link != None:
                if "," in link:  # Bands without DB entries have no links.
                    bandsLoop = link.split(",")
                    for s in bandsLoop:
                        # This can be anything (e.g.  "ex-" "(live)" or whitespaces).
                        # We want everything starting with "ex-" follwed by a band name.
                        # Or a band name followed by "(live)".
                        loopingBand = s.lstrip().rstrip()

                        # TODO: Make this better: Handle live better.
                        # This will return true for legitimate bands followed by "(live)".
                        if is_not_empty_string_or_live(loopingBand):
                            print(loopingBand)
                            if loopingBand != "ex-":  # Test for "-ex" here.  Handle flag later for different diagram.
                                loopingBand = loopingBand.replace("ex-", "")
                                loopingBand = loopingBand.replace("(live)", "")
                                graphBandNames.add(loopingBand)
                else:  # This is the actual link and text.
                    if str(link).rstrip() != "" and "live" not in link:
                        refLink = link.get('href')
                        bandsToVisitInNextRound.add(refLink)
                        graphBandNames.add(link.next_element)
                        # print " Found: [" + link.next_element + "] and added [" + link.get('href') + "] to list."

                link = link.next_sibling

        if not bandsToVisit:
            bandsToVisit = bandsToVisitInNextRound
            bandsToVisitInNextRound = set()
            searchLevel += 1

        print("  Found [" + str(len(graphBandNames)) + "] connected bands.")
        graphBandToBands.update({actualBandName: graphBandNames})

    #    for e in graphBandNames:
    #        print e

    bandGraph = prepareGraph(graphBandToBands)
    writeGraphAndCallGraphviz(bandGraph)
    print('Visited [' + str(len(bandsVisited)) + '] bands.')
