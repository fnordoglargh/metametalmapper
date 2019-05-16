from abc import ABCMeta, abstractmethod


class GraphDatabaseContext:

    def __init__(self, strategy):
        self._strategy = strategy

    def add_band(self, band_dict):
        self._strategy.add_band_interface(band_dict)

    def add_label(self, label_dict):
        self._strategy.add_label_interface(label_dict)

    def add_album(self, album_dict):
        self._strategy.add_album_interface(album_dict)


class GraphDatabaseStrategy(metaclass=ABCMeta):

    @abstractmethod
    def add_band_interface(self, band_dict):
        pass

    @abstractmethod
    def add_label_interface(self, label_dict):
        pass

    @abstractmethod
    def add_album_interface(self, album_dict):
        pass
