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
import re
from graph.choices import *
from datetime import date
from pathlib import Path
from genre import split_genres

em_link_main = 'https://www.metal-archives.com/'
em_link_label = em_link_main + 'labels/'
bands = 'bands/'
bandsQueue = queue.Queue()
ajaxLinks = queue.Queue()
entity_paths = {'bands': 'databases/visited_bands.txt', 'members': 'databases/visited_members.txt'}
lineup_mapping = {"Current lineup": "Current", "Last known lineup": "Last known", "Past members": "past"}

# 8 might be a bit high (leaves some forbidden messages on getting the JSON
# data or the bands).
threadCount = 8


def get_dict_key(source_dict, value):
    return list(source_dict.keys())[list(source_dict.values()).index(value)]


class VisitBandThread(threading.Thread):
    def __init__(self, thread_id, band_links, lock, db_handle, is_detailed=False):
        """Constructs an worker object which is used to get prepared data from a band page.
        The only remarkable thing is switching the ``chardet.charsetprober`` logger to INFO.

        :param thread_id: An integer number
        :param band_links: A queue with short addresses of bands which are consumed one at a time by the workers.
        :param lock: Secures concurrent access to ``database`` which is used by all other workers.
        :param db_handle: The database handle is used to add all entities directly into the database with the strategy
            defined on the outside.
        """

        super(VisitBandThread, self).__init__()
        self.threadID = thread_id
        self.name = "BandVisitor_" + thread_id
        self.bandLinks = band_links
        self.logger = logging.getLogger('chardet.charsetprober')
        self.logger.setLevel(logging.INFO)
        self.logger = logging.getLogger('Crawler')
        self.qsize = band_links.qsize()
        self.logger.debug(f"Initializing {self.name}.")
        self.logger.debug(f"  Init with {self.qsize} bands.")
        self.lock = lock
        self.db_handle = db_handle
        self.visited_entities = self.db_handle.get_all_links()
        self.today = date.today()
        self.is_detailed = is_detailed

    def run(self):
        self.logger.debug("Running " + self.name)
        while self.bandLinks.qsize() != 0:
            link_band_temp = self.bandLinks.get_nowait()

            # TODO: Implement revisiting mechanism based on date.
            # No need to visit if the band is already in the database.
            if link_band_temp in self.visited_entities['bands']:
                self.logger.debug(f"  Skipping {link_band_temp}.")
                continue

            try:
                crawl_result = self.crawl_band(link_band_temp)
            except Exception:
                self.logger.exception("Something bad happened while crawling.")
                crawl_result = -1
            # Error case: putting the link back into circulation.
            if crawl_result == -1:
                self.bandLinks.put(link_band_temp)
                continue
            else:
                self.visited_entities['bands'][link_band_temp] = ""

            temp_band_data = crawl_result['bands']
            temp_artist_data = crawl_result['artists']
            temp_label_data = crawl_result['labels']
            self.lock.acquire()

            try:
                apply_to_db(crawl_result, self.db_handle, self.is_detailed)
            except Exception:
                self.logger.exception("Writing artists failed! This is bad. Expect loss of data for:")
                self.logger.error(temp_band_data)
                self.logger.error(temp_artist_data)
                self.logger.error(temp_label_data)
            finally:
                self.lock.release()
                # TODO: Refactor progress output.
                # progress = len(self.database["bands"]) / self.qsize
                # self.logger.info("Progress: {:.2f}%. {} of {} bands to go.".format(
                #     progress * 100, self.qsize - len(self.database["bands"]), self.qsize))

            # Saving the data to disk will later enable us to limit getting live data if it is not needed.
            for i_band in temp_band_data:
                band = temp_band_data[i_band]
                actual_band_path = f"databases/{band['country']}"
                os.makedirs(actual_band_path, exist_ok=True)
                # We take the band link because it always uses escaped sequences. This way we have the highest
                # compatibility for writing files in underlying filesystems. The slash must be replaced of course.
                db_path = Path(f"{actual_band_path}/{band['link'].replace('/', '_')}.json")
                actual_band_file = open(db_path, "w", encoding="utf-8")
                json_database_string = json.dumps(crawl_result)
                actual_band_file.write(json_database_string)
                actual_band_file.close()

    def crawl_band(self, band_short_link):
        """This is where the magic happens: A short band link is expanded, visited and parsed for data.

            It still may throw an exception that must be caught and dealt with. Best by putting the link back
            into circulation.

        :param band_short_link: Short form of the band link (e.g. Darkthrone/146).
        :return:
            A dictionary with band, artist and label data of the visited band or
            -1 in an error case.
        """

        # TODO: Change your environment or this won't work!
        # The % escaped glyphs only work if the client.py in http
        # is changed in putrequest() before self._output() is called.
        # The line looks like this:
        # url = rfc3986.uri_reference(url).unsplit()
        # Needs to import rfc3986
        link_band = em_link_main + bands + band_short_link
        logger = logging.getLogger('Crawler')
        logger.info(f'>>> Crawling [{band_short_link}]')
        soup = cook_soup(link_band)
        # TODO: Add evaluation of cooked soup.
        logger.debug("  Start scraping from actual band.")
        # Finds band name; needs to extract the ID later.
        s = soup.find_all(attrs={"class": "band_name"})

        if len(s) == 0:
            logger.fatal(f"  Did not find the attribute band_name for {band_short_link}.")
            logger.debug("  Band page source for reference:")
            logger.debug(soup.text)
            return -1

        # All data of a band is collected here.  Band members are referenced and collected in their own collection.
        band_data = {}
        band_id = band_short_link[band_short_link.rfind('/') + 1:]
        band_data[band_id] = {}
        band_data[band_id]["link"] = band_short_link
        band_data[band_id]["visited"] = str(self.today)
        band_data[band_id]["name"] = str(s[0].next_element.text)

        s = soup.find_all(attrs={"class": "float_left"})
        band_data[band_id]["country"] = s[1].contents[3].contents[0]
        country_node = s[1].contents[3].contents[0]
        # Saving the country name and link in a dict.
        country_link = country_node.attrs["href"]
        # Take the last two letters of the link.
        band_data[band_id]["country"] = country_link[-2:]
        location = s[1].contents[7].text

        if location != "N/A":
            location = location.split("/")

        band_data[band_id]["location"] = location
        band_data[band_id]["status"] = get_dict_key(BAND_STATUS, s[1].contents[11].text)
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
                    # TODO: Very strange case for bands which changed their name. Maybe we want to pass that time span.
                    if yearToken != ')':
                        band_data[band_id]["active"].append(yearToken)
            elif type(active) is Tag:
                previous_name = " " + active.contents[0]
                last_position = len(band_data[band_id]["active"]) - 1
                band_data[band_id]["active"][last_position] += previous_name + ")"
            else:
                logger.warning(f"  Found an element of type {type(active)}. This should not happen.")

        # This removes all earlier (or later) incarnations of the band. It would be better to change the above block
        # but I'm too lazy to do it right now.
        for time_span in band_data[band_id]["active"]:
            if time_span.find('(as') > 0:
                band_data[band_id]["active"].remove(time_span)

        s = soup.find_all(attrs={"class": "float_right"})
        band_data[band_id]["genre"] = split_genres(s[3].contents[3].contents[0])
        band_data[band_id]["theme"] = s[3].contents[7].contents[0].split(', ')
        label_node = s[3].contents[11].contents[0]

        # The label from band page is only the active one. All others will only be available through the individual
        # releases. TODO: Visit all releases and get more detailed info.
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

        logger.debug("  Scraping artists from actual band.")
        artists_and_bands = soup.find_all(attrs={"class": "ui-tabs-panel-content"})
        artists_and_band_element = artists_and_bands[0]
        actual_category = artists_and_band_element.contents[1].contents
        band_data[band_id]["lineup"] = {}

        # This check sets a flag if a band e.g. only has a "last known" lineup. In that case it is not "diverse".
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
                logger.debug(f"  Found header: {header_category}")
            # Special case where a band only has one line-up.
            elif last_found_header == "lineupRow":
                # If a band has only one lineup (current, last-known or past) the usual headers will be missing on the
                # page. For active bands with changing lineup we get 'Current'. For a band with no lineup changes it
                # will be empty.
                if not is_lineup_diverse:
                    test_header2 = str(soup.find_all(attrs={"href": "#band_tab_members_current"})[0].contents[0])
                    header_category = lineup_mapping[test_header2]
                    logger.debug(f"  Didn't find a header. Digging deeper: {header_category}")

            if header_category not in band_data[band_id]["lineup"]:
                band_data[band_id]["lineup"][header_category] = []

            # Five elements for artists.
            if len(actual_row) is 5:
                temp_artist_soup_link = actual_row.contents[1].contents[1].attrs["href"]

                # The leading part ist not needed and stripped (https://www.metal-archives.com/artists/).
                # It's always 39 letters long.
                temp_artist_link = actual_row.contents[1].contents[1].attrs["href"][39:]
                temp_artist_id = temp_artist_link[temp_artist_link.find('/') + 1:]
                temp_artist_name = str(actual_row.contents[1].contents[1].contents[0])
                logger.debug(f"    Recording artist data for {temp_artist_name}.")

                if temp_artist_link in self.visited_entities['artists']:
                    logger.debug(f"      Skipping band member {temp_artist_link}.")
                    artist_soup = None
                    artist_exists = True
                else:
                    artist_soup = cook_soup(temp_artist_soup_link)
                    artist_exists = False

                name = ""
                gender = ""
                age = -1

                if artist_soup is not None:
                    member_info = artist_soup.find('div', attrs={'id': 'member_info'})
                    name = str(member_info.contents[7].contents[3].contents[0]).lstrip().rstrip()
                    gender = get_dict_key(GENDER, str(member_info.contents[9].contents[7].contents[0]))
                    temp_age = str(member_info.contents[7].contents[7].contents[0]).lstrip().rstrip()

                    # Age strings contain either an N/A or are YY (born ...).
                    if temp_age.find("N/A") < 0:
                        age = temp_age[:temp_age.find(" ")]
                else:
                    # Error case. This will break if a band member has no MA entry.
                    # return -1
                    pass

                # If the band member does not have a name in the database we simply use the pseudonym. This
                # unfortunately overwrites the name with whatever pseudonym we found last.
                if name.find("N/A") >= 0:
                    name = temp_artist_name

                band_data[band_id]["lineup"][header_category].append(temp_artist_id)
                artist_data[temp_artist_id] = {}
                artist_data[temp_artist_id]["link"] = temp_artist_link
                artist_data[temp_artist_id]["exists"] = artist_exists
                artist_data[temp_artist_id]["visited"] = str(self.today)
                artist_data[temp_artist_id]["name"] = name
                artist_data[temp_artist_id]["gender"] = gender
                artist_data[temp_artist_id]["age"] = age
                artist_data[temp_artist_id]["bands"] = {}
                artist_data[temp_artist_id]["bands"][band_id] = {}
                artist_data[temp_artist_id]["bands"][band_id]["pseudonym"] = temp_artist_name
                # Last replace is not a normal white space (\xa0).
                temp_instruments = actual_row.contents[3].contents[0].rstrip().lstrip().replace('\t', '').replace(' ',
                                                                                                                  '')
                instruments = cut_instruments(temp_instruments)
                artist_data[temp_artist_id]["bands"][band_id][header_category] = instruments

        # Crawl discography.
        link_disco = f"https://www.metal-archives.com/band/discography/id/{band_id}/tab/all"
        soup = cook_soup(link_disco)
        table = soup.find('table', attrs={'class': 'display discog'})
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        band_data[band_id]['releases'] = []

        for row in rows:
            cells = row.findAll("td")

            # Guard clause for the unlikely case if a band has no releases.
            if len(cells) is 1:
                logger.debug(f"  No releases found for {band_data[band_id]['name']}.")
                continue

            # TODO: Visit release page to get details like the actual release date instead of only the year.
            album_id = cells[0].contents[0].attrs['href']
            album_id = album_id[album_id.rfind('/') + 1:]
            album_name = cells[0].text
            album_type = get_dict_key(RELEASE_TYPES, cells[1].text)
            album_year = cells[2].text
            album_rating = cells[3].text.rstrip().strip()
            parenthesis_open = album_rating.find('(')

            if parenthesis_open != -1:
                parenthesis_close = album_rating.find(')')
                # Get int value from a string looking like this: '8 (64%)'
                album_rating = int(album_rating[parenthesis_open + 1:parenthesis_close - 1])
            else:
                album_rating = -1

            band_data[band_id]['releases'].append({
                'emid': album_id,
                'name': album_name,
                'type': album_type,
                'release_date': album_year,
                'rating': album_rating
            })

        # pp = pprint.PrettyPrinter(indent=2)
        # # pp.pprint(band_data)
        # # pp.pprint(artist_data)
        # # pp.pprint(label_data)
        logger.debug('<<< Crawling [' + band_short_link + ']')
        return {'bands': band_data, 'artists': artist_data, 'labels': label_data}


