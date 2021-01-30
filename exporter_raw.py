from exporter_strategy import ExportingStrategy
from export_data import *
from country_helper import COUNTRY_NAMES


def _export_formation_table(country_data: Dict[str, CountryData], formation_year_totals, formation_year_min: int):
    sorted_countries = \
        sorted(country_data,
               key=lambda country: country_data[country].number_formation_total,
               reverse=True)

    # Export formation CSV.
    text = 'Year,Totals,'

    # Continue prepping the headings.
    for country_iso in sorted_countries:
        text += f'{COUNTRY_NAMES[country_iso]},'

    text += '\n'

    for i in range(formation_year_min, datetime.today().year):
        text += f'{i},'

        # Totals first...
        if i in formation_year_totals.keys():
            text += f'{formation_year_totals[i]},'
        else:
            text += f'0,'

        # ...then the totals from sorted country keys.
        for country_iso in sorted_countries:
            if i in country_data[country_iso].formation_years.keys():
                text += f'{country_data[country_iso].formation_years[i]},'
            else:
                text += '0,'
        text += '\n'

    return text


class ExporterRaw(ExportingStrategy):

    def __init__(self):
        super().__init__('raw')

    def do_export(self, export_data: ExportData):
        formation_csv = _export_formation_table(export_data.country_data,
                                                export_data.formation_year_totals,
                                                export_data.formation_year_min)
        file_name = self.generate_file_name('formation_data', 'csv')
        file_name.write_text(formation_csv, encoding='utf-8')
