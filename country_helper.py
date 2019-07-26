from pathlib import Path

# Hardcoded file paths for the countries.
COUNTRY_NAMES_FILE_PATH = Path('countries.csv')
COUNTRY_POPULATION_FILE_PATH = Path('populations.csv')


def load_data_file(file_name):
    """Loads a CSV into a lookup table (dictionary).

    :param file_name:
    :return:
    """
    collection = {}
    file = file_name.open(encoding="utf-8")
    line = file.readline().rstrip()

    while line is not "":
        split_line = line.split(';')
        collection[split_line[0]] = split_line[1]
        line = file.readline().rstrip()

    return collection


# Bootstrap data.
COUNTRY_NAMES = load_data_file(COUNTRY_NAMES_FILE_PATH)
COUNTRY_POPULATION = load_data_file(COUNTRY_POPULATION_FILE_PATH)