class VisitBandListThread(threading.Thread):

    def __init__(self, thread_id, country_links, band_links):
        super(VisitBandListThread, self).__init__()
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
            self.logger.debug(f"  Working on: {link_country_temp}")

            try:
                json_data = json.loads(json_data_string)
            except Exception:
                self.logger.error(f"  JSON error for [{link_country_temp}]. Putting it back in circulation...")
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

        self.logger.debug(f"Finished {self.name} and added {str(link_counter)} links.")


def apply_to_db(ma_dict, db_handle, is_detailed):
    temp_band_data = ma_dict['bands']
    temp_artist_data = ma_dict['artists']
    temp_label_data = ma_dict['labels']

    for band in temp_band_data:

        active_time = temp_band_data[band]['active']
        active_list = []

        for time_slot in active_time:
            if '?' in time_slot or 'N/A' in time_slot:
                continue

            temp_slots = time_slot.split('-')
            time_slot_1 = date(int(temp_slots[0]), 1, 1)

            if len(temp_slots) is 1:
                time_slot_2 = time_slot_1
            else:
                if 'present' in temp_slots[1]:
                    time_slot_2 = date.today()
                else:
                    time_slot_2 = date(int(temp_slots[1]), 1, 1)

            active_list.append(time_slot_1)
            active_list.append(time_slot_2)

        temp_band_dict = {'emid': band,
                          'name': temp_band_data[band]['name'],
                          'link': temp_band_data[band]['link'],
                          'country': temp_band_data[band]['country'],
                          'status': temp_band_data[band]['status'],
                          'themes': temp_band_data[band]['theme'],
                          'genres': temp_band_data[band]['genre'],
                          'locations': temp_band_data[band]['location'],
                          }

        if temp_band_data[band]['formed'] != 'N/A':
            temp_band_dict['formed'] = date(int(temp_band_data[band]['formed']), 1, 1)

        db_handle.add_band(temp_band_dict)

        for release in temp_band_data[band]['releases']:
            # We need to copy the dict first because we need to make a date object for the release date.
            release_copy = dict(release)
            # This is not the accurate date, only the year.
            release_copy['release_date'] = date(int(release_copy['release_date']), 1, 1)
            db_handle.add_release(release_copy)
            db_handle.band_recorded_release(band, release['emid'])

    for member in temp_artist_data:
        inner_data = temp_artist_data[member]

        if not inner_data['exists']:
            temp_member_dict = {'emid': member,
                                'name': inner_data['name'],
                                'link': inner_data['link'],
                                'age': int(inner_data['age']),
                                'gender': inner_data['gender']
                                }

            db_handle.add_member(temp_member_dict)

        for band_relation in inner_data['bands']:
            inner_relation = inner_data['bands'][band_relation]
            for status in MEMBER_STATUS.values():
                if status in inner_relation:
                    for instruments in inner_relation[status]:
                        time_spans = []
                        for time_span_tuple in instruments[1]:
                            if time_span_tuple[0] != '?':
                                d0 = date(time_span_tuple[0], 1, 1)
                            else:
                                continue
                            t1 = time_span_tuple[1]
                            if t1 == 'present':
                                d1 = date.today()
                            elif t1 == '?':
                                continue
                            else:
                                d1 = date(time_span_tuple[1], 12, 31)
                            time_spans.append(d0)
                            time_spans.append(d1)
                        try:
                            db_handle.member_played_in_band(member,
                                                            band_relation,
                                                            instruments[0],
                                                            inner_relation['pseudonym'],
                                                            time_spans,
                                                            get_dict_key(MEMBER_STATUS, status)
                                                            )
                        except Exception:
                            logging.getLogger('Crawler').exception("Making member connection failed.")
                            logging.getLogger('Crawler').error(member)
                            logging.getLogger('Crawler').error(band_relation)
                            logging.getLogger('Crawler').error(instruments[0])
                            logging.getLogger('Crawler').error(inner_relation['pseudonym'])
                            logging.getLogger('Crawler').error(time_spans)

    # Add labels if mode is detailed.
    if is_detailed:
        pass


