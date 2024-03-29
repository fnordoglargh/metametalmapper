"""Classes to export/save reports from a given data. Each ``GraphDatabaseStrategy`` implementation has to use
these classes to successfully export data."""

from collections import defaultdict, OrderedDict
import json
from enum import Enum
from pathlib import Path
import logging

from genre import GENRE_CORE_MA
from global_helpers import get_export_path, get_time_stamp, FOLDER_LINKS, LINK_EXTENSION, FOLDER_LINKS_INVALID,\
    FOLDER_LINKS_MISSING
from country_helper import COUNTRY_NAMES
from graph.choices import GENDER, RELEASE_TYPES
from settings import RELEASE_AVERAGE_MIN, RELEASE_REVIEW_COUNT_MIN, TOP

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2023, Martin Woelke'

POP_PER_100K = 'Bands per 100k people'
POP_POPULATION = 'Population'
GENDER_DISTRIBUTION = 'Gender distribution ({} artists from {} countries)\n'


def check_bands_in_country(country_short, band_links_actual, base_folder=FOLDER_LINKS):
    """Checks if the actual bands list matches the expected bands which are read from a country file.
    A set of results contains both bands that are missing from the database (not crawled yet) and
    the bands which were deleted from M-A since the last crawl.
    The assumption is that the country link file is _always_ the sole source of truth.

    :param country_short: The ISO country code of the country link file to be read for the check.
        Any file name ending in `.lnks` can be used.
    :param band_links_actual: A list of short band links from the running database.
    :param base_folder: The folder relative to the execution path from where to load the
    :return: A set of two lists and a string; the first list contains the bands that are missing
        in the database, the second holds the bands that are in the database but not on M-A. The string
        is either a valid country name or 'Not a country: "country_short"'.
        None if the file does not exist.
    """
    if country_short in COUNTRY_NAMES.keys():
        country_name = COUNTRY_NAMES[country_short]
    else:
        country_name = f'Not a country: "{country_short}"'

    country_file = Path(f'{base_folder}/{country_short}{LINK_EXTENSION}')

    if not country_file.is_file():
        return None

    expected_bands = country_file.read_text(encoding='utf-8').split('\n')

    # Remove all empty lines.
    for i in range(0, expected_bands.count(''), 1):
        expected_bands.remove('')

    bands_missing = list(set(expected_bands) - set(band_links_actual))
    bands_not_expected = list(set(band_links_actual) - set(expected_bands))

    # The collections need to be sorted for the unit tests.
    bands_missing.sort()
    bands_not_expected.sort()

    return bands_missing, bands_not_expected, country_name


class ReportMode(Enum):
    CountryOff = 0
    CountryOn = 1


