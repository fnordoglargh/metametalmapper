from exporter_strategy import ExportingStrategy
from export_data import *
from country_helper import COUNTRY_NAMES
from genre import GENRE_CORE_MA


def _export_core_genre_table(raw_genres):
    """Generates CSV strings of the genres (rows) for all countries (columns).

    :param raw_genres: A dictionary with all genres bands of a state played.
    :return: A tuple containing two strings. The first one contains all genres and the second only the M-A "core
        genres".
    """

    # This gives us a list of
    sorted_countries = sorted(raw_genres,
                              key=lambda country_key: len(raw_genres[country_key]),
                              reverse=True)

    sorted_genres = dict(sorted(raw_genres['Total'].items(), key=lambda x: x[1], reverse=True))

    table_text = 'Genre;'
    table_text_core = 'Genre;'

    # Write the header.
    for country in sorted_countries:
        # Because I was lazy I just put 'Total' into the raw collection. This is where we need to handle it differently
        # from all other ISO country names.
        if country is not 'Total':
            table_text += f'{COUNTRY_NAMES[country]};'
            table_text_core += f'{COUNTRY_NAMES[country]};'
        else:
            table_text += 'Total;'
            table_text_core += 'Total;'

    table_text += '\n'
    table_text_core += '\n'

    for genre in sorted_genres:

        table_text += f'{genre};'

        if genre in GENRE_CORE_MA:
            table_text_core += f'{genre};'

        for country in sorted_countries:
            if genre in raw_genres[country].keys():
                table_text += f'{raw_genres[country][genre]};'
                if genre in GENRE_CORE_MA:
                    table_text_core += f'{raw_genres[country][genre]};'
            else:
                table_text += '0;'

        table_text += '\n'
        if genre in GENRE_CORE_MA:
            table_text_core += '\n'

    return table_text, table_text_core


def _export_formation_table(country_data: Dict[str, CountryData], formation_year_totals, formation_year_min: int):
    """Generates a CSV string of the formation years (rows) of bands in all countries (columns).

    :param country_data: The raw country data object.
    :param formation_year_totals: A collection with the total formation numbers per year.
    :param formation_year_min: The very first year a metal band was founded (from actual country_data and not the
        earliest known instance).
    :return: A string with the CSV data of all band formation years
    """
    sorted_countries = sorted(country_data,
                              key=lambda country: country_data[country].number_formation_total,
                              reverse=True)

    # Export formation CSV.
    formation_csv = 'Year;Totals;'

    # Continue prepping the headings.
    for country_iso in sorted_countries:
        formation_csv += f'{COUNTRY_NAMES[country_iso]};'

    formation_csv += '\n'

    for i in range(formation_year_min, datetime.today().year):
        formation_csv += f'{i};'

        # Totals first...
        if i in formation_year_totals.keys():
            formation_csv += f'{formation_year_totals[i]};'
        else:
            formation_csv += f'0;'

        # ...then the totals from sorted country keys.
        for country_iso in sorted_countries:
            if i in country_data[country_iso].formation_years.keys():
                formation_csv += f'{country_data[country_iso].formation_years[i]};'
            else:
                formation_csv += '0;'
        formation_csv += '\n'

    return formation_csv


class ExporterRaw(ExportingStrategy):

    def __init__(self):
        super().__init__('raw')

    def do_export(self, export_data: ExportData):
        formation_csv = _export_formation_table(export_data.country_data,
                                                export_data.formation_year_totals,
                                                export_data.formation_year_min)
        file_name = self.generate_file_name('formation_data', 'csv')
        file_name.write_text(formation_csv, encoding='utf-8')

        # We get a tuple with two csv strings from the genre function.
        genre_tables = _export_core_genre_table(export_data.genres)
        file_name = self.generate_file_name('genres', 'csv')
        file_name.write_text(genre_tables[0], encoding='utf-8')
        file_name = self.generate_file_name('genres_core', 'csv')
        file_name.write_text(genre_tables[1], encoding='utf-8')
