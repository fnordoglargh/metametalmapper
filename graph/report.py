from collections import defaultdict
from graph.choices import GENDER, RELEASE_TYPES
from global_helpers import get_export_path
from genre import GENRE_CORE_MA
from settings import RELEASE_AVERAGE_MIN, RELEASE_REVIEW_COUNT_MIN

POP_PER_100K = 'Bands per 100k people'
POP_POPULATION = 'Population'
GENDER_DISTRIBUTION = 'Gender distribution ({} artists from {} countries)\n'


class CountryReport:
    """A CountryReport stores information for a country which can be printed on a CLI or exported to a CSV file. A
        constructor allows creation. Everything else but a function to get the amount of people of a certain gender is
        internal.

        We store e.g. the amount of bands and artists and the number of countries they are from plus a gender breakdown
        of all artists. Artists are not filtered through their origin. Any artists linked to a band will be counted.

        A word on genres: A band which plays 'Atmospheric Black Metal' has the genre string dissected into both
        'Atmospheric Black' and 'Black'. This is especially important for counting against the core genres of MA. See
        genre.py for details.
    """
    def __init__(self, country_name, population, number_bands, genders, gender_per_country, genres):
        self._country_name = country_name
        self._population = int(population)
        self._number_bands = number_bands

        # Special case handling for countries like "International" (XX) which have -1 as population.
        if self._population <= 1:
            self._bands_per_100k = 'NA'
            self._population = 'NA'
        else:
            self._bands_per_100k = number_bands / (int(population) / 100000)

        self._genders = {}
        self._amount_people = 0
        self._set_genders(genders)
        # A dictionary with a ISO country name as key and the amount of people from that country as value.
        self._gender_per_country = gender_per_country
        self._genres = []
        self._set_genres(genres)

    def _set_genres(self, genres: list):
        """Internal function used by the constructor to set genres and calculate their percentages in relation to the
            number of bands in the given country.

        :param genres: List of tuples with a genre and the number of bands which play it.
        """

        for genre in genres:
            self._genres.append((genre[0], genre[1], (genre[1] / self._number_bands) * 100))

    def _set_genders(self, genders: dict):
        """Internal function used by the constructor to set the genders.

        :param genders: A dictionary with genders and the number of people of that gender for bands of the given
            country.
        """
        self._amount_people = 0
        for gender in genders.keys():
            self._amount_people += genders[gender]

        if self._amount_people == 0:
            return None

        for gender in GENDER:
            self._genders[gender] = ()

        for gender, count in genders.items():
            # Fill with value pairs count and the percentage.
            self._genders[gender] = (count, (count / self._amount_people) * 100)

    def get_gender(self, gender_key):
        """Gets the countries gender tuple for the given gender key.

        :param gender_key: The gender key. See GENDER for possible values.
        :return: A tuple with three values; The gender string, number of people in the given country belonging to that
            gender and a percentage in relation to the total number of people playing in bands of this country.
        """
        return self._genders[gender_key][0]

    def get_genres(self):
        return self._genres

    def _get_population(self):
        """Returns a string for the str() method which handles the formatting of valid populations (inserts comma for
            thousands-separator) and simply prints the 'NA' of invalid values.

        :return: A perfectly formatted population string used internally by the str() method.
        """
        if str(self._population).isdigit():
            return f'    {POP_POPULATION}: {self._population:,}\n'
        else:
            return f'    {POP_POPULATION}: {self._population}\n'

    def _get_pop_per_100k(self):
        """Returns a string for the str() method which handles the formatting of valid values for the number of bands
            per 100k people (rounds to two digits) and simply prints 'NA' for invalid values.

        :return: A perfectly formatted population per 100k people string used internally by the str() method.
        """
        if str(self._bands_per_100k).isalpha():
            return f'    {POP_PER_100K}: {self._bands_per_100k}\n'
        else:
            return f'    {POP_PER_100K}: {self._bands_per_100k:.2f}\n'

    def _get_csv_gender_data(self):
        gender_csv = ''

        for gender in self._genders:
            gender_csv += f'{self._genders[gender][0]};{self._genders[gender][1]:.2f};'

        return gender_csv

    @staticmethod
    def get_csv_header():
        return 'Country;Population;Bands;Bands per 100k;# Total;# Male;% Male;# Female;% Female;# Unknown;% Unknown;' \
               'TOP genre\n'

    def get_csv_data(self):
        export_data = f'{self._country_name};{self._population};{self._number_bands};'

        if str(self._bands_per_100k).isalpha():
            export_data += f'{self._bands_per_100k}'
        else:
            export_data += f'{self._bands_per_100k:.2f}'

        export_data += f';{self._amount_people};{self._get_csv_gender_data()}{self._genres[0][0]} Metal\n'

        return export_data

    def __str__(self):
        if len(self._genders) == 0:
            return "Invalid Country Report: Genders not set."

        report = f'  {self._country_name}\n'
        report += self._get_population()
        report += f'    Bands: {self._number_bands}\n'
        report += self._get_pop_per_100k()
        report += f'    {GENDER_DISTRIBUTION.format(self._amount_people, len(self._gender_per_country))}'

        for gender, value_pair in self._genders.items():
            report += f'      {GENDER[gender]}: {value_pair[0]} ({value_pair[1]:.2f}%)\n'

        top = 5

        # Make sure we only print the amount available (until maximum defined above).
        if len(self._genres) < top:
            top = len(self._genres)

        report += f'    TOP {top} Genres;\n'

        for index in range(0, top):
            report += f'      {self._genres[index][0]}: {self._genres[index][1]} ({self._genres[index][2]:.2f}%)\n'

        return report


