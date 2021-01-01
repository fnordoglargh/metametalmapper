import logging

from graph.graph_neomodel_impl import NeoModelStrategy
from graph.report import DatabaseReport, ReportMode
from export_data import ExportData

def init_db():
    logger = logging.getLogger('Mapper')
    db_handle = None
    try:
        db_handle = GraphDatabaseContext(NeoModelStrategy())
    except:
        logger.error('  Need a database to function properly. Exiting...')

    return db_handle


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

    def prepare_export_data(self, country_shorts: list, report_mode: ReportMode) -> ExportData:
        return self._strategy.prepare_export_data(country_shorts, report_mode)

    def generate_report(self, country_shorts=None, report_mode=ReportMode.CountryOn) -> DatabaseReport:
        return self._strategy.generate_report_interface(country_shorts, report_mode)