class CountryReport:
    """A CountryReport stores information for a country which can be printed on a CLI or exported to a CSV file. A
        constructor allows creation. Everything else but a function to get the amount of people of a certain gender is
        internal.

        We store e.g. the amount of bands and artists and the number of countries they are from plus a gender breakdown
        of all artists. Artists are not filtered through their origin. Any artists linked to a band will be counted.

        A word on genres: A band which plays 'Atmospheric Black Metal' has the genre string dissected into both
        'Atmospheric Black' and 'Black'. This is especially important for counting against the core genres of MA. See
        genre.py for details.
    """
    TXT_MISSING = 'Missing bands; not in database but in country link file'
    TXT_INVALID = 'Invalid bands; in database but not in country link file'

    def __init__(self, country_short, population, sanity_bands, genders, gender_per_country, genres, bands_per_year):
        self._country_short = country_short
        self._country_name = COUNTRY_NAMES[country_short]
        self._population = int(population)
        self._number_bands = len(sanity_bands)
        self._checked_bands = check_bands_in_country(country_short, sanity_bands)

        # Tuple with formatted printable text and a line terminated string.
        self._report_missing = self._make_sanity_report(0, self.TXT_MISSING)
        self._report_invalid = self._make_sanity_report(1, self.TXT_INVALID)

        # Special case handling for countries like "International" (XX) which have -1 as population.
        if self._population <= 1:
            self._bands_per_100k = 'NA'
            self._population = 'NA'
        else:
            self._bands_per_100k = self._number_bands / (int(population) / 100000)

        self._genders = {}
        self._amount_people = 0
        self._set_genders(genders)
        # A dictionary with a ISO country name as key and the amount of people from that country as value.
        self._gender_per_country = gender_per_country
        self._genres = []
        self._set_genres(genres)
        self.bands_per_year = bands_per_year

    def _set_genres(self, genres: list):
        """Internal function used by the constructor to set genres and calculate their percentages in relation to the
            number of bands in the given country.

        :param genres: List of tuples with a genre and the number of bands which play it.
        """

        for genre in genres:
            self._genres.append((genre[0], genre[1], (genre[1] / self._number_bands) * 100))

    def _set_genders(self, genders: dict):
        """Internal function used by the constructor to set the genders.

        :param genders: A dictionary with genders and the number of people of that gender for bands of the given
            country.
        """
        self._amount_people = 0
        for gender in genders.keys():
            self._amount_people += genders[gender]

        if self._amount_people == 0:
            return None

        for gender in GENDER:
            self._genders[gender] = ()

        for gender, count in genders.items():
            # Fill with value pairs count and the percentage_bands.
            self._genders[gender] = (count, (count / self._amount_people) * 100)

    def get_gender(self, gender_key):
        """Gets the countries gender tuple for the given gender key.

        :param gender_key: The gender key. See GENDER for possible values.
        :return: A tuple with three values; The gender string, number of people in the given country belonging to that
            gender and a percentage_bands in relation to the total number of people playing in bands of this country.
        """
        return self._genders[gender_key][0]

    def get_genres(self):
        return self._genres

    def _get_population(self):
        """Returns a string for the str() method which handles the formatting of valid populations (inserts comma for
            thousands-separator) and simply prints the 'NA' of invalid values.

        :return: A perfectly formatted population string used internally by the str() method.
        """
        if str(self._population).isdigit():
            return f'    {POP_POPULATION}: {self._population:,}\n'
        else:
            return f'    {POP_POPULATION}: {self._population}\n'

    def _get_pop_per_100k(self):
        """Returns a string for the str() method which handles the formatting of valid values for the number of bands
        per 100k people (rounds to two digits) and simply prints 'NA' for invalid values.

        :return: A perfectly formatted population per 100k people string used internally by the str() method.
        """
        if str(self._bands_per_100k).isalpha():
            return f'    {POP_PER_100K}: {self._bands_per_100k}\n'
        else:
            return f'    {POP_PER_100K}: {self._bands_per_100k:.2f}\n'

    def _get_csv_gender_data(self):
        gender_csv = ''

        for gender in self._genders:
            gender_csv += f'{self._genders[gender][0]};{self._genders[gender][1]:.2f};'

        return gender_csv

    @staticmethod
    def get_csv_header():
        return 'Country;Population;Bands;Bands per 100k;# Total;# Male;% Male;# Female;% Female;# Unknown;% Unknown;' \
               'TOP genre\n'

    def get_csv_data(self):
        export_data = f'{self._country_name};{self._population};{self._number_bands};'

        if str(self._bands_per_100k).isalpha():
            export_data += f'{self._bands_per_100k}'
        else:
            export_data += f'{self._bands_per_100k:.2f}'

        export_data += f';{self._amount_people};{self._get_csv_gender_data()}{self._genres[0][0]} Metal\n'

        return export_data

    def _make_sanity_report(self, index, message):
        """Generates two strings of either the missing or invalid bands. The strings can be used to print to the
        terminal or to save the list to a file.

        :param index: The index signifies which list from the checked bands is picked. 0 means "missing" and 1 is
            "invalid". There is no boundary check.
        :param message: This should be either "Missing" or "Invalid" as nothing else makes sense.
        :return: A tuple of two strings. The first is one continuous line mainly used to print to the terminal. The
            second is used to save the list to a file for later processing. If no bands are available the function
            returns None.
        """
        if self._checked_bands is None:
            return None
        # TODO: No boundary checks. Rewrite to named tuple.
        bands = self._checked_bands[index]

        if len(bands) < 1:
            return None

        print_report = f'    {message} ({len(bands)}). '
        export_text = ''

        for band in self._checked_bands[index]:
            export_text += f'{band}\n'

        return print_report, export_text

    def save_report_missing(self):
        return self._save_sanity_report(FOLDER_LINKS_MISSING, self._report_missing[1])

    def save_report_invalid(self):
        return self._save_sanity_report(FOLDER_LINKS_INVALID, self._report_invalid[1])

    def _save_sanity_report(self, folder, export_text):
        report_path = Path(f'{folder}/{self._country_short}_{get_time_stamp()}{LINK_EXTENSION}')
        report_path.write_text(export_text)
        return report_path

    def __str__(self):
        if len(self._genders) == 0:
            return "Invalid Country Report: Genders not set."

        report = f'  {self._country_name}\n'
        report += self._get_population()
        report += f'    Bands: {self._number_bands}\n'
        report += self._get_pop_per_100k()
        report += f'    {GENDER_DISTRIBUTION.format(self._amount_people, len(self._gender_per_country))}'

        for gender, value_pair in self._genders.items():
            report += f'      {GENDER[gender]}: {value_pair[0]} ({value_pair[1]:.2f}%)\n'

        # Take the maximum from the settings file.
        top = TOP

        # Make sure we only print the amount available (until maximum defined above).
        if len(self._genres) < top:
            top = len(self._genres)

        report += f'    TOP {top} Genres;\n'

        for index in range(0, top):
            report += f'      {self._genres[index][0]}: {self._genres[index][1]} ({self._genres[index][2]:.2f}%)\n'

        if self._report_missing:
            report += self._report_missing[0] + 'Saved in ' + str(self.save_report_missing()) + '\n'

        if self._report_invalid:
            report += self._report_invalid[0] + 'Saved in ' + str(self.save_report_invalid()) + '\n'

        return report


