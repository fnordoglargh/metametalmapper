from abc import ABCMeta, abstractmethod
import logging
from settings import FILTER_UNCONNECTED, FIND_MA_INCONSISTENCIES

from global_helpers import get_export_path
from genre import GENRE_CORE_MA, GENRE_CORE_MAP

""" Prototype of a key node which can be completed with a format() call to enter the number for the `id` property
    and the attribute's name."""
genre_key_element = '<key id="d{}" for="node" attr.name="{}" attr.type="bool"><default>false</default></key>\n'


def escape_band_names(unclean_band_name):
    """Removes (some) XML/HTML control characters from the band name.

    :param unclean_band_name: The band name which may be invalid for XML/HTML exports.
    :return: A clean and valid band name.
    """
    clean_band_name = unclean_band_name

    if '&' in clean_band_name:
        clean_band_name = clean_band_name.replace('&', '&amp;')
    elif '\'' in clean_band_name:
        clean_band_name = clean_band_name.replace('\'', '&apos;')
    elif '"' in clean_band_name:
        clean_band_name = clean_band_name.replace('"', '&quot;')

    return clean_band_name


class GraphExportContext:

    def __init__(self, strategy):
        self._strategy = strategy

    def export_graph(self, export_data):
        self._strategy.export_graph_interface(export_data)


class GraphExportStrategy(metaclass=ABCMeta):

    @abstractmethod
    def export_graph_interface(self, export_data):
        """Exports a graph from given data.

        :param export_data: A dictionary with band IDs as keys and one list of band IDs as value.
        """
        pass


class GraphMLExporter(GraphExportStrategy):
    @staticmethod
    def generate_genre_keys(index_offset):
        """Generates a string (by formatting `genre_key_element`) with key nodes of all known core genres from
            `GENRE_CORE_MA`.

        :param index_offset: The index of the first `id` attribute of the new key nodes.
        :return: String of key nodes filled with genres.
        """
        genre_keys = ''

        for genre in GENRE_CORE_MA:
            genre_keys += genre_key_element.format(GENRE_CORE_MA.index(genre) + index_offset, genre)

        return genre_keys

    def __init__(self):
        self.logger = logging.getLogger('GraphMLExporter')

    def export_graph_interface(self, data_dict: dict):
        self.logger.info('Starting GraphML export to file.')
        # Indicates the starting index for the `id` attributes of the `key` nodes in the header. If you add another line
        # with an `id` property, make sure you change this to the correct number.
        index_offset = 2

        header = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<graphml xmlns="http://graphml.graphdrawing.org/xmlns"\n'
            f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
            f'xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">\n'
            f'<key id="d0" for="node" attr.name="label" attr.type="string"/>\n'
            f'<key id="d1" for="node" attr.name="country" attr.type="string"/>\n'
            f'{self.generate_genre_keys(index_offset)}'
            f'<graph id="G" edgedefault="undirected">\n'
        )

        footer = (
            f'</graph>\n'
            f'</graphml>'
        )

        db_path = get_export_path('bands', '.graphml')
        export_file = open(db_path, 'w', encoding='utf-8')
        export_file.write(header)
        filtered_nodes = []

        # Go through collection once to create nodes.
        for node, payload in data_dict.items():
            if FILTER_UNCONNECTED and len(payload['relations']) is 0:
                pass
            else:
                band_name = escape_band_names(payload['name'])
                key_element = ''

                for genre in payload['genres']:
                    if genre in GENRE_CORE_MAP.keys():
                        # First we need to get the core genre name from the lookup table GENRE_CORE_MAP
                        key_index = GENRE_CORE_MA.index(GENRE_CORE_MAP[genre]) + index_offset
                        if str(key_index) not in key_element:
                            key_element += f'<data key="d{key_index}">true</data>'

                export_file.write(
                    f'<node id="n{node}"><data key="d0">{band_name}</data>'
                    f'<data key="d1">{payload["country"]}</data>{key_element}</node>\n'
                )

        # Keeps track of connections we already made so that no two nodes are connected more than once.
        connections_made = {}
        counter = 0

        # Only in a second run we write the connections. This might seem odd, but Cytoscape does not like the
        # connections mixed with the nodes.
        for node, payload in data_dict.items():
            if FILTER_UNCONNECTED and len(payload['relations']) is 0:
                pass
            else:
                # Add an empty list for the actual ID (node).
                if node not in connections_made:
                    connections_made[node] = []

            for relation in payload['relations']:
                # Check if the relation is valid for this export. E.g. While exporting a Norwegian-only graph,
                # every other country is invalid. Another special case is inconsistencies in raw data; one relation is
                # reported as core member and another is a live member.
                if relation not in data_dict and not FIND_MA_INCONSISTENCIES:
                    continue
                elif relation not in connections_made:
                    connections_made[relation] = []

                # Test if a connection already exists.
                if relation in connections_made[node] or node in connections_made[relation]:
                    pass
                else:
                    connections_made[node].append(relation)
                    connections_made[relation].append(node)
                    export_file.write(f'<edge id="e{counter}" source="n{node}" target="n{relation}"/>\n')
                    counter += 1

        export_file.write(footer)
        export_file.close()
        self.logger.info(f'Band network available as "{db_path}".')
