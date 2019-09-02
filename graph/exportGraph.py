from abc import ABCMeta, abstractmethod
from pathlib import Path
import logging
from global_helpers import get_export_path
from graph.choices import GENDER
from graph.metalGraph import POP_BANDS, POP_PER_100K, POP_POPULATION, RAW_GENRES, POP_COUNTRY
from genre import GENRE_CORE


def get_genres(raw_data) -> dict:
    genres = {}

    for genre in GENRE_CORE.keys():
        pass

    return genres


class GraphExportContext:

    def __init__(self, strategy):
        self._strategy = strategy

    def export_graph(self, export_data):
        self._strategy.export_graph_interface(export_data)


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
            f'<key id="d0" for="node" attr.name="label" attr.type="string"/>\n'
            f'<key id="d1" for="node" attr.name="country" attr.type="string"/>\n'
            f'<graph id="G" edgedefault="undirected">\n'
        )

        footer = (
            f'</graph>\n'
            f'</graphml>'
        )

        db_path = get_export_path('bands', '.graphml')
        export_file = open(db_path, "w", encoding="utf-8")
        export_file.write(header)

        # Go through collection once to create nodes.
        for node, payload in data_dict.items():
            band_name = payload["name"]

            if '&' in band_name:
                band_name = band_name.replace('&', '&amp;')
            elif '\'' in band_name:
                band_name = band_name.replace('\'', '&apos;')
            elif '"' in band_name:
                band_name = band_name.replace('"', '&quot;')

            export_file.write(
                f'<node id="n{node}"><data key="d0">{band_name}</data>'
                f'<data key="d1">{payload["country"]}</data></node>\n'
            )

        # Only in a second run we write the connections. This might seem odd but Cytoscape does not like the connections
        # between the nodes.
        counter = 0

        for node, payload in data_dict.items():
            for relation in payload['relations']:
                export_file.write(f'<edge id="e{counter}" source="n{node}" target="n{relation}"/>\n')
                counter += 1

        export_file.write(footer)
        export_file.close()
        self.logger.info(f'Band network available as "{db_path}".')
