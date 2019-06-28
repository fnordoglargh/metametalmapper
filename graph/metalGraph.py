from abc import ABCMeta, abstractmethod


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
