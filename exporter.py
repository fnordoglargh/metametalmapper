"""Classes to export data into different formats."""
from enum import Enum
from typing import List

from graph.report import DatabaseReport, ReportMode
from graph.metal_graph_context import GraphDatabaseContext
from exporter_strategy import ExportingStrategy
from exporter_raw import ExporterRaw
from exporter_markdown import ExporterMarkdown
from exporter_graphml import ExporterGraphML
from export_data import ExportData

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2022, Martin Woelke'


class ExportMode(Enum):
    Raw = 0
    Markdown = 1
    GraphML = 2


class Exporter:
    def __init__(self, export_mode: ExportMode, db_handle: GraphDatabaseContext, countries: List[str],
                 report_mode: ReportMode) -> None:
        self._mode = export_mode
        if export_mode is ExportMode.Markdown:
            strategy = ExporterMarkdown()
        elif export_mode is ExportMode.GraphML:
            strategy = ExporterGraphML()
        else:
            strategy = ExporterRaw()

        self._strategy = strategy
        self._db_handle = db_handle

        if export_mode is ExportMode.GraphML:
            # TODO: Looks ugly already. Introduce dict into ExportData for the graph?
            self.prepped_data = ExportData()
            self.prepped_data.band_network = db_handle.export_bands_network(countries)
        else:
            self.prepped_data = db_handle.prepare_export_data(countries, report_mode)

    @property
    def strategy(self) -> ExportingStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: ExportingStrategy) -> None:
        self._strategy = strategy

    def do_export(self) -> None:
        if self._mode is not ExportMode.GraphML:
            self.prepped_data.do_export_calc()
        self._strategy.do_export(self.prepped_data)