class DatabaseReport:
    """A DatabaseReport stores the analysis of the entire database plus the attached CountryReport objects. It always
        contains e.g. the amount of _all_ artists and which genders they have.
    """
    def __init__(self, band_count, genders, artist_count, artists_per_country, genres, album_report):
        self._band_count = band_count
        self._genders = {}
        self._country_reports = []
        self._genres = []
        self._amount_artists = 0
        self._artists_per_country = []
        self.album_report = album_report

        for gender in genders:
            self._amount_artists += genders[gender]
            self._genders[gender] = (genders[gender], (genders[gender] / artist_count) * 100)
            self._artists_per_country = artists_per_country

        genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))

        for genre_name, count in genres.items():
            self._genres.append((genre_name, count, (count / band_count) * 100))

    def add_country_report(self, report: CountryReport):
        """Appends the ready made CountryReport to the DatabaseReport.

        :param report: The CountryReport to add.
        """
        self._country_reports.append(report)

    def export_csv_country(self):
        export_text = CountryReport.get_csv_header()

        for report in self._country_reports:
            export_text += report.get_csv_data()

        export_file = get_export_path('countries', 'csv')
        export_file.write_text(export_text, encoding="utf-8")

        return export_file

    def export_csv_genres(self):
        """Exports a CSV of all genres (rows) in all countries (columns).

        :return: The Path object to the saved file.
        """
        country_genres = {'Total': {}}
        genre_cache = {}

        for report in self._country_reports:
            genre_tuples = report.get_genres()
            genre_cache[report._country_name] = {}

            for genre_tuple in genre_tuples:
                # 0: Genre name
                if genre_tuple[0] not in country_genres['Total'].keys():
                    country_genres['Total'][genre_tuple[0]] = genre_tuple[1]
                else:
                    country_genres['Total'][genre_tuple[0]] += genre_tuple[1]

                genre_cache[report._country_name][genre_tuple[0]] = genre_tuple[1]

        # At this point we have a all known genres in 'Total'. Now we need to construct the rest of the table. Having
        # the cache will make that easier.
        # Sort the dict from highest to lowest amount of genres.
        country_genres['Total'] = dict(sorted(country_genres['Total'].items(), key=lambda x: x[1], reverse=True))
        # First two items of the header.
        export_all = 'Genre;Total;'

        # Add all other countries to the header. TODO: Maybe sort the countries too.
        for country in genre_cache.keys():
            export_all += f'{country};'

        # Last item of the header.
        export_all += '\n'
        export_core = export_all

        # This loop constructs the rest of the table, starting with the genre.
        for genre_name, count in country_genres['Total'].items():
            export_all += f'{genre_name};{count};'
            # Either append the number of bands playing the genre or an empty cell.
            for country in genre_cache.keys():
                if genre_name in genre_cache[country].keys():
                    export_all += f'{genre_cache[country][genre_name]};'
                else:
                    export_all += ';'

            export_all += '\n'

        export_file_all = get_export_path('genres_all', 'csv')
        export_file_all.write_text(export_all, encoding="utf-8")

        for genre_name in GENRE_CORE_MA:
            if genre_name in country_genres["Total"].keys():
                export_core += f'{genre_name};{country_genres["Total"][genre_name]};'
            else:
                export_core += f'{genre_name};;'

            for country in genre_cache.keys():
                if genre_name in genre_cache[country].keys():
                    export_core += f'{genre_cache[country][genre_name]};'
                else:
                    export_core += ';'

            export_core += '\n'

        export_file_core = get_export_path('genres_core', 'csv')
        export_file_core.write_text(export_core, encoding="utf-8")

        return export_file_all, export_file_core

    def get_csv_header(self):
        return 'Country;Population;Bands;Bands per 100k;# Male;% Male;# Female;% Female;# Unknown;% Unknown;TOP genre'

    def get_csv_data(self):
        return f''

    def __str__(self):
        report = f'Database report for {len(self._country_reports)} countries. {self._amount_artists} artists from '
        report += f'{len(self._artists_per_country)} countries play in {self._band_count} bands.\n'
        report += f'  Gender distribution for entire database:\n'

        country_report_str = ''

        for country_report in self._country_reports:
            country_report_str += str(country_report)

        for gender, value_pair in self._genders.items():
            report += f'    {GENDER[gender]}: {value_pair[0]} ({value_pair[1]:.2f}%)\n'

        report += f'  {self._band_count} bands play {len(self._genres)} genres (there are more genres than bands; a '
        report += 'band playing Atmospheric Black Metal counts as both "Atmospheric Black" and "Black"):\n'

        for genre in self._genres:
            report += f'    {genre[0]}: {genre[1]} ({genre[2]:.2f}%)\n'

        return report + country_report_str + str(self.album_report)


