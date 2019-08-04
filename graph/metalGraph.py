from abc import ABCMeta, abstractmethod

POP_PER_100K = 'Bands per 100k people'
POP_POPULATION = 'Population'
POP_BANDS = 'Bands'


def prettify_calc_result(calc_dict: dict) -> str:
    """Prettifies the raw data from the dict returned by calc_bands_per_pop.

    :param calc_dict: Takes a dict with the format supplied by calc_bands_per_pop.
    :return: A string representation of the given dict.
    """
    pretty_string = ""

    if len(calc_dict) is 0:
        return pretty_string

    for inner_key, inner_value in calc_dict.items():
        pretty_string += f'  {inner_key}\n'
        for outer_key, outer_value in inner_value.items():
            pretty_string += f'    {outer_key}: {outer_value}\n'

    return pretty_string[:-1]


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
            used: 'bands' and 'artists'. For ~10k bands and ~40k artists this takes ~7s. It's faster than checking for
            the existence of nodes (which takes ~0.01s for the neomodel implementation).

        :return: Dictionary with all known 'bands' and 'artists'. Each short link of these entities has a time stamp of
            the last visit as the value.
        """
        return self._strategy.get_all_links_interface()

    def export_bands_network(self, country_short=None):
        return self._strategy.export_bands_network_interface(country_short)

    def calc_bands_per_pop(self, country_short) -> dict:
        return self._strategy.calc_bands_per_pop_interface(country_short)

    def raw_analysis(self):
        return self._strategy.raw_analysis_interface()


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
    def export_bands_network_interface(self, country_short):
        pass

    @abstractmethod
    def calc_bands_per_pop_interface(self, country_short) -> dict:
        pass

    @abstractmethod
    def raw_analysis_interface(self):
        pass