class DatabaseReport:
    """A DatabaseReport stores the analysis of the entire database plus the attached CountryReport objects. It always
    contains e.g. the amount of _all_ artists and which genders they have.
    """
    def __init__(self, band_count, genders, artist_count, artists_per_country, genres, album_report, report_mode):
        self._band_count = band_count
        self._genders = {}
        self._country_reports = []
        self._genres = []
        self._amount_artists = 0
        self._artists_per_country = []
        self._report_mode = report_mode
        self.album_report = album_report
        self.bands_per_year = defaultdict(int)

        for gender in genders:
            self._amount_artists += genders[gender]
            self._genders[gender] = (genders[gender], (genders[gender] / artist_count) * 100)
            self._artists_per_country = artists_per_country

        genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))

        for genre_name, count in genres.items():
            self._genres.append((genre_name, count, (count / band_count) * 100))

    def add_country_report(self, report: CountryReport):
        """Appends the ready made CountryReport to the DatabaseReport.

        :param report: The CountryReport to add.
        """
        for year, number in report.bands_per_year.items():
            self.bands_per_year[year] += number
        self._country_reports.append(report)

    def export_csv_bands_formed(self):
        """Generates a CSV file with formed bands per year sorted by total amount for each country.

        :return: The Path object to the saved file.
        """
        sorted_bands_per_year = OrderedDict(sorted(self.bands_per_year.items()))
        last_year = list(sorted_bands_per_year.keys())[0]

        for actual_year in sorted_bands_per_year.keys():
            # If the difference between the actual and last year is greater than 1, we need to insert the missing years.
            year_diff = actual_year - last_year
            if year_diff > 1:
                for missed_year in range(last_year + 1, actual_year):
                    # We cannot change the ordered dict while we iterate on it, so we make changes to the source.
                    self.bands_per_year[missed_year] = 0
            last_year = actual_year

        # Sort the source again, because we added missing years to it.
        sorted_bands_per_year = OrderedDict(sorted(self.bands_per_year.items()))
        first_year = list(sorted_bands_per_year.keys())[0]
        # Sort collection by amount of bands.
        sorted_bands_by_count = sorted(self._country_reports, key=lambda x: x._number_bands, reverse=True)

        # Generate the header first.
        export_text = 'Years;Total;'
        for country_report in sorted_bands_by_count:
            export_text += f'{country_report._country_name};'

        export_text += '\n'
        # Now add the real data.
        for actual_year in range(first_year, last_year + 1):
            export_text += f'{actual_year};{self.bands_per_year[actual_year]};'
            for country_report in sorted_bands_by_count:
                export_text += f'{country_report.bands_per_year[actual_year]};'
            export_text += '\n'

        export_file = get_export_path('bands_formed', 'csv')
        export_file.write_text(export_text, encoding="utf-8")

        return export_file

    def export_csv_country(self):
        export_text = CountryReport.get_csv_header()

        for report in self._country_reports:
            export_text += report.get_csv_data()

        export_file = get_export_path('countries', 'csv')
        export_file.write_text(export_text, encoding="utf-8")

        return export_file

    def export_csv_genres(self):
        """Exports a CSV of all genres (rows) in all countries (columns).

        :return: The Path object to the saved file.
        """
        country_genres = {'Total': {}}
        genre_cache = {}

        for report in self._country_reports:
            genre_tuples = report.get_genres()
            # I know that it's sloppy.
            genre_cache[report._country_name] = {}

            for genre_tuple in genre_tuples:
                # 0: Genre name
                if genre_tuple[0] not in country_genres['Total'].keys():
                    country_genres['Total'][genre_tuple[0]] = genre_tuple[1]
                else:
                    country_genres['Total'][genre_tuple[0]] += genre_tuple[1]

                genre_cache[report._country_name][genre_tuple[0]] = genre_tuple[1]

        # At this point we have a all known genres in 'Total'. Now we need to construct the rest of the table. Having
        # the cache will make that easier.
        # Sort the dict from highest to lowest amount of genres.
        country_genres['Total'] = dict(sorted(country_genres['Total'].items(), key=lambda x: x[1], reverse=True))
        # First two items of the header.
        export_all = 'Genre;Total;'

        # Add all other countries to the header. TODO: Maybe sort the countries too.
        for country in genre_cache.keys():
            export_all += f'{country};'

        # Last item of the header.
        export_all += '\n'
        export_core = export_all

        # This loop constructs the rest of the table, starting with the genre.
        for genre_name, count in country_genres['Total'].items():
            export_all += f'{genre_name};{count};'
            # Either append the number of bands playing the genre or an empty cell.
            for country in genre_cache.keys():
                if genre_name in genre_cache[country].keys():
                    export_all += f'{genre_cache[country][genre_name]};'
                else:
                    export_all += ';'

            export_all += '\n'

        export_file_all = get_export_path('genres_all', 'csv')
        export_file_all.write_text(export_all, encoding="utf-8")

        for genre_name in GENRE_CORE_MA:
            if genre_name in country_genres["Total"].keys():
                export_core += f'{genre_name};{country_genres["Total"][genre_name]};'
            else:
                export_core += f'{genre_name};;'

            for country in genre_cache.keys():
                if genre_name in genre_cache[country].keys():
                    export_core += f'{genre_cache[country][genre_name]};'
                else:
                    export_core += ';'

            export_core += '\n'

        export_file_core = get_export_path('genres_core', 'csv')
        export_file_core.write_text(export_core, encoding="utf-8")

        return export_file_all, export_file_core

    @staticmethod
    def get_csv_header():
        return 'Country;Population;Bands;Bands per 100k;# Male;% Male;# Female;% Female;# Unknown;% Unknown;TOP genre'

    def __str__(self):
        if len(self._country_reports) == 1:
            word = 'country'
        else:
            word = 'countries'

        report = f'Database report for {len(self._country_reports)} {word}. {self._amount_artists} artists from '
        report += f'{len(self._artists_per_country)} countries play in {self._band_count} bands.\n'
        report += f'  Gender distribution for entire database:\n'

        country_report_str = ''

        if self._report_mode is ReportMode.CountryOn:
            for country_report in self._country_reports:
                country_report_str += str(country_report)

        for gender, value_pair in self._genders.items():
            report += f'    {GENDER[gender]}: {value_pair[0]} ({value_pair[1]:.2f}%)\n'

        report += f'  Genre distribution: {self._band_count} bands play {len(self._genres)} genres.\n'
        report += '  There will be more genres than bands. A band playing Atmospheric Black Metal\n'
        report += '  counts as both "Atmospheric Black" and "Black".\n'

        for genre in self._genres:
            report += f'    {genre[0]}: {genre[1]} ({genre[2]:.2f}%)\n'

        return report + country_report_str + str(self.album_report)


