from pathlib import Path

REG_NC = ("NCO", "Nordic Countries", ["DK", "SE", "NO", "IS", "FI", "GL", "FO", "AX", "SJ"])
REG_SCA = ("SCA", "Scandinavia",  ["DK", "SE", "NO", "IS", "FI", "FO", "AX"])
REG_EUR_WEST = ("WEU", "Western Europe", ["BE", "FR", "IE", "LU", "MC", "NL", "GB"])
REG_EUR_CENTRAL = ("CEU", "Central Europe", ["AT", "CZ", "DE", "HU", "LI", "PL", "SK", "CH"])

REG_AMC_NORTH = ("NAM", "North America", ["US", "CA", "MX", "PR", "TC", "AG", "BS", "BB", "BZ", "CR", "CU", "DM", "DO", "SV", "GD", "GT", "HT", "HN", "JM", "NI", "PA", "KN", "LC", "VC", "TT"])
REG_AMC_CENTRAL = ("CAM", "Central America", ["BZ", "CR", "SV", "GT", "HN", "NI", "PA"])
REG_AMC_SOUTH = ("SAM", "South America", ["AR", "BO", "BR", "CL", "CO", "EC", "GY", "PY", "PE", "SR", "UY", "VE"])
REG_AMC = ("AMC", "Americas", list(set(REG_AMC_CENTRAL[2] + REG_AMC_NORTH[2] + REG_AMC_SOUTH[2])))

# As of Nov 2019: No bands in TL (Timor Leste).
REG_ASE = ("ASE", "South East Asia", ["BN", "KH", "ID", "LA", "MY", "MM", "PH", "SG", "TH", "VN"])
# As of Nov 2019: No bands in Bhutan and Pakistan.
REG_ASA = ("ASA", "South Asia", ["AF", "BD", "IN", "MV", "NP", "LK"])
REG_ACA = ("ACA", "Central Asia", ["KZ", "KG", "TJ", "TM", "UZ"])
# Will there ever be metal in North Korea?
REG_AEA = ("AEA", "East Asia", ["CN", "JP", "MN", "KR", "TW"])
# As of Nov 2019: No bands in Palestine and Yemen.
REG_AWA = ("AWA", "Western Asia", ["AM", "AZ", "BH", "CY", "EG", "GE", "IR", "IQ", "IL", "JO", "KW", "LB", "OM", "QA", "SA", "SY", "TR", "AE"])
REG_ASIA = ("ASIA", "Asia", list(set(REG_ASE[2] + REG_ASA[2] + REG_ACA[2] + REG_AEA[2] + REG_AWA[2])))

REG_TST = ("TST", "Test", ["IS", "GL", "FO", "AX", "SJ"])

REGIONS = {
    REG_NC[0]: REG_NC,
    REG_SCA[0]: REG_SCA,
    REG_EUR_WEST[0]: REG_EUR_WEST,
    REG_EUR_CENTRAL[0]: REG_EUR_CENTRAL,
    REG_AMC_NORTH[0]: REG_AMC_NORTH,
    REG_AMC_CENTRAL[0]: REG_AMC_CENTRAL,
    REG_AMC_SOUTH[0]: REG_AMC_SOUTH,
    REG_AMC[0]: REG_AMC,
    REG_ASE[0]: REG_ASE,
    REG_ASA[0]: REG_ASA,
    REG_ACA[0]: REG_ACA,
    REG_AEA[0]: REG_AEA,
    REG_AWA[0]: REG_AWA,
    REG_ASIA[0]: REG_ASIA,
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


def print_countries(columns_count, country_links):
    """Uses ``crawl_countries`` to get a list of all available countries and their ISO codes from MA. The list is then
    used to prepare a formatted printable string with all countries.

    :param columns_count: The amount of columns for the formatted printout. The column width depends on the length
    of the longest country name. A count of three or four should work fine.
    :param country_links:
    :return: A string with all ISO country codes and their names neatly formatted in columns.
    """
    if type(columns_count) is not int:
        print("Cannot list countries with parameter type other than int.")
        return
    elif columns_count < 1:
        print("Cannot list countries with columns count smaller than one. Defaulting to one.")
        columns_count = 1

    longest_country = 0

    for key, value in COUNTRY_NAMES.items():
        if len(value) > longest_country and key in country_links:
            longest_country = len(value)

    line_format = "[{}] {:" + str(longest_country) + "}"
    counter = 0
    actual_line = "    "

    for key, country_name in COUNTRY_NAMES.items():
        if key in country_links:
            actual_line += line_format.format(key, country_name)
            counter += 1
            if counter is columns_count:
                counter = 0
                actual_line += '\n    '

    return actual_line


def print_regions():
    """Prepares a string with all known regions from inside this file and their countries.

    :return: String with all regions and their containing countries.
    """
    lines = ''
    for key, value in REGIONS.items():
        lines += f'  [{value[0]}] {value[1]}: '
        for country_key in value[2]:
            lines += COUNTRY_NAMES[country_key] + ', '
        lines = lines[0:lines.rfind(',')]
        lines += '\n'

    return lines
