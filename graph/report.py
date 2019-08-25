from graph.choices import GENDER
from country_helper import COUNTRY_NAMES, COUNTRY_POPULATION

POP_PER_100K = 'Bands per 100k people'
POP_POPULATION = 'Population'
GENDER_DISTRIBUTION = 'Gender distribution ({} artists from {} countries)\n'


def get_percentage_string(dividend, divisor):
    """Prepares a string with a number and a percentage (in parenthesis) for a given value pair.

    :param dividend: Dividend for percentage calculation.
    :param divisor: Divisor for percentage calculation.
    :return: A string based on given values in the format "dividend (percentage%)" with two digits. The string will be
        empty for invalid value pairs (e.g. divisor is zero or any value is smaller than zero).
    """
    if divisor is 0 or divisor * dividend < 0:
        return ""
    else:
        percentage = (dividend / divisor) * 100
        return f'{dividend} ({percentage:.2f}%)'


class CountryReport:
    def __init__(self, country_name, population, number_bands, genders, gender_per_country, genres):
        self._country_name = country_name
        self._population = int(population)
        self._number_bands = number_bands
        self._bands_per_100k = number_bands / (int(population) / 100000)
        self._genders = {}
        self._amount_people = 0
        self._set_genders(genders)
        self._gender_per_country = gender_per_country
        self._genres = genres

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

    def __str__(self):
        if len(self._genders) == 0:
            return "Invalid Country Report: Genders not set."

        report = f'  {self._country_name}\n' \
                 f'    {POP_POPULATION}: {self._population:,}\n' \
                 f'    Bands: {self._number_bands}\n' \
                 f'    {POP_PER_100K}: {self._bands_per_100k:.2f}\n' \
                 f'    {GENDER_DISTRIBUTION.format(self._amount_people, len(self._gender_per_country))}'

        for gender, value_pair in self._genders.items():
            report += f'      {GENDER[gender]}: {value_pair[0]} ({value_pair[1]:.2f}%)\n'

        return report


class DatabaseReport:
    def __init__(self):
        self.genders = {}

        for gender in GENDER:
            self.genders[gender] = 0

        self.country_reports = {}
        self.genres = {}
    #
    # def add_country(self, report: CountryReport):
    #     for gender, count in report.genders:
    #         self.genders[gender] += report.genders[gender]
    #
    # def init_country(self, country_short):
    #     if country_short not in COUNTRY_NAMES:
    #         return None
    #
    #     self.country_reports[country_short] = \
    #         CountryReport(COUNTRY_NAMES[country_short], COUNTRY_POPULATION[country_short], -1)
    #
    # def add_genders(self, country_short, genders: dict):
    #     if country_short not in COUNTRY_NAMES:
    #         return None

    def __str__(self):
        report = f'Database report for {len(self.country_reports)} countries.\n'
        gender_total = {}
        country_report_str = ''
        amount_artists = 0
        gender_per_country = {}

        for gender in GENDER:
            gender_total[gender] = 0

        for country_name, country_report in self.country_reports.items():
            country_report_str += str(country_report)

            for key, count in country_report._gender_per_country.items():
                if key not in gender_per_country.keys():
                    gender_per_country[key] = 0

                gender_per_country[key] += country_report._gender_per_country[key]

            for key in gender_total.keys():
                gender_total[key] += country_report._genders[key][0]
                amount_artists += country_report._genders[key][0]

        report += f'  {GENDER_DISTRIBUTION.format(amount_artists, len(gender_per_country))}'

        for gender, count in gender_total.items():
            report += f'    {GENDER[gender]}: {get_percentage_string(count, amount_artists)}\n'

        return report + country_report_str


