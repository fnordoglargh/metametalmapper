"""Contains both base files of the strategy pattern to write database implementations. Each implementation
    must inherit `GraphDatabaseStrategy`. Database handles are instantiated with 
    `GraphDatabaseContext(Implementation)`. See implementation in graph_neomodel_impl.py."""

from abc import ABCMeta, abstractmethod

from graph.report import DatabaseReport, ReportMode
from export_data import ExportData

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2021, Martin Woelke'

POP_PER_100K = 'Bands per 100k people'
POP_POPULATION = 'Population'
POP_BANDS = 'Bands'
RAW_GENRES = 'Genres'
POP_COUNTRY = 'Country'


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
    def prepare_export_data(self, country_shorts: list, report_mode: ReportMode) -> ExportData:
        pass

    @abstractmethod
    def generate_report_interface(self, country_shorts, report_mode) -> DatabaseReport:
        pass
