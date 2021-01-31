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

    def __init__(self, country, year: int, band_name: str, release_name: str, link: str, release_type, rating: int, review_count: int):
        if release_type in RELEASE_TYPES:
            self.release_type = RELEASE_TYPES[release_type]

        self.country = country
        self.year = year
        self.band_name = band_name
        self.release_name = release_name
        self.link = link
        self.rating = rating
        self.review_count = review_count


@dataclass
class ExportGender:
    genders: Dict = field(default_factory=dict)
    totals: Dict = field(default_factory=dict)


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
    genders: Dict = field(default_factory=dict)
    genres: Dict = field(default_factory=dict)
    formation_year_totals: Dict[int, int] = field(default_factory=dict)
    country_data: Dict[str, CountryData] = field(default_factory=dict)
    releases: List[ExportRelease] = field(default_factory=list)
    bands_total = 0
    formation_year_min = datetime.today().year

    # def __init__(self):
    #     self.genres['Totals'] = {}

    def add_gender_country(self, band_origin, artist_origin, gender, count):
        """Function to add sane gender data to the underlying genders collection. Countries and genders will be added
            as keys to the dict.

        :param band_origin: An ISO country name; used as key for the gender data. The origin of the band has the highest
            priority, under that the individual band members are counted under the state of their origin.
        :param artist_origin: An ISO country name; used as key for the gender data of artists under a country.
        :param gender: A gender key as defined in graph.choices module (GENDERS).
        :param count: The total number of entries for he supplied gender.
        :return: True if the supplied country and gender are valid, otherwise False.
        """
        is_applied = False

        if band_origin in COUNTRY_NAMES.keys() and artist_origin in COUNTRY_NAMES.keys():
            if band_origin not in self.genders:
                self.genders[band_origin] = {}
            if artist_origin not in self.genders[band_origin]:
                self.genders[band_origin][artist_origin] = {}
            if gender in GENDER.keys():
                if count < 0:
                    count = 0
                else:
                    is_applied = True
                self.genders[band_origin][artist_origin][gender] = count

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

    def add_release(self, country, band_name, release_name, rating, review_count, link, release_type, date):
        """Add a release to the dataclass if rating, review_count and release_type match the values from the settings
            file.

        :param country:
        :param band_name:
        :param release_name:
        :param rating:
        :param review_count:
        :param link:
        :param release_type:
        :param date:
        :return: True if the release was added and False if it was filtered.
        """
        if review_count < RELEASE_REVIEW_COUNT_MIN or release_type not in RELEASE_TYPES_REVIEW \
                or rating < RELEASE_AVERAGE_MIN:
            return False

        release_year = int(date[:4])
        release = ExportRelease(country, release_year, band_name, release_name, link, release_type, rating, review_count)

        self.releases.append(release)

        return True

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

        for country in self.country_data.values():
            country.percentage_bands = country.number_bands / self.bands_total
            country.formation_years = OrderedDict(sorted(country.formation_years.items()))
