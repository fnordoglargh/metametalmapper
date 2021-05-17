from exporter_strategy import ExportingStrategy
from export_data import ExportData
from settings import FILTER_UNCONNECTED, FIND_MA_INCONSISTENCIES

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2021, Martin Woelke'


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


class ExporterGraphML(ExportingStrategy):
    def __init__(self):
        super().__init__('graphml')

    def do_export(self, export_data: ExportData):
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

        export_text = header

        footer = (
            f'</graph>\n'
            f'</graphml>'
        )

        filtered_nodes = []

        # Go through collection once to create nodes.
        for node, payload in export_data.band_network.items():
            if FILTER_UNCONNECTED and len(payload['relations']) is 0:
                pass
            else:
                band_name = escape_band_names(payload['name'])

                export_text += f'<node id="n{node}"><data key="d0">{band_name}</data>'
                export_text += f'<data key="d1">{payload["country"]}</data></node>\n'

        # Keeps track of connections we already made so that no two nodes are connected more than once.
        connections_made = {}
        counter = 0

        # Only in a second run we write the connections. This might seem odd, but Cytoscape does not like the
        # connections mixed with the nodes.
        for node, payload in export_data.band_network.items():
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
                if relation not in export_data.band_network and not FIND_MA_INCONSISTENCIES:
                    continue
                elif relation not in connections_made:
                    connections_made[relation] = []

                # Test if a connection already exists.
                if relation in connections_made[node] or node in connections_made[relation]:
                    pass
                else:
                    connections_made[node].append(relation)
                    connections_made[relation].append(node)
                    export_text += f'<edge id="e{counter}" source="n{node}" target="n{relation}"/>\n'
                    counter += 1

        export_text += footer

        file_name = self.generate_file_name('band_network', 'graphml')
        file_name.write_text(export_text, encoding='utf-8')
        self.logger.info(f'Band network saved under: {file_name}')
