from graph.choices import GENDER

POP_PER_100K = 'Bands per 100k people'
POP_POPULATION = 'Population'


def get_percentage_string(dividend, divisor):
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
        report = 'Database report:\n'
        for country_name, country_report in self.country_reports.items():
            report += str(country_report)
        return report


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
                 f'    Gender distribution ({amount_people} artists from {len(self.gender_per_country)} countries)\n'

        for gender, number in self.genders.items():
            report += f'      {GENDER[gender]}: ' + get_percentage_string(number, amount_people) + '\n'

        return report


