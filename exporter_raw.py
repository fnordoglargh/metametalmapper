from exporter_strategy import ExportingStrategy
from export_data import *
from country_helper import COUNTRY_NAMES


class ExporterRaw(ExportingStrategy):
    def do_export(self, export_data: ExportData):

        sorted_countries = \
            sorted(export_data.country_data,
                   key=lambda country_iso: export_data.country_data[country_iso].number_formation_total,
                   reverse=True)

        # Export formation CSV.
        text = 'Year,Totals,'

        # Continue prepping the headings.
        for country_iso in sorted_countries:
            text += f'{COUNTRY_NAMES[country_iso]},'

        text += '\n'

        for i in range(export_data._formation_year_min, datetime.today().year):
            text += f'{i},'

            # Totals first...
            if i in export_data.formation_year_totals.keys():
                text += f'{export_data.formation_year_totals[i]},'
            else:
                text += f'0,'

            # ...then the totals from sorted country keys.
            for country_iso in sorted_countries:
                if i in export_data.country_data[country_iso].formation_years.keys():
                    text += f'{export_data.country_data[country_iso].formation_years[i]},'
                else:
                    text += '0,'
            text += '\n'
