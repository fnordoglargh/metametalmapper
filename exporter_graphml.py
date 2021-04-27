from exporter_strategy import ExportingStrategy
from export_data import ExportData


class ExporterGraphML(ExportingStrategy):
    def __init__(self):
        super().__init__('graphml')

    def do_export(self, export_data: ExportData):
        pass
