from abc import ABCMeta, abstractmethod
from pathlib import Path
import logging
from global_helpers import FOLDER_EXPORTS
from datetime import datetime


class GraphExportContext:

    def __init__(self, strategy):
        self._strategy = strategy

    def export_graph(self, data_dict):
        self._strategy.export_graph_interface(data_dict)


class GraphExportStrategy(metaclass=ABCMeta):

    @abstractmethod
    def export_graph_interface(self, db_handle):
        pass


class GraphMLExporter(GraphExportStrategy):

    def __init__(self):
        self.logger = logging.getLogger('GraphMLExporter')

    def export_graph_interface(self, data_dict: dict):
        self.logger.info('Starting GraphML export to file.')

        header = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<graphml xmlns="http://graphml.graphdrawing.org/xmlns"\n'
            f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
            f'xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">\n'
            f'<key id="d0" for="node" attr.name="band_name" attr.type="string"/>\n'
            f'<graph id="G" edgedefault="undirected">\n'
        )

        footer = (
            f'</graph>\n'
            f'</graphml>'
        )

        actual_time = datetime.now()
        time_stamp = f'{actual_time.date()}_{actual_time.time().strftime("%H%M%S")}'
        db_path = Path(f"{FOLDER_EXPORTS}/bands_{time_stamp}.graphml")
        export_file = open(db_path, "w", encoding="utf-8")
        export_file.write(header)

        # Go through collection once to create nodes.
        for node, payload in data_dict.items():
            band_name = payload["name"]

            if '&' in band_name:
                band_name = band_name.replace('&', '&amp;')

            export_file.write(f'<node id="n{node}"><data key="d0">{band_name}</data></node>\n')

        # The second time we write the connections. This might seem odd but Cytoscape does not like the connections
        # between the nodes.
        counter = 0

        for node, payload in data_dict.items():
            for relation in payload['relations']:
                export_file.write(f'<edge id="e{counter}" source="n{node}" target="n{relation}"/>\n')
                counter += 1

        export_file.write(footer)
        export_file.close()
        self.logger.info(f'Band network available as "{db_path}".')
