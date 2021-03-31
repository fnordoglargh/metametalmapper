from pathlib import Path
from exporter_strategy import ExportingStrategy
from export_data import *
from country_helper import COUNTRY_NAMES
from genre import GENRE_CORE_MA
from settings import RELEASE_TYPES_REVIEW, RELEASE_AVERAGE_MIN, RELEASE_REVIEW_COUNT_MIN

REPORT_TEMPLATE = Path('data/report.tpl')


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


def _export_country_table(country_data: Dict[str, CountryData], genders_country, genres):
    """Generates a CSV string of country reports which contains the key information of the evaluated countries. It lists
        country name, population, number of bands, bands per 100k people, artist breakdown with total numbers and
        percentages. The last column contains the most popular metal genre.

    :param country_data: Prepared country data.
    :param genders_country: Prepped country gender data.
    :param genres: Genres on a per country basis.
    :return: A CSV string of the converted data, ready to be saved into a file.
    """
    # Determine existing gender keys first. We want to use what we have and not all possible entries.
    gender_keys = []
    for export_data in genders_country.values():
        for gender_key in export_data.genders.keys():
            if gender_key not in gender_keys:
                gender_keys.append(gender_key)

    # Prep the header.
    export_text = 'Country;Population;# Bands;Bands per 100k;# Artists;'
    for gender in gender_keys:
        export_text += f'# {GENDER[gender]};% {GENDER[gender]};'
    export_text += 'TOP genre;\n'

    for country, data_entry in country_data.items():
        export_text += f'{data_entry.country_name};{COUNTRY_POPULATION[country]};{data_entry.number_bands};'
        export_text += f'{data_entry.bands_per_100k:.2f};{genders_country[country].totals};'
        for gender in gender_keys:
            actual_number = 0
            actual_percentage = 0
            if gender in genders_country[country].genders:
                actual_number = genders_country[country].genders[gender]
                actual_percentage = genders_country[country].percentages[gender] * 100
            export_text += f'{actual_number};{actual_percentage:.2f};'
        top_genre = max(genres[country], key=genres[country].get)
        export_text += f'{top_genre};\n'
    return export_text


def _get_releases_per_year(releases):
    # Sorted by year (descending).
    sorted_releases = dict(sorted(releases.items(), reverse=True))
    sorting = {}

    for year, release_types in sorted_releases.items():
        sorting[year] = {}

        for release_type in RELEASE_TYPES_REVIEW:
            sorting[year][release_type] = []

        for release_type, releases in release_types.items():
            sorted_type = []

            # The raw report is not interested in previously filtered items.
            for release in releases:
                if not release.is_filtered:
                    sorted_type.append(release)

            sorting[year][release_type] = sorted(sorted_type, key=lambda x: x.rating, reverse=True)

    return sorting


def _get_release_csv(sorted_releases):
    csv_releases = 'Year;'

    for release_type in RELEASE_TYPES_REVIEW:
        csv_releases += f'{RELEASE_TYPES[release_type]};'

    csv_releases += '\n'

    for year, release_types in sorted_releases.items():
        csv_releases += f'{year};'
        longest_category = 1

        for release_type in RELEASE_TYPES_REVIEW:
            category_length = len(release_types[release_type])
            if category_length > longest_category:
                longest_category = category_length

        for i in range(0, longest_category):
            for release_type in RELEASE_TYPES_REVIEW:
                if len(release_types[release_type]) < longest_category:
                    csv_releases += ';'
                else:
                    actual_release = release_types[release_type][i]
                    csv_releases += f'{actual_release.release_name} ({actual_release.rating}%) by {actual_release.band_name};'

            csv_releases += '\n;'

        csv_releases = csv_releases[:-1]

    return csv_releases


def _get_releases_ordered(sorted_releases):
    releases_all = {}

    for releases_types in sorted_releases.values():
        for release_type, releases in releases_types.items():
            if release_type not in releases_all:
                releases_all[release_type] = []

            releases_all[release_type] += releases
            releases_all[release_type] = sorted(releases_all[release_type], key=lambda x: x.rating, reverse=True)

    export_string = '{ '

    for release_type, releases in releases_all.items():
        export_string += f'"{RELEASE_TYPES[release_type]}": [ '
        counter = 1
        last_used_number = 0
        # No release can be better than 100%. But it ensures that the conditions inside the loop works even if the
        # first ratings value is 100.
        last_rating = 101

        for release in releases:
            # As soon as the rating is different from the last, we save the rating and increment the rank counter.
            if release.rating < last_rating:
                last_rating = release.rating
                last_used_number = counter

            # TODO: Move this hotfix to data entry.
            release_name = release.release_name.replace('"', '&quot;')
            export_string += f'{{ "release_name": "{release_name}", "link": "{release.link}", '
            export_string += f'"ratings": "{release.rating}", "band_name": "{release.band_name}", '
            export_string += f' "rank": {last_used_number} }}, '
            counter += 1

        export_string = export_string[:-2]
        export_string += '], '

    export_string = export_string[:-2]
    export_string += '}'

    return export_string


