from exporter_strategy import ExportingStrategy
from export_data import *
from country_helper import COUNTRY_NAMES


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
