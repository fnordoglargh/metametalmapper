from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime
from collections import defaultdict, OrderedDict

from country_helper import COUNTRY_NAMES, COUNTRY_POPULATION
from graph.choices import GENDER, RELEASE_TYPES
from settings import RELEASE_AVERAGE_MIN, RELEASE_REVIEW_COUNT_MIN, RELEASE_TYPES_REVIEW


# def load_list(raw_lists: list, lookup_table: dict) -> dict:
#     """Loads data from a list of lists into a dictionary.
#
#     :param raw_lists: A lists of lists as returned by a cypher query.
#     :param lookup_table: A dictionary from the choices module (containing the database.
#     :return: A dict the translated data which can be easily read humans and used as is for any exports.
#     """
#     resulting_dict = {}
#
#     for element in raw_lists:
#         resulting_dict[lookup_table[element[0]]] = element[1]
#
#     return resulting_dict

@dataclass
class ExportRelease:
    country: str = 'not set'
    year: int = -1
    link: str = 'not set'
    band_name: str = 'not set'
    release_name: str = 'not set'
    rating: int = -1
    review_count: int = -1
    release_type: str = 'not set'

    def __init__(self, country, year: int, band_name: str, release_name: str, link: str, release_type, rating: int,
                 review_count: int, is_filtered: bool):

        if release_type in RELEASE_TYPES:
            self.release_type = RELEASE_TYPES[release_type]
        else:
            # TODO: Add Exception?
            pass

        self.country = country
        self.year = year
        self.band_name = band_name
        self.release_name = release_name
        self.link = link
        self.rating = rating
        self.review_count = review_count
        self.is_filtered = is_filtered


@dataclass
class ExportGender:
    totals: int
    genders: dict = field(default_factory=int)
    percentages: dict = field(default_factory=float)

    def __init__(self):
        self.genders = {}
        self.percentages = {}
        self.totals = 0

    def add_gender(self, gender, number):
        if gender in GENDER:
            self.genders[gender] = number
            self.totals += number

    def inc_gender(self, gender):
        if gender in GENDER:
            if gender not in self.genders:
                self.genders[gender] = 0
            self.genders[gender] += 1
            self.totals += 1

    def update_percentages(self, totals=-1):
        # TODO: Add totals for the worlds total artist numbers.
        for gender, number in self.genders.items():
            self.percentages[gender] = number/self.totals


@dataclass
class CountryData:
    formation_year_min = datetime.today().year
    formation_years: Dict = field(default_factory=dict)
    country_name: str = 'not set'
    number_bands: int = -1
    number_formation_total: int = 0
    bands_per_100k: float = -1.0
    percentage_bands: float = -1.0

    def __init__(self, country_short: str, number_bands: int):
        self.country_name = COUNTRY_NAMES[country_short]
        self.number_bands = number_bands
        self.bands_per_100k = number_bands/(int(COUNTRY_POPULATION[country_short])/100000)
        self.formation_years = {}

    def add_formation_year(self, year: int, number_formation: int):
        # Fill every year which is not in the collection yet with zeros.
        if year < self.formation_year_min:
            for year_add in range(year, self.formation_year_min):
                self.formation_years[year_add] = 0
            # Set the new minimum year.
            self.formation_year_min = year
        # At last we write the actual data.
        self.formation_years[year] = number_formation
        self.number_formation_total += number_formation


