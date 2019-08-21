from graph.choices import GENDER


class DatabaseReport:
    def __init__(self):
        self.genders = {}

        for gender in GENDER:
            self.genders[gender] = 0


class CountryReport:
    def __init__(self, country_name):
        self.country_name = country_name
