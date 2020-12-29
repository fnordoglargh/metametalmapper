"""Classes to export data into different formats."""
from enum import Enum

from graph.metal_graph_context import GraphDatabaseContext
from exporter_strategy import ExportingStrategy
from exporter_raw import ExporterRaw
from exporter_markdown import ExporterMarkdown


class ExportMode(Enum):
    Raw = 0
    Markdown = 1


class Exporter:
    def __init__(self, export_mode: ExportMode, db_handle: GraphDatabaseContext) -> None:
        if export_mode is ExportMode.Markdown:
            strategy = ExporterMarkdown()
        else:
            strategy = ExporterRaw

        self._strategy = strategy
        self._db_handle = db_handle

    @property
    def strategy(self) -> ExportingStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: ExportingStrategy) -> None:
        self._strategy = strategy

    def do_export(self) -> None:
        self._strategy.do_export()


