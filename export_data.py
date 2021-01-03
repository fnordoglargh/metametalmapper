from dataclasses import dataclass, field
from typing import Dict

from country_helper import COUNTRY_NAMES
from graph.choices import GENDER


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
class ExportGender:
    genders: Dict = field(default_factory=dict)


@dataclass
class ExportData:
    origins: Dict = field(default_factory=dict)
    genders: Dict = field(default_factory=dict)
    genres: Dict = field(default_factory=dict)

    def add_gender_country(self, country, gender, count):
        """Function to add sane gender data to the underlying genders collection. Countries and genders will be added
            as keys to the dict.

        :param country: An ISO country name; used as key for the genre data.
        :param gender: A gender key as defined in graph.choices module (GENDERS).
        :param count: The total number of entries for he supplied gender.
        :return: True if the supplied country and gender are valid, otherwise False.
        """
        is_applied = False

        if country in COUNTRY_NAMES.keys():
            if country not in self.genders:
                self.genders[country] = {}
            if gender in GENDER.keys():
                self.genders[country][gender] = count
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
            for genre in genres:
                if genre not in self.genres[country]:
                    self.genres[country][genre] = count
                else:
                    self.genres[country][genre] += count
                is_applied = True

        return is_applied
