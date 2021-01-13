from dataclasses import dataclass, field
from typing import Dict, List

from country_helper import COUNTRY_NAMES
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
class ExportData:
    origins: Dict = field(default_factory=dict)
    genders: Dict = field(default_factory=dict)
    genres: Dict = field(default_factory=dict)
    releases: List[ExportRelease] = field(default_factory=list)

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
            for genre in genres:
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

