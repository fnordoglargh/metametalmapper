"""Contains both base files of the strategy pattern to write database implementations. Each implementation
    must inherit `GraphDatabaseStrategy`. Database handles are instantiated with 
    `GraphDatabaseContext(Implementation)`. See implementation in graph_neomodel_impl.py."""

from abc import ABCMeta, abstractmethod
from pathlib import Path

from graph.report import DatabaseReport, ReportMode
from global_helpers import FOLDER_LINKS, LINK_EXTENSION
from country_helper import COUNTRY_NAMES

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2020, Martin Woelke'

POP_PER_100K = 'Bands per 100k people'
POP_POPULATION = 'Population'
POP_BANDS = 'Bands'
RAW_GENRES = 'Genres'
POP_COUNTRY = 'Country'


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
        is either a valid country name or 'Not a country: "country_short"'
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


class GraphDatabaseContext:

    def __init__(self, strategy):
        self._strategy = strategy

    def add_band(self, band_dict):
        self._strategy.add_band_interface(band_dict)

    def add_label(self, label_dict):
        self._strategy.add_label_interface(label_dict)

    def add_release(self, release_dict):
        self._strategy.add_release_interface(release_dict)

    def add_member(self, member_dict):
        self._strategy.add_member_interface(member_dict)

    def band_recorded_release(self, band_id, release_id):
        self._strategy.band_recorded_release_interface(band_id, release_id)

    def member_played_in_band(self, member_id, band_id, instrument, pseudonym, time_frame, status):
        # time_frame: Pairs of two are treated as start and end dates. If someone was only in for a year you still
        # need the same date twice.
        self._strategy.member_played_in_band_interface(member_id, band_id, instrument, pseudonym, time_frame, status)

    def label_issued_release(self, label_id, release_id):
        self._strategy.label_issued_release_interface(label_id, release_id)

    def get_all_links(self) -> dict:
        """Prepares a dictionary that contains all previously visited short links of all bands and artists. Two keys are
            used: 'bands' and 'artists'. For ~10k bands and ~40k artists this takes ~7s. Using the lookup table is  much
            faster than checking for the existence of nodes (which takes ~0.01s for the neomodel implementation per
            check).

        :return: Dictionary with all known 'bands' and 'artists'. Each short link of these entities has a time stamp of
            the last visit as the value.
        """
        return self._strategy.get_all_links_interface()

    def export_bands_network(self, country_shorts=None):
        return self._strategy.export_bands_network_interface(country_shorts)

    def calc_bands_per_pop(self, country_short, bands) -> dict:
        return self._strategy.calc_bands_per_pop_interface(country_short, bands)

    def generate_report(self, country_shorts=None, report_mode=ReportMode.CountryOn) -> DatabaseReport:
        return self._strategy.generate_report_interface(country_shorts, report_mode)


class GraphDatabaseStrategy(metaclass=ABCMeta):

    @abstractmethod
    def add_band_interface(self, band_dict):
        pass

    @abstractmethod
    def add_label_interface(self, label_dict):
        pass

    @abstractmethod
    def add_release_interface(self, release_dict):
        pass

    @abstractmethod
    def add_member_interface(self, member_dict):
        pass

    @abstractmethod
    def band_recorded_release_interface(self, band_id, release_id):
        pass

    @abstractmethod
    def member_played_in_band_interface(self, member_id, band_id, instrument, pseudonym, time_frame, status):
        pass

    @abstractmethod
    def label_issued_release_interface(self, label_id, release_id):
        pass

    @abstractmethod
    def get_all_links_interface(self) -> dict:
        pass

    @abstractmethod
    def export_bands_network_interface(self, country_shorts):
        pass

    @abstractmethod
    def calc_bands_per_pop_interface(self, country_short, bands) -> dict:
        pass

    @abstractmethod
    def generate_report_interface(self, country_shorts, report_mode) -> DatabaseReport:
        pass
