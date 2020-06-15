"""Defines classes and functions to crawl M-A for band and artist pages."""

import os
import json
import threading
import time
import queue
import logging
import re
from datetime import date, datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict

import certifi
import urllib3
from urllib3.exceptions import ReadTimeoutError, MaxRetryError
import progressbar
from settings import CRAWLER_THREAD_COUNT
from bs4 import BeautifulSoup, NavigableString, Tag

from country_helper import COUNTRY_NAMES
from genre import split_genres
from global_helpers import get_dict_key
from graph.choices import *

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2020, Martin Woelke'

em_link_main = 'https://www.metal-archives.com/'
em_link_label = em_link_main + 'labels/'
bands = 'bands/'
ajaxLinks = queue.Queue()
entity_paths = {'bands': 'databases/visited_bands.txt', 'members': 'databases/visited_members.txt'}
lineup_mapping = {"Current lineup": "Current", "Last known lineup": "Last known", "Past members": "past"}
STATUS_ERROR = 'unrecoverable'
STATUS_SKIPPED = 'skipped'
STATUS_ADDED = 'added'
stop_crawl_user_input = ""


@dataclass
class DbEntity:
    emid: int = -1
    link: str = 'not set'
    name: str = 'not set'
    type: str = 'not set'


@dataclass
class Band(DbEntity):
    lineup: Dict = field(default_factory=dict)
    genres: List[str] = field(default_factory=list)
    theme: List[str] = field(default_factory=list)
    active: List[str] = field(default_factory=list)
    artists: List[str] = field(default_factory=list)
    label: Label = Label()
    visited: str = 'not set'
    country: str = 'not set'
    location: str = 'not set'
    status: str = 'not set'
    formed: str = 'not set'

    def __init__(self):
        self.genres = []
        self.theme = []
        self.artists = []
        self.active = []
        self.lineup = {}
        self.type = 'band'


