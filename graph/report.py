from graph.choices import GENDER

POP_PER_100K = 'Bands per 100k people'
POP_POPULATION = 'Population'


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
        self.population = population
        self.bands_per_100k = number_bands / (int(population) / 100000)
        self.genders = {}

        for gender in GENDER:
            self.genders[gender] = 0

        self.genres = {}

    def __str__(self):
        report = f'  {self.country_name}\n' \
                 f'    {POP_POPULATION}: {self.population}\n' \
                 f'    {POP_PER_100K}: {self.bands_per_100k}\n'

        return report