def _get_release_per_year_json(sorted_releases):
    # Define valid release types for functionality using the JSON export.
    workable_types = []
    for release_type in RELEASE_TYPES_REVIEW:
        workable_types.append(RELEASE_TYPES[release_type])

    export_string = '[{"categories": ['

    for release_type in RELEASE_TYPES_REVIEW:
        export_string += f'"{RELEASE_TYPES[release_type]}", '

    export_string = export_string[:-2]
    export_string += ']}'

    for year, releases_types in sorted_releases.items():
        # Double curly brace for escaping.
        export_string += f', {{"year": "{year}", '

        for release_type, releases in releases_types.items():
            export_string += f'"{RELEASE_TYPES[release_type]}": ['
            for release in releases:
                # TODO: Move this hotfix to data entry.
                release_name = release.release_name.replace('"', '&quot;')
                export_string += f'{{"name": "{release_name}", "band": "{release.band_name}",'
                export_string += f'"rating": "{release.rating}", "link": "{release.link}"}}, '

            if len(releases) > 0:
                export_string = export_string[:-2]

            export_string += '], '
        export_string = export_string[:-2]
        export_string += '}'
    export_string += ']'

    return export_string


def _generate_html_report(report_locations: list):
    """ Generates an HTML report from a template with pre-generated JSON data.

    Loads a HTML template and replaces markers with given JSON data.

    :param report_locations: A list of tuples (JSON string and marker name).
    :return: The HTML report as a string.
    """

    template_text = REPORT_TEMPLATE.read_text(encoding="utf-8")

    for data_tuple in report_locations:
        template_text = template_text.replace(data_tuple[1], data_tuple[0])

    return template_text


def _export_releases(releases):
    # Sorted by year (descending).
    sorted_releases = _get_releases_per_year(releases)
    release_csv = _get_release_csv(sorted_releases)
    release_json_year = _get_release_per_year_json(sorted_releases)
    releases_all = _get_releases_ordered(sorted_releases)
    return release_csv, release_json_year, releases_all


class ExporterRaw(ExportingStrategy):

    def __init__(self):
        super().__init__('raw')

    def do_export(self, export_data: ExportData):
        self.logger.info('')
        self.logger.info('Exporting data:')
        formation_csv = _export_formation_table(export_data.country_data,
                                                export_data.formation_year_totals,
                                                export_data.formation_year_min)
        file_name = self.generate_file_name('formation_data', 'csv')
        file_name.write_text(formation_csv, encoding='utf-8')
        self.logger.info(f'  Formation data (per year and country): {file_name}')

        # We get a tuple with two csv strings from the genre function.
        genre_tables = _export_core_genre_table(export_data.genres)
        file_name = self.generate_file_name('genres', 'csv')
        file_name.write_text(genre_tables[0], encoding='utf-8')
        self.logger.info(f'  All recorded genres (per country): {file_name}')
        file_name = self.generate_file_name('genres_core', 'csv')
        file_name.write_text(genre_tables[1], encoding='utf-8')
        self.logger.info(f'  Core genres (per country): {file_name}')

        # Prepare and export country statistics.
        country_table = _export_country_table(export_data.country_data, export_data.genders_country, export_data.genres)
        file_name = self.generate_file_name('countries', 'csv')
        file_name.write_text(country_table, encoding='utf-8')
        self.logger.info(f'  Basic statistics (per country): {file_name}')

        # Prepare and export release statistics.
        exported_releases = _export_releases(export_data.releases)
        file_name = self.generate_file_name('releases_per_year', 'csv')
        file_name.write_text(exported_releases[0], encoding='utf-8')
        self.logger.info(f'  All releases (per year with at least {RELEASE_REVIEW_COUNT_MIN} '
                         f'reviews and a min. average rating of {RELEASE_AVERAGE_MIN}%):')
        self.logger.info(f'    CSV: {file_name}')

        # Write JSON exports.
        file_name = self.generate_file_name('releases_per_year', 'json')
        file_name.write_text(exported_releases[1], encoding='utf-8')
        self.logger.info(f'    JSON: {file_name}')

        file_name = self.generate_file_name('releases_all', 'json')
        file_name.write_text(exported_releases[2], encoding='utf-8')
        self.logger.info(f'    JSON: {file_name}')

        # Use JSON strings for teh HTML exports.
        html_text = _generate_html_report([
            (exported_releases[1], 'marker_releases_year'),
            (exported_releases[2], 'marker_releases_all')
        ])
        file_name = self.generate_file_name('release_report', 'html')
        file_name.write_text(html_text, encoding='utf-8')
        self.logger.info(f'    HTML: {file_name}')