class ReleaseReport:
    """A ReleaseReport stores the data for releases and prints it to he command line and/or exports it to a CSV file.
    """

    def __init__(self, workable_types: list):
        """The constructor needs a list of release types to work with. The types must be written exactly as any of the
            values in RELEASE_TYPES. Raises ValueError if the `workable_types` list is invalid.

        :param workable_types: List of release types to consider when `process_release` is called.
        """
        if len(workable_types) == 0:
            raise ValueError('List or workable types was empty.')

        for workable_type in workable_types:
            if workable_type not in RELEASE_TYPES.values():
                raise ValueError(f'The type {workable_type} is not recognized.')

        self.workable_types = workable_types
        self.country_releases = defaultdict(lambda: defaultdict(int))
        self.releases_total = defaultdict(int)
        self.releases_per_year = defaultdict(lambda: defaultdict(list))
        self.all_releases = defaultdict(list)
        self.logger = logging.getLogger('ReleaseReport')

    def process_release(self, country_name, band_id, band_name, release_name, link, release_type, year, ratings,
                        review_count):
        if len(country_name) < 1:
            raise ValueError('Country name was empty.')
        elif len(band_name) < 1:
            raise ValueError('Band name was empty.')
        elif release_type not in self.workable_types:
            # For now we don't want to consider any releases other than defined in the settings.
            return

        # Collect release counts per type (and total).
        self.country_releases[country_name][release_type] += 1
        self.releases_total[release_type] += 1

        # Collect releases in a tuple. We filter by the minimum values for average percentage_bands and review count from the
        # settings file.
        if ratings >= RELEASE_AVERAGE_MIN and review_count >= RELEASE_REVIEW_COUNT_MIN:
            # Instantiate release types in the order we like (so that the JSON export is consistent).
            if str(year)[0:4] not in self.releases_per_year:
                for temp_type in self.workable_types:
                    self.releases_per_year[str(year)[0:4]][temp_type] = []
            self.releases_per_year[str(year)[0:4]][release_type].append((release_name, band_name, ratings, link))
            self.all_releases[release_type].append(
                {
                    "release_name": release_name,
                    "country_name": country_name,
                    "link": link,
                    "ratings": ratings,
                    "band_name": band_name
                }
            )

    @staticmethod
    def get_release_tuple_string(release_tuple):
        if len(release_tuple) >= 3:
            return f'{release_tuple[0]} ({release_tuple[2]}%) by {release_tuple[1]}'
        else:
            return ''

    @staticmethod
    def _get_sort_key(item):
        """This strange-looking function serves the sorting of releases in `export_csv_releases`.

        :param item: A release tuple.
        :return: The score element of a release tuple.
        """
        return item[2]

    def export_csv_releases_per_year(self):
        # Prep the CSV header.
        export_text = 'Year;'

        for release_type in self.workable_types:
            export_text += f'{release_type};'

        export_text += '\n'
        releases_per_year = dict(sorted(self.releases_per_year.items(), reverse=True))

        for year, release_types in releases_per_year.items():
            export_text += f'{year};'

            # Types will be exported in columns. First we determine the maximum amount of elements in the largest
            # category.
            type_size = 0
            sorted_types = {}

            for release_type, releases in release_types.items():
                if len(releases) > type_size:
                    type_size = len(releases)
                sorted_types[release_type] = sorted(releases, key=self._get_sort_key, reverse=True)

            for i in range(0, type_size):
                # We want the the year column to be empty and only contain the year.
                if i > 0:
                    export_text += ';'

                # We use the workable types to check existence and control the order.
                for type_name in self.workable_types:
                    # Add the actual element.
                    if i < len(release_types[type_name]):
                        export_text += f'{self.get_release_tuple_string(sorted_types[type_name][i])};'
                    # Add an empty cell because there are no elements anymore.
                    else:
                        export_text += ';'

                export_text += '\n'

        export_file = get_export_path('releases_per_year', 'csv')
        export_file.write_text(export_text, encoding="utf-8")

        return export_file

    def export_all_releases(self):
        export_releases = {}

        for temp_type in self.workable_types:
            export_releases[temp_type] = []

        for release_type, releases in self.all_releases.items():
            # Sort the releases by the ratings property in each dict of the releases list.
            sorted_releases = sorted(releases, key=lambda x: x['ratings'], reverse=True)
            counter = 1
            last_used_number = 0

            # No release can be better than 100%. But it ensures that the conditions inside the loop works even if the
            # first ratings value is 100.
            last_rating = 101

            for temp_release in sorted_releases:
                # Use counter as actual number.

                if temp_release['ratings'] < last_rating:
                    last_used_number = counter
                elif temp_release['ratings'] is last_rating:
                    pass

                counter += 1
                temp_release['rank'] = last_used_number
                export_releases[release_type].append(temp_release)
                # Save the current ratings value.
                last_rating = temp_release['ratings']

        json_export = json.dumps(export_releases)
        export_file = get_export_path('all_releases', 'json')
        export_file.write_text(json_export, encoding="utf-8")
        return export_file

    def export_json_releases_per_year(self):
        # Define valid release types for functionality using the JSON export.
        export_releases = [{"categories": self.workable_types}]
        # Sort the existing dict by year (descending) and use copy from now on.
        releases_per_year = dict(sorted(self.releases_per_year.items(), reverse=True))

        for year, release_types in releases_per_year.items():
            export_releases.append({"year": year})

            for release_type, releases in release_types.items():
                # Sort releases of the actual type by average score (descending).
                sorted_releases = sorted(releases, key=lambda x: x[2], reverse=True)
                temp_releases = []

                for release in sorted_releases:
                    temp_release = {
                        "name": release[0],
                        "band": release[1],
                        "rating": release[2],
                        "link": release[3],
                    }
                    temp_releases.append(temp_release)
                # It's safe to use the length here because a year was added.
                export_releases[len(export_releases)-1][release_type] = temp_releases

        # convert into JSON:
        json_export = json.dumps(export_releases)
        export_file = get_export_path('releases_per_year', 'json')
        export_file.write_text(json_export, encoding="utf-8")

        return export_file

    def __str__(self):
        report = 'Release Report (percentages in relation to totals):\n  Totals\n'

        for release_type, count in self.releases_total.items():
            report += f'    {release_type}s: {count}\n'

        for country, releases in self.country_releases.items():
            report += f'  {country}\n'
            for release_type, count in releases.items():
                percentage = (count / self.releases_total[release_type]) * 100
                report += f'    {release_type}s: {count} ({percentage:.2f}%)\n'

        # Take the maximum from the settings file.
        if TOP < 1:
            top = 1
        else:
            top = TOP

        releases_per_year = dict(sorted(self.releases_per_year.items(), reverse=True))
        report += 'Best releases per year:\n'

        for year, releases in releases_per_year.items():
            top_temp = top
            if len(releases[RELEASE_TYPES['F']]) < top:
                top_temp = len(releases[RELEASE_TYPES['F']])

            # No full-length releases in this year.
            if top_temp == 0:
                continue

            sorted_releases = sorted(releases[RELEASE_TYPES["F"]], key=lambda x: x[2], reverse=True)
            report += f'  Best releases in {year} (TOP {top_temp} of {len(sorted_releases)}):\n'

            for i in range(0, top_temp):
                report += f'    {self.get_release_tuple_string(sorted_releases[i])}\n'

        return report