@dataclass
class ExportData:
    origins: Dict = field(default_factory=dict)
    # Genders of all artists hailing from a certain country.
    genders_country: Dict[str, ExportGender] = field(default_factory=dict)
    # Genders of all artists playing in bands from a certain country. Every artists is counted once per country but can
    # play in different countries.
    genders_origins: Dict[str, dict] = field(default_factory=dict)
    genres: Dict = field(default_factory=dict)
    formation_year_totals: Dict[int, int] = field(default_factory=dict)
    country_data: Dict[str, CountryData] = field(default_factory=dict)
    releases: Dict[int, dict] = field(default_factory=dict)
    bands_total = 0
    formation_year_min = datetime.today().year

    def add_gender_country(self, artist_origin, gender, count=1, band_origin=''):
        """Function to add sane gender data to the underlying genders_country collection. Countries and genders_country will be added
            as keys to the dict.

        :param artist_origin: An ISO country name; used as key for the gender data of artists under a country.
        :param gender: A gender key as defined in graph.choices module (GENDERS).
        :param count: The total number of entries for he supplied gender. Number will be set to 0 if the given number is
            smaller than 0.
        :param band_origin: An ISO country name; used as key for the gender data. The origin of the band has the highest
            priority, under that the individual band members are counted under the state of their origin.
        :return: True if the supplied country and gender are valid, otherwise False.
        """
        is_applied = False

        if band_origin == '':
            if artist_origin not in self.genders_country:
                self.genders_country[artist_origin] = ExportGender()
            self.genders_country[artist_origin].add_gender(gender, count)
            is_applied = True
        elif band_origin in COUNTRY_NAMES.keys() and artist_origin in COUNTRY_NAMES.keys():
            if gender in GENDER.keys():
                if band_origin not in self.genders_origins.keys():
                    self.genders_origins[band_origin] = {}
                if artist_origin not in self.genders_origins[band_origin].keys():
                    self.genders_origins[band_origin][artist_origin] = ExportGender()

                self.genders_origins[band_origin][artist_origin].inc_gender(gender)
                is_applied = True

        return is_applied

    def add_genre_country(self, country: str, genres: list, count: int):
        """Adds sane genre data on a per country basis to the underlying genres dict. Countries and genres will be added
            as keys to the dict.

        :param country: An ISO country name; used as key for the genre data.
        :param genres: A list of genres played in the supplied country.
        :param count: The number of bands playing each of the genres.
        :return: True if the supplied country and genres are valid, otherwise False.
        """
        is_applied = False

        if country in COUNTRY_NAMES.keys():
            if country not in self.genres:
                self.genres[country] = {}
            if 'Total' not in self.genres:
                self.genres['Total'] = {}

            for genre in genres:
                if genre not in self.genres['Total']:
                    self.genres['Total'][genre] = count
                else:
                    self.genres['Total'][genre] += count

                if genre not in self.genres[country]:
                    self.genres[country][genre] = count
                else:
                    self.genres[country][genre] += count
                is_applied = True

        return is_applied

    def add_release(self, country, band_name, name, rating, review_count, link, release_type, date):
        """Add a release to the dataclass. A flag (if the release was filtered) is automatically applied if rating and
            review_count are below the threshold from the settings file. An unwanted release_type is never added.
            file.

        :param country:
        :param band_name:
        :param name:
        :param rating:
        :param review_count:
        :param link:
        :param release_type:
        :param date:
        :return: True is the release was added and False if not. This only happens if the release type is unwanted.
        """

        if release_type not in RELEASE_TYPES_REVIEW:
            return False

        is_filtered = False

        if review_count < RELEASE_REVIEW_COUNT_MIN or rating < RELEASE_AVERAGE_MIN:
            is_filtered = True

        release_year = int(date[:4])
        release = ExportRelease(country, release_year, band_name, name, link, release_type, rating, review_count,
                                is_filtered)
        if release_year not in self.releases:
            self.releases[release_year] = {}

        if release_type not in self.releases[release_year]:
            self.releases[release_year][release_type] = []

        self.releases[release_year][release_type].append(release)

    def add_bands_per_country(self, country_short, number_bands):
        if country_short in COUNTRY_NAMES.keys():
            self. country_data[country_short] = CountryData(country_short, number_bands)
            self.bands_total += number_bands

    def add_band_formation_date(self, country_short: str, year: int, formation_number: int):
        if country_short in COUNTRY_NAMES.keys() and country_short in self.country_data.keys():
            if year < self.formation_year_min:
                self.formation_year_min = year
            self.country_data[country_short].add_formation_year(year, formation_number)

            if year not in self.formation_year_totals.keys():
                self.formation_year_totals[year] = formation_number
            else:
                self.formation_year_totals[year] += formation_number

        if country_short not in self.country_data.keys():
            pass

    def do_export_calc(self):
        formation_year_min = datetime.today().year

        # Determine the first year a metal band was founded.
        for country in self.country_data.values():
            if country.formation_year_min < formation_year_min:
                formation_year_min = country.formation_year_min

        for entry in self.genders_country.values():
            entry.update_percentages()

        for country in self.country_data.values():
            country.percentage_bands = country.number_bands / self.bands_total
            country.formation_years = OrderedDict(sorted(country.formation_years.items()))
