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

linkMain = 'http://www.metal-archives.com/'
bands = 'bands/'
bandsQueue = queue.Queue()
ajaxLinks = queue.Queue()

# 8 might be a bit high (leaves some forbidden messages on getting the JSON
# data or the bands).
threadCount = 8


class VisitBandThread(threading.Thread):

    def __init__(self, threadID, bandLinks):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = "BandVisiter_" + threadID
        self.bandLinks = bandLinks
        self.logger = logging.getLogger('Crawler')
        self.logger.debug("Initing " + self.name)

    def run(self):
        self.logger.debug("Running " + self.name)
        while self.bandLinks.qsize() != 0:
            linkBandTemp = self.bandLinks.get_nowait()
            crawlBand(linkBandTemp)


class VisitBandListThread(threading.Thread):

    def __init__(self, threadID, countryLinks, bandLinks):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = "BandListVisiter_" + threadID
        self.countryLinks = countryLinks
        self.bandLinks = bandLinks
        self.logger = logging.getLogger('Crawler')
        self.logger.debug("Initing " + self.name)

    def run(self):
        self.logger.debug("Running " + self.name)
        linkCounter = 0

        while self.countryLinks.qsize() != 0:
            linkCountryTemp = self.countryLinks.get_nowait()
            http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
            countryJson = http.request('GET', linkCountryTemp)
            jsonDataString = countryJson.data.decode("utf-8")
            jsonDataString = jsonDataString.replace("\"sEcho\": ,", '')
            jsonData = None
            self.logger.debug("  Working on:" + linkCountryTemp)

            try:
                jsonData = json.loads(jsonDataString)
            except:
                self.logger.error("  JSON error for [" + linkCountryTemp + "]. Putting it back in circulation...")
                self.countryLinks.put(linkCountryTemp)

            if jsonData is not None:
                for band in jsonData["aaData"]:
                    indexFirstApostrophe = band[0].find("'")
                    indexSecondApostrophe = band[0].find("'", indexFirstApostrophe + 1)
                    bandLink = band[0][indexFirstApostrophe + 1:indexSecondApostrophe]
                    indexFirstClosingBracket = band[0].find(">")
                    indexSecondOpeningBracket = band[0].find("<", indexFirstClosingBracket)
                    bandName = band[0][indexFirstClosingBracket + 1:indexSecondOpeningBracket]
                    self.logger.debug("    {}: {}".format(bandName, bandLink))
                    # We do not need the leading "https://www.metal-archives.com/bands/".
                    self.bandLinks.put(bandLink[37:len(bandLink)])
                    linkCounter += 1

        self.logger.debug("Finished {} and added {} links.".format(self.name, str(linkCounter)))


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
    temp_instruments = instrument_string.split(',')
    instruments = ''
    has_found_multi_year = False
    time_spans = []
    collection = {}

    for element in temp_instruments:
        if '(' not in element and not has_found_multi_year:
            instruments += element + ','
        elif has_found_multi_year:
            has_closing_parenthesis = element.find(')')
            if has_closing_parenthesis is -1:
                time_spans.append(element.lstrip().rstrip())
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


def visit_band_list(countryLink, startIndex, bandLinks):
    logger = logging.getLogger('Crawler')
    linkCountryTemp = countryLink + str(startIndex)
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    countryJson = http.request('GET', linkCountryTemp)
    jsonDataString = countryJson.data.decode("utf-8")
    jsonDataString = jsonDataString.replace("\"sEcho\": ,", '')
    jsonData = json.loads(jsonDataString)

    for band in jsonData["aaData"]:
        indexFirstApostrophe = band[0].find("'")
        indexSecondApostrophe = band[0].find("'", indexFirstApostrophe + 1)
        bandLink = band[0][indexFirstApostrophe + 1:indexSecondApostrophe]
        logger.debug("  link: " + bandLink)
        indexFirstClosingBracket = band[0].find(">")
        indexSecondOpeningBracket = band[0].find("<", indexFirstClosingBracket)
        bandName = band[0][indexFirstClosingBracket + 1:indexSecondOpeningBracket]
        logger.debug("  name: " + bandName)
        bandLinks[bandName] = bandLink


