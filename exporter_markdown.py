from collections import defaultdict

from exporter_strategy import ExportingStrategy
from export_data import ExportData
from country_helper import COUNTRY_TO_REGIONS, COUNTRY_NAMES


class ExporterMarkdown(ExportingStrategy):
    def __init__(self):
        super().__init__('markdown')

    def do_export(self, export_data: ExportData):
        missing_countries = sorted(COUNTRY_NAMES - COUNTRY_TO_REGIONS.keys())
        # missing_countries = COUNTRY_NAMES - export_data.country_data.keys()

        texts = defaultdict(str)
        texts['world'] = '# Countries without metal bands\n\n' \
                         f'No metal bands are known in {len(missing_countries)} (out of {len(COUNTRY_NAMES)}) ' \
                         f'countries.\n\n'

        for country in missing_countries:
            texts['world'] += f'  * {COUNTRY_NAMES[country]}\n'
        # Write metal world.
        file_name = self.generate_file_name('world', 'md')
        file_name.write_text(texts['world'], encoding='utf-8')
        self.logger.info(f'    JSON: {file_name}')

