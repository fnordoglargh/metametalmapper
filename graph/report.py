from graph.choices import GENDER

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


class DatabaseReport:
    def __init__(self):
        self.genders = {}

        for gender in GENDER:
            self.genders[gender] = 0

        self.country_reports = {}
        self.genres = {}

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

            for key, count in country_report.gender_per_country.items():
                if key not in gender_per_country.keys():
                    gender_per_country[key] = 0

                gender_per_country[key] += country_report.gender_per_country[key]

            for key in gender_total.keys():
                gender_total[key] += country_report.genders[key]
                amount_artists += country_report.genders[key]

        report += f'  {GENDER_DISTRIBUTION.format(amount_artists, len(gender_per_country))}'

        for gender, count in gender_total.items():
            report += f'    {GENDER[gender]}: {get_percentage_string(count, amount_artists)}\n'

        print(gender_total)

        return report + country_report_str


class CountryReport:
    def __init__(self, country_name, population, number_bands):
        self.country_name = country_name
        self.population = int(population)
        self.number_bands = number_bands
        self.bands_per_100k = number_bands / (int(population) / 100000)
        self.genders = {}
        self.gender_per_country = {}

        for gender in GENDER:
            self.genders[gender] = 0

        self.genres = {}

    def __str__(self):
        amount_people = 0
        for gender in self.genders.keys():
            amount_people += self.genders[gender]

        report = f'  {self.country_name}\n' \
                 f'    {POP_POPULATION}: {self.population:,}\n' \
                 f'    Bands: {self.number_bands}\n' \
                 f'    {POP_PER_100K}: {self.bands_per_100k:.2f}\n' \
                 f'    {GENDER_DISTRIBUTION.format(amount_people, len(self.gender_per_country))}'

        for gender, count in self.genders.items():
            report += f'      {GENDER[gender]}: {get_percentage_string(count, amount_people)}\n'

        return report