def crawlCountry(linkCountry):
    logger = logging.getLogger('Crawler')
    logger.debug(">>> Crawling Country: " + linkCountry)
    jsonDataString = ""
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    while True:
        countryJson = http.request('GET', linkCountry)
        jsonDataString = countryJson.data.decode("utf-8")

        if "Forbidden." not in jsonDataString:
            break
        else:
            logger.debug("  trying again...")
            time.sleep(.5)

    jsonDataString = jsonDataString.replace("\"sEcho\": ,", '')
    jsonData = json.loads(jsonDataString)

    # The total amount of entries for this country is the only data we need for now.
    amountEntries = jsonData["iTotalRecords"]
    logger.debug("  Country has [{}] entries.".format(amountEntries))
    # Limit imposed by MA.
    displayConstant = 500
    # Amount of runs needed.
    neededRunCount = (amountEntries // displayConstant)

    # We need at least one and always one more (because of the division rounding down).
    if amountEntries % displayConstant > 0:
        neededRunCount += 1

    threadCount = 8

    # Override number of threads in case we don't need all.
    if neededRunCount < threadCount:
        threadCount = neededRunCount

    logger.debug("  Setting up to do [{}] runs with [{}] threads.".format(str(neededRunCount), str(threadCount)))
    linkSuffix = "json/1?sEcho=1&iDisplayStart="

    # Prepare the AJAX links for the actual run.
    for i in range(0, amountEntries, displayConstant):
        ajaxLinks.put_nowait(linkCountry + linkSuffix + str(i))
        logger.debug("    Prepping link: " + str(i))

    threads = []

    # Create threads and let them run.
    for i in range(0, threadCount):
        thread = VisitBandListThread(str(i), ajaxLinks, bandsQueue)
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    logger.debug("<<< Crawling Country")


def crawlCountries():
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    countriesPage = http.request('GET', "https://www.metal-archives.com/browse/country")
    soup = BeautifulSoup(countriesPage.data, "html.parser")
    s = soup.find_all(attrs={"class": "countryCol"})
    countryLinks = []

    for i in range(0, len(s)):
        for j in range(1, len(s[i].contents), 3):
            tempLink = s[i].contents[j].attrs["href"]
            countryShort = tempLink[len(tempLink) - 2:len(tempLink)]
            countryLinks.append("https://www.metal-archives.com/browse/ajax-country/c/" + countryShort)

    return countryLinks


def crawlBand(bandShortLink):
    # TODO: The % escaped glyphs only work if the client.py in http
    # is changed in putrequest() before self._output() is called.
    # The line looks like this:
    # url = rfc3986.uri_reference(url).unsplit()
    # Needs to import rfc3986
    linkBand = linkMain + bands + bandShortLink
    logger = logging.getLogger('Crawler')
    logger.debug('>>> Crawling [' + bandShortLink + ']')

    # Initialize the pool manager with certificates.  There will be nasty warnings for every call if you don't.
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    bandPage = http.request('GET', linkBand)
    soup = BeautifulSoup(bandPage.data, "html.parser")
    # soup = BeautifulSoup(bandPage.data, "lxml")

    # Finds band name; needs to extract the ID later.
    s = soup.find_all(attrs={"class": "band_name"})

    if len(s) == 0:
        return -1

    # All data of a band is collected here.  Band members are referenced and collected in their own collection.
    bandData = {}
    bandID = bandShortLink[bandShortLink.rfind('/') + 1:]
    bandData[bandID] = {}
    bandData[bandID]["link"] = bandShortLink
    bandData[bandID]["name"] = s[0].next_element.next_element

    s = soup.find_all(attrs={"class": "float_left"})
    bandData[bandID]["country"] = s[1].contents[3].contents[0]
    countryNode = s[1].contents[3].contents[0]
    countryName = countryNode.contents[0]
    # Saving the country name and link in a dict.
    countryLink = countryNode.attrs["href"]
    bandData[bandID]["country"] = {countryName: countryLink}
    bandData[bandID]["location"] = s[1].contents[7].contents[0].split("/")
    bandData[bandID]["status"] = s[1].contents[11].contents[0]
    bandData[bandID]["formed"] = s[1].contents[15].contents[0]
    bandData[bandID]["active"] = []
    artistData = {}

    s = soup.find_all(attrs={"class": "clear"})
    active = ""

    # Iterate over all time spans the band was (or is) active.
    for element in s[3].contents[3].contents:
        active = element
        if type(active) is NavigableString:
            active = active.replace('\t', '')
            active = active.replace('),', '')
            active = active.replace('\n', '')
            active = active.replace(' ', '')
            yearTokens = active.split(',')
            for yearToken in yearTokens:
                bandData[bandID]["active"].append(yearToken)
        elif type(active) is Tag:
            previousName = " " + active.contents[0]
            lastPosition = len(bandData[bandID]["active"]) - 1
            bandData[bandID]["active"][lastPosition] += previousName + ")"
        else:
            logger.warning("  Found an element of type {}. This should not happen.".format(type(active)))

    s = soup.find_all(attrs={"class": "float_right"})
    genres = s[3].contents[3].contents[0]
    genres = genres.split(',')
    bandData[bandID]["genre"] = genres
    bandData[bandID]["theme"] = s[3].contents[7].contents[0].split(',')
    labelNode = s[3].contents[11].contents[0]

    if type(labelNode) is NavigableString:
        bandData[bandID]["label"] = {s[3].contents[11].contents[0]: ""}
    else:
        labelName = labelNode.contents[0]
        labelLink = labelNode.attrs["href"]
        bandData[bandID]["label"] = {labelName: labelLink}

    artistsAndBands = soup.find_all(attrs={"class": "ui-tabs-panel-content"})
    artistsAndBandElement = artistsAndBands[0]
    logger.debug("  Scraping artists from actual band.")
    actualCategory = artistsAndBandElement.contents[1].contents
    bandData[bandID]["lineup"] = {}

    # The elements alternate from a band member to bands or member to
    # member if it's the only band for the latter.
    # Category (like current or past) are found at index.
    for i in range(1, len(actualCategory), 2):
        actualRow = actualCategory[i]
        lastFoundHeader = actualRow.attrs["class"][0]
        if lastFoundHeader == "lineupHeaders":
            headerCategory = actualRow.contents[1].contents[0].rstrip().lstrip().replace('\t', '')
            logger.debug("    Found header: {}".format(headerCategory))
            bandData[bandID]["lineup"][headerCategory] = []

        # Five elements for artists.
        if len(actualRow) is 5:
            # The leading part ist not needed and stripped
            # (https://www.metal-archives.com/artists/).  It's always 39
            # letters long.
            tempArtistLink = actualRow.contents[1].contents[1].attrs["href"][39:]
            temp_artist_id = tempArtistLink[tempArtistLink.find('/') + 1:]
            tempArtistName = str(actualRow.contents[1].contents[1].contents[0])
            bandData[bandID]["lineup"][headerCategory].append(temp_artist_id)
            tempInstruments = actualRow.contents[3].contents[0].rstrip().lstrip().replace('\t', '').replace(' ', '')
            instruments = cut_instruments(tempInstruments)

            artistData[temp_artist_id] = {}
            artistData[temp_artist_id]["link"] = tempArtistLink
            artistData[temp_artist_id]["name"] = tempArtistName
            artistData[temp_artist_id]["bands"] = {}
            artistData[temp_artist_id]["bands"][bandID] = instruments

            # bandData["lineup"][headerCategory][tempArtistLink].append(tempInstrumentCollection)
    #            logger.debug("      {:30} | {:30} | {}".format(tempArtistLink, tempArtistName, tempInstruments))
    #    pp = pprint.PrettyPrinter(indent=4)
    #    pp.pprint(bandData)
    # logger.debug(bandData)
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(artistData)
    logger.debug('<<< Crawling [' + bandShortLink + ']')


def crawlBands(fileWithBandLinks):
    logger = logging.getLogger('Crawler')
    logger.debug('>>> Crawling all bands in [{}]'.format(fileWithBandLinks))
    isFileAvailable = os.path.isfile(fileWithBandLinks)

    if isFileAvailable:
        logger.info("  {} is available. Starting to crawl all available bands. This may take a very long time.".format(
            fileWithBandLinks))
    else:
        logger.error("  {} is not available. Run with -c first.".format(fileWithBandLinks))
        return -1

    localBandsQueue = queue.Queue()

    with open(fileWithBandLinks, "r") as bandsFile:
        for line in bandsFile:
            localBandsQueue.put_nowait(line.rstrip('\r\n'))

    threads = []

    # Create threads and let them run.
    for i in range(0, threadCount):
        thread = VisitBandThread(str(i), localBandsQueue)
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    logger.debug('<<< Crawling all bands in [{}]'.format(fileWithBandLinks))


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