class AlbumReport:

    def __init__(self, workable_types):
        self.workable_types = workable_types
        self.country_releases = defaultdict(lambda: defaultdict(int))
        self.releases_total = defaultdict(int)
        self.releases_per_year = defaultdict(lambda: defaultdict(list))

    def process_release(self, country_name, band_id, band_name, release_name, release_type, year, ratings,
                        review_count):
        if ratings is -1:
            return
        if len(country_name) is 0 or len(band_name) < 1:
            return
        elif release_type not in self.workable_types:
            return

        # Collect release counts per type (and total).
        self.country_releases[country_name][release_type] += 1
        self.releases_total[release_type] += 1

        # Collect releases in a tuple. We filter by the minimum values for average percentage and review count from the
        # settings file.
        if ratings >= RELEASE_AVERAGE_MIN and review_count >= RELEASE_REVIEW_COUNT_MIN:
            self.releases_per_year[str(year)[0:4]][release_type].append((release_name, band_name, ratings))

    @staticmethod
    def get_release_tuple_string(release_tuple):
        if len(release_tuple) is 3:
            return f'{release_tuple[0]} ({release_tuple[2]}%) by {release_tuple[1]}'
        else:
            return ''

    def get_csv_header(self):
        csv_header = 'Year;'

        for release_type in self.workable_types:
            csv_header += f'{release_type};'

        csv_header += '\n'

        return csv_header

    def get_sort_key(self, item):
        return item[2]

    def export_csv_releases(self):
        export_text = self.get_csv_header()
        releases_per_year = dict(sorted(self.releases_per_year.items(), reverse=True))

        for year, release_types in releases_per_year.items():
            export_text += f'{year};'

            # for type

            # Types will be exported in columns. First we determine the maximum amount of elements in the largest
            # category.
            type_size = 0
            sorted_types = {}

            for release_type, releases in release_types.items():
                if len(releases) > type_size:
                    type_size = len(releases)
                sorted_types[release_type] = sorted(releases, key=self.get_sort_key, reverse=True)

            for i in range(0, type_size):
                if i > 0:
                    export_text += ';'
                # We use the workable types to check existence and control the order.
                for type_name in self.workable_types:
                    if type_name not in release_types:
                        continue

                    # Add the actual element.
                    if i < len(release_types[type_name]):
                        export_text += f'{self.get_release_tuple_string(sorted_types[type_name][i])};'
                    # Add an empty cell because there no elements anymore.
                    else:
                        export_text += ';'

                export_text += '\n'

        export_text += '\n'
        export_file = get_export_path('releases_per_year', 'csv')
        export_file.write_text(export_text, encoding="utf-8")

        return export_file

    def __str__(self):
        report = 'Release Report (percentages in relation to totals):\n  Totals\n'

        for release_type, count in self.releases_total.items():
            report += f'    {release_type}s: {count}\n'

        for country, releases in self.country_releases.items():
            report += f'  {country}\n'
            for release_type, count in releases.items():
                percentage = (count / self.releases_total[release_type]) * 100
                report += f'    {release_type}s: {count} ({percentage:.2f}%)\n'

        top = 5
        releases_per_year = dict(sorted(self.releases_per_year.items(), reverse=True))
        report += 'Best releases per year:\n'

        for year, releases in releases_per_year.items():
            top_temp = top
            if len(releases[RELEASE_TYPES['F']]) < top:
                top_temp = len(releases[RELEASE_TYPES['F']])

            # No full-length releases in this year.
            if top_temp is 0:
                continue

            sorted_releases = sorted(releases[RELEASE_TYPES["F"]], key=lambda x: x[2], reverse=True)
            report += f'  Best releases in {year} (TOP {top_temp} of {len(sorted_releases)}):\n'

            for i in range(0, top_temp):
                report += f'    {self.get_release_tuple_string(sorted_releases[i])}\n'

        return report