def cook_soup(link, retry_count=5):
    """Wraps getting a web page for further parsing.

    Retries several times to get the page if the request yields in a *Forbidden*.

    :param link: URL to get the web page from.
    :param retry_count: Set to any number greater than 0 (will be set internally to 1 if smaller than 1).
    :return: Either a BeautifulSoup object of the requested page or ``None`` if the request failed.
    """
    logger = logging.getLogger('Crawler')
    # Set to 1 if value is invalid.
    if retry_count < 1:
        retry_count = 1

    logger.debug(f"  Cooking soup for {link}")

    while retry_count > 0:
        # Initialize the pool manager with certificates. There will be nasty warnings for every call if you don't.
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        web_page = http.request('GET', link)
        web_page_string = web_page.data.decode("utf-8")

        if "Forbidden." in web_page_string:
            logger.debug("  trying again...")
            time.sleep(.5)
            retry_count -= 1
        else:
            retry_count = -1

    if retry_count is 0:
        return None

    return BeautifulSoup(web_page.data, "html.parser")


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
    collection = []
    # First split along the '),'.
    temp_instruments = instrument_string.split('),')

    # Put the ')' back into every element but the last one. It's needed to preserve parts like "(earlier)".
    for index in range(0, len(temp_instruments) - 1):
        temp_instruments[index] += ')'

    for temp_instrument in temp_instruments:
        temp_instrument = temp_instrument.lstrip()
        # Test if there are any numerals in instrument_string.
        if not bool(re.search(r'\d', temp_instrument)):
            collection.append((temp_instrument, []))
        # We have at least one year.
        else:
            split_more = temp_instrument.split('(')
            back_together = split_more[0]
            ready_spans = []
            for inner in range(1, len(split_more)):
                if bool(re.search(r'\d', split_more[inner])):
                    # First split by commas.
                    time_spans = split_more[inner].split(',')
                    # Then we have one of four types of strings. (1) two years separated by a '-', (2) a single
                    # year, (3) a year followed by a '-' and 'present' or (4) at least one '?'.
                    for time_span in time_spans:
                        time_span = time_span.lstrip().rstrip()
                        # There still is a trailing ')' in the end.
                        if time_span[len(time_span) - 1] == ')':
                            time_span = time_span[:-1]
                        # (2)
                        if len(time_span) is 4:
                            years = (int(time_span), int(time_span))
                        # (1)
                        elif len(time_span) is 9:
                            years = (int(time_span[0:4]), int(time_span[5:]))
                        # (4) Nasty special case.
                        elif '?' in time_span:
                            if time_span[0] == '?' and time_span[:-1] == '?':
                                years = ('?', '?')
                            elif time_span[0] == '?':
                                years = ('?', int(time_span[2:]))
                            elif time_span[-1:] == '?':
                                years = (int(time_span[0:4]), '?')
                            else:
                                years = ()
                        # (3)
                        else:
                            years = (int(time_span[0:4]), 'present')

                        ready_spans.append(years)
                # Strings in brackets, part of the instrument we're looking for.
                else:
                    back_together += '(' + split_more[inner]
            collection.append((back_together.rstrip(), ready_spans))
    return collection


