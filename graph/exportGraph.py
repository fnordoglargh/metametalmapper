from abc import ABCMeta, abstractmethod
from pathlib import Path


class GraphExportContext:

    def __init__(self, strategy):
        self._strategy = strategy

    def export_graph(self, data_dict):
        self._strategy.export_bands_interface(data_dict)


class GraphExportStrategy(metaclass=ABCMeta):

    @abstractmethod
    def export_graph_interface(self, db_handle):
        pass


class GraphMLExporter(GraphExportStrategy):
    def export_graph_interface(self, data_dict):
        pass
