from collections import defaultdict

from exporter_strategy import ExportingStrategy
from export_data import ExportData
from country_helper import COUNTRY_TO_REGIONS, COUNTRY_NAMES, COUNTRY_POPULATION
from graph.choices import GENDER
from settings import YEAR_REPORT

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2021, Martin Woelke'


class ExporterMarkdown(ExportingStrategy):
    def __init__(self):
        super().__init__('markdown')

    def do_export(self, export_data: ExportData):
        texts = defaultdict(str)
        texts['world'] = f'# Summary {YEAR_REPORT}\n\n'

        number_people = 0

        for population in COUNTRY_POPULATION.values():
            number_people += int(population)

        number_artists = 0
        gender_totals = {}

        for gender in GENDER.keys():
            gender_totals[gender] = 0

        for country, gender_info in export_data.genders_country.items():
            number_artists += gender_info.totals

            for gender, number in gender_info.genders.items():
                gender_totals[gender] += number

        # ISO codes of countries without metal bands.
        missing_countries_short = COUNTRY_NAMES - COUNTRY_TO_REGIONS.keys()
        missing_countries_names = []

        for country in missing_countries_short:
            missing_countries_names.append(COUNTRY_NAMES[country])

        missing_countries_names = sorted(missing_countries_names)

        texts['world'] += f'Approximately {number_people/1000000000:.3f} billion people lived on earth that year. ' \
                          f'{export_data.bands_total} bands hail from {len(export_data.country_data)} countries. '
        texts['world'] += f'No metal bands are known in {len(missing_countries_names)} (out of {len(COUNTRY_NAMES)}) ' \
                          'countries.\n\n'

        texts['world'] += '# Gender Overview\n\n' \
                          f'The {number_artists} people who played in metal bands consist of:\n\n'

        for gender, number in gender_totals.items():
            texts['world'] += f'* {GENDER[gender]}: {number} ({number/number_artists*100:.2f}%)\n'

        texts['world'] += '# Countries without metal bands\n\n'

        for country in missing_countries_names:
            texts['world'] += f'  * {country}\n'
        # Write metal world.
        file_name = self.generate_file_name('world', 'md')
        file_name.write_text(texts['world'], encoding='utf-8')
        self.logger.info(f'World report saved under: {file_name}')