def crawl_country(link_country):
    """Crawls the given country page for band links and puts them into the global variable bandsQueue.

    Depending on the total amount of bands in the given country, the pages will be fetched through
    MA's AJAX API in packages of up til 500 bands. Parsing happens in eight threads.

    TODO: Move global variable to smaller scope?

    :param link_country: Address of a country to parse band links from.
    """

    logger = logging.getLogger('Crawler')
    logger.debug(f">>> Crawling Country: {link_country}")
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

    logger.debug(f"  Setting up to do [{str(needed_run_count)}] runs with [{str(thread_count)}] threads.")
    link_suffix = "/json/1?sEcho=1&iDisplayStart="

    # Prepare the AJAX links for the actual run.
    for i in range(0, amount_entries, display_constant):
        ajaxLinks.put_nowait(link_country + link_suffix + str(i))
        logger.debug(f"    Prepping link: {str(i)}")

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
    """Crawls MA's country page for all available ISO country codes.

    :return: A list of two-letter ISO country codes.
    """

    soup = cook_soup("https://www.metal-archives.com/browse/country")
    s = soup.find_all(attrs={"class": "countryCol"})
    country_links = []

    for i in range(0, len(s)):
        for j in range(1, len(s[i].contents), 3):
            temp_link = s[i].contents[j].attrs["href"]
            country_short = temp_link[-2:]
            country_links.append(country_short)

    return country_links


def crawl_bands(band_links, db_handle, is_detailed=False):
    logger = logging.getLogger('Crawler')
    logger.debug('>>> Crawling all bands.')
    local_bands_queue = queue.Queue()

    # Put links from list into queue.
    for link in band_links:
        local_bands_queue.put_nowait(link)

    threads = []
    lock = threading.Lock()

    # Create threads.
    for i in range(0, threadCount):
        thread = VisitBandThread(
            str(i), local_bands_queue, lock, db_handle, is_detailed)
        threads.append(thread)

    # If we already start the threads in above loop, the queue count at initialization will not be the same for
    # all threads.
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(database)

    logger.debug('<<< Crawling all bands')
