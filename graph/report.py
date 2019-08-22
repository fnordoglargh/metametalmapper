from graph.choices import GENDER


class DatabaseReport:
    def __init__(self):
        self.genders = {}

        for gender in GENDER:
            self.genders[gender] = 0

        self.country_reports = {}


class CountryReport:
    def __init__(self, country_name, population, number_bands):
        self.country_name = country_name
        self.population = population

        self.bands_per_100k = number_bands / (int(population) / 100000)
