from pathlib import Path

REG_NORDIC = ("NC", "Nordic Countries", ["DK", "SE", "NO", "IS", "FI", "GL", "FO", "AX", "SJ"])
REG_TST = ("TST", "Test", ["IS", "GL", "FO", "AX", "SJ"])
REGIONS = {
    REG_NORDIC[0]: REG_NORDIC,
    REG_TST[0]: REG_TST
}

# Hardcoded file paths for the countries.
COUNTRY_FILE_PATH = Path('iso_countries.csv')


def load_data_file(file_name: Path, value_column, key_column=0):
    """Loads two columns of a CSV into a lookup table (dictionary).

    :param file_name: Path object for the file to be loaded.
    :param value_column: The column number which will be used as value.
    :param key_column: The column from which the value will be read. Standard is the first column (0).
    :return: A dict with key/value pairs.
    """
    collection = {}
    file = file_name.open(encoding="utf-8")
    line = file.readline().rstrip()

    while line is not "":
        split_line = line.split(';')
        collection[split_line[key_column]] = split_line[value_column]
        line = file.readline().rstrip()

    return collection


# Bootstrap data.
COUNTRY_NAMES = load_data_file(COUNTRY_FILE_PATH, 1)
COUNTRY_POPULATION = load_data_file(COUNTRY_FILE_PATH, 2)
