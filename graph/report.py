from graph.choices import GENDER

POP_PER_100K = 'Bands per 100k people'
POP_POPULATION = 'Population'
GENDER_DISTRIBUTION = 'Gender distribution ({} artists from {} countries)\n'


class CountryReport:
    """A CountryReport stores information for a country which can be printed on a CLI or exported to a CSV file. A
        constructor allows creation. Everything else but a function to get the amount of people of a certain gender is
        internal.

        We store e.g. the amount of bands and artists and the number of countries they are from plus a gender breakdown
        of all artists. Artists are not filtered through their origin. Any artists linked to a band will be counted.
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
        for genre in genres:
            self._genres.append((genre[0], genre[1], (genre[1] / self._number_bands) * 100))

    def _set_genders(self, genders: dict):
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
        return self._genders[gender_key][0]

    # Handles invalid populations.
    def _get_population(self):
        if str(self._population).isdigit():
            return f'    {POP_POPULATION}: {self._population:,}\n'
        else:
            return f'    {POP_POPULATION}: {self._population}\n'

    # Handles invalid populations.
    def _get_pop_per_100k(self):
        if str(self._bands_per_100k).isalpha():
            return f'    {POP_PER_100K}: {self._bands_per_100k}\n'
        else:
            return f'    {POP_PER_100K}: {self._bands_per_100k:.2f}%\n'

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
    def __init__(self, band_count, genders, artist_count, artists_per_country):
        self._band_count = band_count
        self._genders = {}
        self._country_reports = []
        self._genres = {}
        self._amount_artists = 0
        self._artists_per_country = []

        for gender in genders:
            self._amount_artists += genders[gender]
            self._genders[gender] = (genders[gender], (genders[gender] / artist_count) * 100)
            self._artists_per_country = artists_per_country

    def add_country_report(self, report: CountryReport):
        self._country_reports.append(report)

    def __str__(self):
        report = f'Database report for {len(self._country_reports)} countries. {self._amount_artists} artists from '
        report += f'{len(self._artists_per_country)} countries play in {self._band_count} bands.\n'
        report += f'  Gender distribution for entire database:\n'

        country_report_str = ''

        for country_report in self._country_reports:
            country_report_str += str(country_report)

        for gender, value_pair in self._genders.items():
            report += f'    {GENDER[gender]}: {value_pair[0]} ({value_pair[1]:.2f}%)\n'

        # print(f'{len(bands_all)} bands play {len(genres)} genres. Note that a genre like "Atmospheric Black Metal" is '
        #       f'counted as both "Atmospheric Black" and "Black."')
        # print('Displaying MA\'s core genres (in relation to all bands):')

        return report + country_report_str
