from exporter_strategy import ExportingStrategy
from export_data import *
from country_helper import COUNTRY_NAMES


class ExporterRaw(ExportingStrategy):
    def do_export(self, export_data: ExportData):

        # Export formation CSV.
        text = 'Year,Totals,'
        totals = []

        for country, country_data in export_data.country_data.items():
            text += f'{COUNTRY_NAMES[country]},'

        text += '\n'

        for i in range(export_data._formation_year_min, datetime.today().year):
            text += f'{i},'

            if i in export_data.formation_year_totals.keys():
                text += f'{export_data.formation_year_totals[i]},'
            else:
                text += f'0,'

            for country_data in export_data.country_data.values():
                if i in country_data.formation_years.keys():
                    text += f'{country_data.formation_years[i]},'
                else:
                    text += '0,'
            text += '\n'

