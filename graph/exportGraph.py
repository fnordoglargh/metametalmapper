from abc import ABCMeta, abstractmethod
from pathlib import Path
import logging
from global_helpers import FOLDER_EXPORTS
from datetime import datetime
from graph.metalGraph import POP_BANDS, POP_PER_100K, POP_POPULATION, RAW_GENRES, POP_COUNTRY


def prettify_calc_result(calc_dict: dict) -> str:
    """Prettifies the raw data from the dict returned by calc_bands_per_pop.

    :param calc_dict: Takes a dict with the format supplied by calc_bands_per_pop.
    :return: A string representation of the given dict.
    """
    pretty_string = ''
    indentation_1 = '  '
    indentation_2 = '    '

    if len(calc_dict) is 0:
        return pretty_string

    for inner_key, inner_value in calc_dict.items():
        if inner_key == POP_COUNTRY:
            indent = indentation_1
        else:
            indent = indentation_2

        pretty_string += f'{indent}{inner_key}: {inner_value}\n'

    return pretty_string[:-1]


class GraphExportContext:

    def __init__(self, strategy):
        self._strategy = strategy

    def export_graph(self, export_data):
        self._strategy.export_graph_interface(export_data)

    def export_csv(self, statistics):
        self._strategy.export_csv_interface(statistics)


class GraphExportStrategy(metaclass=ABCMeta):

    @abstractmethod
    def export_graph_interface(self, db_handle):
        pass

    @abstractmethod
    def export_csv_interface(self, statistics):
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
            elif '\'' in band_name:
                band_name = band_name.replace('\'', '&apos;')
            elif '"' in band_name:
                band_name = band_name.replace('"', '&quot;')

            export_file.write(
                f'<node id="n{node}"><data key="d0">{band_name}</data>'
                f'<data key="d1">{payload["country"]}</data></node>\n'
            )

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

    def export_csv_interface(self, statistics: dict):
        raw_data = statistics['raw_data']
        number_bands = statistics['number_bands']
        number_countries = statistics['number_countries']

        print(f'This raw analysis contains data of {number_bands} bands from {number_countries} countries.')

        # Prepare the genres by adding all known genres in a dictionary.
        genres = {}

        for calc_result in raw_data:
            print(prettify_calc_result(calc_result))
            for genre, count in calc_result[RAW_GENRES].items():
                if genre not in genres.keys():
                    genres[genre] = count
                else:
                    genres[genre] += count

        genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
        print(f'{number_bands} bands play {len(genres)} genres. Note that a genre like "Atmospheric Black Metal" is '
              f'counted as both "Atmospheric Black" and "Black."')
        print('Displaying MA\'s core genres (in relation to all bands):')

        for genre in genres:
            percentage = (genre[1] / number_bands) * 100
            print(f'  {genre[0]}: {genre[1]} ({percentage:.2f}%)')

        number_artists = statistics['number_artists']
        artist_per_country = statistics['artist_per_country']
        print(f'The database contains {number_artists} artists from {len(artist_per_country)} countries.')

        # for key, value in GENDER.items():
        #     artist_gender = Member.nodes.filter(gender__exact=key)
        #     percentage = (len(artist_gender) / amount_artists) * 100
        #     print(f'  {len(artist_gender)} ({percentage:.2f}%) artists are {value}.')