class VisitBandThread(threading.Thread):
    def __init__(self, thread_id, band_links, lock, db_handle, band_errors, visited_entities, progress_bar,
                 visited_bands, is_detailed=False, is_single_mode=True):
        """Constructs an worker object which is used to get prepared data from a band page.
        The only remarkable thing is switching the ``chardet.charsetprober`` logger to INFO.

        :param thread_id: An integer number
        :param band_links: A queue with short addresses of bands which are consumed one at a time by the workers.
        :param lock: Secures concurrent access to ``database`` which is used by all other workers.
        :param db_handle: The database handle is used to add all entities directly into the database with the strategy
            defined on the outside.
        :param band_errors: A shared dictionary with band links as keys and the number of unsuccessful crawl attempts as
            the value.
        :param visited_entities: A dictionary with keys like 'bands' or 'artists' to quickly check if crawling is
            needed. The value is the date the entry was written into the database. The dictionary must be filled on the
            outside or everything will be crawled and applied to the database.
        :param progress_bar: The progress bar is initialized on the outside with the size of the band_links as the
            maximum value.
        :param visited_bands: A list shared among the threads so that the progress bar is updated easily.
        :param is_detailed: A parameter that is not used and might be useful someday.
        :param is_single_mode: Indicates if a single band and its immediate connections is crawled.
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
        self.visited_entities = visited_entities
        self.visited_bands = visited_bands
        self.today = date.today()
        self.is_detailed = is_detailed
        self.is_single_mode = is_single_mode
        self.band_errors = band_errors
        self.retries_max = 3
        self.progress_bar = progress_bar
        global stop_crawl_user_input

    def update_bar(self, band_link):
        self.visited_bands.append(band_link)
        self.progress_bar.update(len(self.visited_bands))

    def run(self):
        """Runs crawling as long as band links are retrieved from the links queue.

        :return: -1 as soon as the queue runs out of links.
        """
        self.logger.debug("Running " + self.name)

        while stop_crawl_user_input is not "Q":
            try:
                link_band_temp = self.bandLinks.get_nowait()
            except queue.Empty:
                return -1

            # TODO: Implement revisiting mechanism based on date.
            # No need to visit if the band is already in the database.
            if link_band_temp in self.visited_entities['bands']:
                self.logger.debug(f"  Skipping {link_band_temp}.")
                self.update_bar(link_band_temp)
                self.band_errors[STATUS_SKIPPED][link_band_temp] = ""
                continue

            try:
                crawl_result = self.crawl_band(link_band_temp)
            except Exception:
                self.logger.exception("Something bad happened while crawling.")
                crawl_result = -1

            # Error case: putting the link back into circulation.
            if crawl_result == -1:
                if link_band_temp not in self.band_errors[STATUS_ERROR].keys():
                    self.band_errors[STATUS_ERROR][link_band_temp] = 1
                else:
                    self.band_errors[STATUS_ERROR][link_band_temp] += 1

                if self.band_errors[STATUS_ERROR][link_band_temp] < self.retries_max:
                    self.bandLinks.put(link_band_temp)
                else:
                    self.logger.error(f'Too many retries for {link_band_temp}.')
                    self.update_bar(link_band_temp)
                continue
            else:
                self.visited_entities['bands'][link_band_temp] = ''

            temp_band_data = crawl_result['bands']
            temp_artist_data = crawl_result['artists']
            temp_label_data = crawl_result['labels']
            self.lock.acquire()

            try:
                apply_to_db(crawl_result, self.db_handle, self.is_detailed)
                self.band_errors[STATUS_ADDED][link_band_temp] = ''
            except Exception:
                self.logger.exception("Writing artists failed! This is bad. Expect loss of data for:")
                self.logger.error(temp_band_data)
                self.logger.error(temp_artist_data)
                self.logger.error(temp_label_data)
                self.band_errors[STATUS_ERROR][link_band_temp] = ''
            finally:
                self.lock.release()
                self.update_bar(link_band_temp)

            # Saving the data to disk will later enable us to limit getting live data if it is not needed.
            for i_band in temp_band_data:
                band = temp_band_data[i_band]
                actual_band_path = f"databases/{band['country']}"
                os.makedirs(actual_band_path, exist_ok=True)
                # We take the band link because it always uses escaped sequences. This way we have the highest
                # compatibility for writing files in underlying filesystems. The slash must be replaced of course.
                db_path = Path(f"{actual_band_path}/{band['link'].replace('/', '_')}.json")
                actual_band_file = open(db_path, "w", encoding="utf-8")
                # TODO: Add try block for the dump. It crashed once because it found a Tag object.
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

        if len(band_short_link) is 0:
            return -1

        # TODO: Change your environment or this won't work!
        # The % escaped glyphs only work if the client.py in http
        # is changed in putrequest() before self._output() is called.
        # The line looks like this:
        # url = rfc3986.uri_reference(url).unsplit()
        # Needs to import rfc3986
        link_band = em_link_main + bands + band_short_link
        logger = logging.getLogger('Crawler')
        logger.info(f'>>> Crawling [{band_short_link}]')
        band_soup = cook_soup(link_band)

        if band_soup is None:
            return -1

        logger.debug("  Start scraping from actual band.")
        # Finds band name; needs to extract the ID later.
        s = band_soup.find_all(attrs={"class": "band_name"})

        if len(s) == 0:
            logger.fatal(f"  Did not find the attribute band_name for {band_short_link}.")
            logger.debug("  Band page source for reference:")
            logger.debug(band_soup.text)
            return -1

        # All data of a band is collected here.  Band members are referenced and collected in their own collection.
        band_data_ref = Band()
        band_data_ref.name = str(s[0].next_element.text)
        band_data_ref.emid = band_short_link[band_short_link.rfind('/') + 1:]
        band_data_ref.link = band_short_link

        band_data_ref.visited = str(self.today)

        band_data = {}
        band_id = band_short_link[band_short_link.rfind('/') + 1:]
        band_data[band_id] = {}
        band_data[band_id]["link"] = band_short_link
        band_data[band_id]["visited"] = str(self.today)
        band_data[band_id]["name"] = str(s[0].next_element.text)

        s = band_soup.find_all(attrs={"class": "float_left"})
        # Saving the country name and link in a dict.
        country_link = s[1].contents[3].contents[0].attrs["href"][-2:]
        # Take the last two letters of the link.
        band_data[band_id]["country"] = country_link
        location = s[1].contents[7].text

        if location == "N/A":
            location = ["N/A"]
        else:
            location = location.split("/")

        band_data_ref.country = s[1].contents[3].contents[0].attrs["href"][-2:]
        band_data_ref.location = location
        band_data_ref.status = get_dict_key(BAND_STATUS, s[1].contents[11].text)
        band_data_ref.formed = s[1].contents[15].text

        band_data[band_id]["location"] = location
        band_data[band_id]["status"] = get_dict_key(BAND_STATUS, s[1].contents[11].text)
        band_data[band_id]["formed"] = s[1].contents[15].text
        band_data[band_id]["active"] = []
        artist_data = {}
        s = band_soup.find_all(attrs={"class": "clear"})

        # Get years into a list. Earlier incarnations of a band are ignored.
        years_raw = s[3].contents[3].text.lstrip().rstrip()
        years_raw = years_raw.replace('\t', '')
        years_raw = years_raw.replace('\n', '')
        year_tokens = years_raw.split(',')

        for year_token in year_tokens:
            # First one filters the earlier incarnation. The second one is for a bit more obscure use case. In that an
            # earlier incarnation exists but has a comma in the name (leading for the latter portion to be split).
            if '(as' not in year_token and ')' not in year_token:
                band_data[band_id]["active"].append(year_token.lstrip())
                band_data_ref.active.append(year_token.lstrip())

        s = band_soup.find_all(attrs={"class": "float_right"})
        band_data[band_id]["genre"] = split_genres(s[3].contents[3].contents[0])
        band_data[band_id]["theme"] = s[3].contents[7].contents[0].split(', ')
        band_data_ref.genres = split_genres(s[3].contents[3].contents[0])
        band_data_ref.theme = s[3].contents[7].contents[0].split(', ')

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
            if len(label_node.contents) > 0:
                label_name = label_node.contents[0]
                label_link = label_node.attrs["href"][len(em_link_label):]
                label_id = label_link[label_link.find('/') + 1:]
            else:
                logger.error("Label node appears to empty; dumping parent parent node.")
                logger.error(str(s[3]))
                raise ValueError('Label node must not be empty.')

        band_data[band_id]["label"] = label_id
        label_data = {label_id: {"name": label_name, "link": label_link}}
        band_data_ref.label.name = label_name
        band_data_ref.label.link = label_link

        logger.debug("  Scraping artists from actual band.")
        artists_and_bands = band_soup.find_all(attrs={"class": "ui-tabs-panel-content"})
        artists_and_band_element = artists_and_bands[0]
        actual_category = artists_and_band_element.contents[1].contents
        band_data[band_id]["lineup"] = {}

        # This check sets a flag if a band e.g. only has a "last known" lineup. In that case it is not "diverse".
        lineup_finder = band_soup.find_all(attrs={"href": "#band_tab_members_all"})
        is_lineup_diverse = True

        if len(lineup_finder) == 0:
            is_lineup_diverse = False

        # The contents of actual_category starts with a LF (`Navigable String`) and has a LF at every even position.
        # So we start at index 1 with actual payload and only take data from uneven indexes.
        # Data at even indexes are from one of three categories:
        #   * lineupHeaders: A header category like "Current" or "Past".
        #   * lineupRow: An artist including instruments and time spans.
        #   * lineupBandsRow: Other bands an artist played in. We do not need to parse this as we connect each band
        #     member with the actual band.
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
                    test_header2 = str(band_soup.find_all(attrs={"href": "#band_tab_members_current"})[0].contents[0])
                    header_category = lineup_mapping[test_header2]
                    logger.debug(f"  Didn't find a header. Digging deeper: {header_category}")
            elif last_found_header == "lineupBandsRow":
                pass

            # Add an empty lineup list for the found header_category if it was not in before. `header_category` will
            # always have a valid value.
            band_data[band_id]["lineup"][header_category] = []
            band_data_ref.lineup[header_category] = []
            # TODO: Add line-up.
            # band_data_ref.lineup[header_category] = []

            # Five elements for artists.
            if len(actual_row) is 5:
                temp_artist_soup_link = actual_row.contents[1].contents[1].attrs["href"]

                # The leading part ist not needed and stripped (https://www.metal-archives.com/artists/).
                # It's always 39 letters long.
                temp_artist_link = actual_row.contents[1].contents[1].attrs["href"][39:]
                temp_artist_id = temp_artist_link[temp_artist_link.find('/') + 1:]
                temp_artist_pseudonym = str(actual_row.contents[1].contents[1].contents[0])
                logger.debug(f"    Recording artist data for {temp_artist_pseudonym}.")

                # Don't visit known band members.
                if temp_artist_link in self.visited_entities['artists']:
                    logger.debug(f"      Skipping band member {temp_artist_link}.")
                    artist_soup = None
                    artist_exists = True
                else:
                    artist_soup = cook_soup(temp_artist_soup_link)
                    artist_exists = False

                name = ""
                gender = "U"
                age = -1
                origin = 'ZZ'

                if artist_soup is not None:
                    member_info = artist_soup.find('div', attrs={'id': 'member_info'})
                    name = str(member_info.contents[7].contents[3].contents[0]).lstrip().rstrip()
                    gender = str(member_info.contents[9].contents[7].contents[0])

                    if gender not in GENDER.values():
                        gender = 'U'
                    else:
                        gender = get_dict_key(GENDER, gender)

                    temp_age = str(member_info.contents[7].contents[7].contents[0]).lstrip().rstrip()
                    # Age strings contain either an N/A or are YY (born ...).
                    if 'N/A' not in temp_age:
                        age = temp_age[:temp_age.find(" ")]

                    if 'N/A' not in member_info.contents[9].contents[3].text:
                        origin = member_info.contents[9].contents[3].contents[1].attrs['href'][-2:]
                else:
                    # Error case. artist_soup is invalid and the artist does not exist.
                    if not artist_exists:
                        return -1

                # If the band member does not have a name in the database we simply use the pseudonym. This
                # unfortunately overwrites the name with whatever pseudonym we found last.
                if 'N/A' in name:
                    name = temp_artist_pseudonym

                band_data[band_id]["lineup"][header_category].append(temp_artist_id)
                artist_data[temp_artist_id] = {}
                artist_data[temp_artist_id]["link"] = temp_artist_link
                artist_data[temp_artist_id]["exists"] = artist_exists
                artist_data[temp_artist_id]["visited"] = str(self.today)
                artist_data[temp_artist_id]["name"] = name
                artist_data[temp_artist_id]["gender"] = gender
                artist_data[temp_artist_id]["age"] = age
                artist_data[temp_artist_id]["origin"] = origin
                artist_data[temp_artist_id]["bands"] = {}
                artist_data[temp_artist_id]["bands"][band_id] = {}
                artist_data[temp_artist_id]["bands"][band_id]["pseudonym"] = temp_artist_pseudonym
                # Last replace is not a normal white space (\xa0).
                temp_instruments = actual_row.contents[3].contents[0].rstrip().lstrip().replace('\t', '').replace(' ',
                                                                                                                  '')
                instruments = cut_instruments(temp_instruments)
                artist_data[temp_artist_id]["bands"][band_id][header_category] = instruments

        # Happens only for the first band if -s was used as the command line switch.
        if self.is_single_mode:
            self.add_connected_bands_to_queue(band_soup)

        # Crawl discography.
        link_disco = f"https://www.metal-archives.com/band/discography/id/{band_id}/tab/all"
        disco_soup = cook_soup(link_disco)

        if disco_soup is None:
            logger.error(f"  Unable to get the discography for {band_short_link}.")
            # We have to throw everything away and start anew.
            return -1

        table = disco_soup.find('table', attrs={'class': 'display discog'})
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
            # We don't need the fixed part of the link (https://www.metal-archives.com/albums/).
            album_link = album_id[38:]
            # Get the ID just to be sure.
            album_id = album_id[album_id.rfind('/') + 1:]
            album_name = cells[0].text
            album_type = get_dict_key(RELEASE_TYPES, cells[1].text)
            album_year = cells[2].text
            album_rating_raw = cells[3].text.rstrip().strip()
            parenthesis_open = album_rating_raw.find('(')
            # Instantiate with data for invalid review and and ratings.
            album_rating = -1
            review_count = 0

            if parenthesis_open != -1:
                split_rating = album_rating_raw.split('(')

                # Get the average rating and review count from a string looking like this: '8 (64%)'
                if len(split_rating) is 2:
                    review_count = int(split_rating[0].rstrip())
                    album_rating = int(split_rating[1][:-2])

            band_data[band_id]['releases'].append({
                'emid': album_id,
                'name': album_name,
                'type': album_type,
                'release_date': album_year,
                'rating': album_rating,
                'review_count': review_count,
                'link': album_link
            })

        logger.debug(f'<<< Crawling [{band_short_link}]')
        return {'bands': band_data, 'artists': artist_data, 'labels': label_data}

    def add_connected_bands_to_queue(self, band_soup):
        """Extracts all band links from the given band soup and adds them to the queue, resets the single mode flag and
            updates the progressbar to the new band amount.

        :param band_soup: The band soup of the band that's crawled right now. A band soup is cooked with
            `cook_soup(link_band)` (which expects the _full_ address of a band page).
        """
        band_rows = band_soup.find_all('tr', attrs={'class': 'lineupBandsRow'})
        linked_bands = []

        for band_row in band_rows:
            actual_bands = band_row.contents[1].contents
            for i in range(1, len(actual_bands), 2):
                band_link = actual_bands[i].attrs['href'][37:]
                if band_link not in linked_bands:
                    linked_bands.append(band_link)
                    self.bandLinks.put(band_link)

        # Most of the time the crawler log is off, so this goes to the screen and the log file.
        if len(linked_bands) is 0:
            log_message = f'The chosen band does not have any outward connections.'
        else:
            log_message = f'Added {len(linked_bands)} connected bands to the crawl.'
        print(log_message)
        self.logger.info(log_message)
        # Switch off the single mode after the first call. At least for now. Maybe we'll do two levels (or more) later.
        self.is_single_mode = False
        # The additional band is the actual one because it is not in the queue right now.
        self.progress_bar.max_value = self.bandLinks.qsize() + 1


def make_band_list(country_links):
    logger = logging.getLogger('Crawler')
    logger.debug('Started Band List Visitor')
    skipped_links = 0
    band_links = []
    # Used as a very crude way to see if duplicate data is sent by MA.
    json_strings = []

    while country_links.qsize() != 0:
        link_country_temp = country_links.get_nowait()
        logger.debug(f'  Working on: {link_country_temp}')
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        country_json = http.request('GET', link_country_temp)
        json_data_string = country_json.data.decode('utf-8')

        if json_data_string not in json_strings:
            json_strings.append(json_data_string)
        else:
            logger.error(f'  Invalid data for [{link_country_temp}]. Putting it back in circulation...')
            country_links.put(link_country_temp)

        # The data string might contain an incomplete data definition which prevents conversion to the dict below.
        json_data_string = json_data_string.replace('"sEcho": ,', '')
        json_data = None

        try:
            json_data = json.loads(json_data_string)
        except Exception:
            logger.error(f'  JSON error for [{link_country_temp}]. Putting it back in circulation...')
            country_links.put(link_country_temp)

        if json_data is None:
            country_links.put(link_country_temp)
            continue

        for band in json_data["aaData"]:
            # We do not need the leading "'<a href=\'https://www.metal-archives.com/bands/".
            partial_link = band[0][46:band[0].rfind("'>")]

            if partial_link not in band_links:
                band_links.append(partial_link)
            else:
                logger.error(f'  Found a duplicate band link in MA [{partial_link}].')
                skipped_links += 1

        # Not waiting is much faster but generates more errors.
        time.sleep(1.0)

    return band_links


def apply_to_db(ma_dict, db_handle, is_detailed):
    logger = logging.getLogger('Crawler')
    temp_band_data = ma_dict['bands']
    temp_artist_data = ma_dict['artists']
    temp_label_data = ma_dict['labels']
    logger.debug("Apply to DB...")

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
                if 'present' in temp_slots[1] or '?' in temp_slots[1]:
                    time_slot_2 = date.today()
                else:
                    time_slot_2 = date(int(temp_slots[1]), 12, 31)

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
                          'visited': datetime.strptime(temp_band_data[band]['visited'], "%Y-%m-%d").date()
                          # 'active': active_list
                          }

        if temp_band_data[band]['formed'] != 'N/A':
            temp_band_dict['formed'] = date(int(temp_band_data[band]['formed']), 1, 1)

        logger.debug(f'  Writing data for band {temp_band_dict["link"]}.')
        db_handle.add_band(temp_band_dict)

        for release in temp_band_data[band]['releases']:
            # We need to copy the dict first because we need to make a date object for the release date.
            release_copy = dict(release)
            # This is not the accurate date, only the year.
            release_copy['release_date'] = date(int(release_copy['release_date']), 1, 1)
            logger.debug(f'  Writing data for release {release_copy["name"]}.')
            db_handle.add_release(release_copy)
            db_handle.band_recorded_release(band, release['emid'])

    for member in temp_artist_data:
        inner_data = temp_artist_data[member]

        if not inner_data['exists']:
            temp_member_dict = {'emid': member,
                                'name': inner_data['name'],
                                'link': inner_data['link'],
                                'age': int(inner_data['age']),
                                'gender': inner_data['gender'],
                                'origin': inner_data['origin'],
                                'visited': datetime.strptime(inner_data['visited'], "%Y-%m-%d").date()
                                }

            logger.debug(f"  Writing data for artist {temp_member_dict['link']}.")
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
        web_page = None

        try:
            web_page = http.request('GET', link, timeout=10.0)
        except ReadTimeoutError as e:
            logger.error(e)
            retry_count -= 1
        except MaxRetryError as e:
            logger.error(e)
            retry_count -= 1

        if web_page is not None:
            web_page_string = web_page.data.decode("utf-8")

            if "Forbidden.\n" == web_page_string:
                time.sleep(.5)
                retry_count -= 1
                logger.debug(f"  Trying again... ({retry_count} to go)")
            else:
                # Breaks out of the loop.
                retry_count = -1

    # Error case: No web page data after n retries.
    if retry_count is 0:
        return None

    return BeautifulSoup(web_page.data.decode('utf-8', 'ignore'), "html.parser")


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
                    # Then we have one of four types of strings. (1) two years separated by a '-' but the hyphen must be
                    #  in the middle (if it is not we have e.g. a 10-string bass: ARGH!) , (2) a single
                    # year, (3) a year followed by a '-' and 'present' or (4) at least one '?'. (5) The nastiest special
                    # case so far: inside the parenthesis is a string we cannot interpret (e.g. 'on EP 1').
                    for time_span in time_spans:
                        time_span = time_span.lstrip().rstrip()
                        # Safeguard against sloppy instruments where the time span starts with a comma.
                        if time_span == '':
                            continue
                        # There still is a trailing ')' in the end.
                        if time_span[len(time_span) - 1] == ')':
                            time_span = time_span[:-1]
                        # (2)
                        if len(time_span) is 4:
                            years = (int(time_span), int(time_span))
                        # (1)
                        elif len(time_span) is 9 and time_span[0] != '?' and time_span[4] == '-':
                            years = (int(time_span[0:4]), int(time_span[5:]))
                        # (4) Nasty special case.
                        elif '?' in time_span:
                            # '?-?' after removing a trailing ')'.
                            if time_span[0] == '?' and time_span[-1:] == '?':
                                years = ('?', '?')
                            elif time_span[0] == '?':
                                if re.search('[Pp]resent', time_span):
                                    years = ('?', 'present')
                                else:
                                    years = ('?', int(time_span[2:]))
                            elif time_span[-1:] == '?':
                                years = (int(time_span[0:4]), '?')
                            else:
                                years = ()
                        # (5)
                        elif not time_span.isdigit() and not re.search('[Pp]resent', time_span):
                            continue
                        # (3)
                        else:
                            years = (int(time_span[0:4]), 'present')

                        ready_spans.append(years)
                # Strings in brackets, part of the instrument we're looking for.
                else:
                    back_together += '(' + split_more[inner]
            collection.append((back_together.rstrip(), ready_spans))
    return collection


def crawl_country(country_short):
    """Crawls the given country page for band links and returns the list of short band links.

    Depending on the total amount of bands in the given country, the pages will be fetched through
    MA's AJAX API in packages of up til 500 bands.

    :param country_short: A country's ISO code to parse band links from.
    :return An unsorted list of short band links.
    """

    logger = logging.getLogger('Crawler')
    logger.debug(f">>> Crawling Country: {COUNTRY_NAMES[country_short]}")
    link_country = "https://www.metal-archives.com/browse/ajax-country/c/" + country_short
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
    logger.debug(f'  Country has [{amount_entries}] entries.')
    # Limit imposed by MA.
    display_constant = 500
    link_suffix = "/json/1?sEcho=1&iDisplayStart="

    band_links = None
    alt_link = "https://www.metal-archives.com/browse/ajax-country/c/{0}/json/1?sEcho={1:.0f}&iDisplayStart={2}"

    # I reworked this section multiple times but kept running into trouble infrequently. Running twice (and slowly)
    # seems to do the trick.
    for j in range(1):
        # Prepare the AJAX links for the actual run.
        for i in range(0, amount_entries, display_constant):
            ajaxLinks.put_nowait(alt_link.format(country_short, (i/500)+1, i))

        band_links = make_band_list(ajaxLinks)

        if amount_entries - len(band_links) is not 0:
            logger.error(f'  {amount_entries - len(band_links)} bands are missing.')

            if j is 0:
                logger.info('  Preparing a second run.')
            else:
                break

    if amount_entries - len(band_links) is not 0:
        logger.fatal('Despite trying twice, the band list is not complete. Run again in single run.')

    logger.debug("<<< Crawling Country")

    return band_links


def crawl_countries():
    """Crawls MA's country page for all available ISO country codes.

    :return: A list of two-letter ISO country codes.
    """

    country_links = []
    country_soup = cook_soup("https://www.metal-archives.com/browse/country", retry_count=10)

    if country_soup is not None:
        s = country_soup.find_all(attrs={"class": "countryCol"})

        for i in range(0, len(s)):
            for j in range(1, len(s[i].contents), 3):
                temp_link = s[i].contents[j].attrs["href"]
                country_short = temp_link[-2:]
                country_links.append(country_short)

    return country_links


def read_user_input():
    """Continuously reads the standard input until a Q is entered.

    """
    global stop_crawl_user_input

    while stop_crawl_user_input is not "Q":
        stop_crawl_user_input = input()

    print('Received request to quit. Stand by for threads to finish.')


def crawl_bands(band_links, db_handle, is_detailed=False, is_single_mode=False):
    # TODO: Add comment and parameter description.
    logger = logging.getLogger('Crawler')
    logger.debug('>>> Crawling all bands.')
    print("Starting band crawl. All logging is diverted to file. Prepping database:")
    local_bands_queue = queue.Queue()

    # Put links from list into queue.
    for link in band_links:
        local_bands_queue.put_nowait(link)

    # We do it once and give the collection to all threads. It was formerly done inside the thread initialization but it
    # took longer and longer the larger the database got.
    time_start = datetime.now()
    visited_entities = db_handle.get_all_links()
    time_delta = datetime.now() - time_start
    amount_bands = len(visited_entities["bands"])
    amount_artists = len(visited_entities["artists"])
    prep_report = f'Preparing previously visited {amount_bands} bands and {amount_artists} artists took {time_delta}.'
    logger.info(prep_report)
    print(prep_report)
    print(f'Crawling {local_bands_queue.qsize()} bands. This is going to take a while.')
    progress_bar = progressbar.ProgressBar(max_value=local_bands_queue.qsize())
    visited_bands = []

    threads = []
    lock = threading.Lock()
    thread_count = CRAWLER_THREAD_COUNT

    if len(band_links) < CRAWLER_THREAD_COUNT:
        thread_count = len(band_links)
    elif thread_count < 1 or thread_count > 8:
        logger.error("Thread count is outside safe range from 1 to 8. Overriding to 4.")
        thread_count = 4

    bands_status = {
        STATUS_ERROR: {},
        STATUS_SKIPPED: {},
        STATUS_ADDED: {}
    }

    print("Press Q and <ENTER> to stop crawl. All threads will finish their current work and then stop.")

    # Create threads.
    for i in range(0, thread_count):
        thread = VisitBandThread(
            str(i), local_bands_queue, lock, db_handle, bands_status, visited_entities, progress_bar,
            visited_bands, is_detailed, is_single_mode)
        threads.append(thread)

    # If we already start the threads in above loop, the queue count at initialization will not be the same for
    # all threads.
    for t in threads:
        t.start()

    user_input = threading.Thread(target=read_user_input)
    user_input.daemon = True
    user_input.start()

    for t in threads:
        t.join()

    user_input.join(1)

    progress_bar.finish()
    logger = logging.getLogger('Post-Crawler')

    # Print all bands which were not added to the database to the log and save the short links into a file.
    if len(bands_status[STATUS_ERROR]) > 0:
        logger.error('The following bands had too many problems and were not added to the database:')
        actual_time = datetime.now()
        time_stamp = f'{actual_time.date()}_{actual_time.time().strftime("%H%M%S")}'
        unrecoverable_file_name = Path(f'links/_bands_with_errors_{time_stamp}')
        unrecoverable_file = open(unrecoverable_file_name, "w", encoding="utf-8")

        for key, value in bands_status[STATUS_ERROR].items():
            logger.error(f'  {key}')
            unrecoverable_file.write(f'{key}\n')

        unrecoverable_file.close()
        logger.info(f'The short links of the bands are available in [{unrecoverable_file_name}].')

    if len(bands_status[STATUS_SKIPPED]) > 0:
        logger.info(f'{len(bands_status[STATUS_SKIPPED])} of {len(band_links)} bands were skipped.')

    if len(bands_status[STATUS_ADDED]) > 0:
        logger.info(f'{len(bands_status[STATUS_ADDED])} of {len(band_links)} bands were added.')

    logger.info('<<< Crawling all bands')
