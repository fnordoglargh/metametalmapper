"""Provides a list of regions and bootstraps itself. Note that it will also exit any program importing it if the
    essential iso_countries.csv is not found inside ./data or ../data!
"""

from pathlib import Path

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2020, Martin Woelke'

REG_NC = ('NCO', 'Nordic Countries', ['DK', 'SE', 'NO', 'IS', 'FI', 'GL', 'FO', 'AX', 'SJ'])
REG_SCA = ('SCA', 'Scandinavia',  ['DK', 'SE', 'NO', 'IS', 'FI', 'FO', 'AX'])

# Europe's region definitions: https://en.wikipedia.org/wiki/Central_Europe#/media/File:Grossgliederung_Europas-en.svg
REG_EUR_NORTH = ('NEU', 'Northern Europe', ['DK', 'SE', 'NO', 'IS', 'FI'])
# Isle of Man (IM) and Guernsey (GG) can be seen as part of WEU.
REG_EUR_WEST = ('WEU', 'Western Europe', ['BE', 'FR', 'IE', 'MC', 'NL', 'GB', 'MC', 'AD', 'GG', 'IM'])
REG_EUR_CENTRAL = ('CEU', 'Central Europe', ['AT', 'CZ', 'DE', 'HU', 'LI', 'PL', 'SK', 'CH', 'LU', 'EE', 'LV', 'LT',
                                             'HR', 'SI'])
REG_EUR_SOUTH = ('SEU', 'Southern Europe', ['PT', 'ES', 'IT', 'SM', 'MT'])
REG_EUR_EAST = ('EEU', 'Eastern Europe', ['AT', 'BY', 'RU'])
# As of Nov 2019: No Bands in Kosovo.
REG_EUR_SOUTH_EAST = ('SEE', 'Southeastern Europe', ['RO', 'MD', 'BG', 'RS', 'BA', 'MK', 'GR', 'ME', 'AL', 'CY'])
REG_EURO = ('EURO', 'Europe', list(set(REG_EUR_NORTH[2] + REG_EUR_WEST[2] + REG_EUR_CENTRAL[2] + REG_EUR_SOUTH[2] +
                                       REG_EUR_EAST[2] + REG_EUR_SOUTH_EAST[2])))

REG_AMC_NORTH = ('NAM', 'North America', ['US', 'CA', 'MX', 'PR', 'TC', 'AG', 'BS', 'BB', 'BZ', 'CR', 'CU', 'DM', 'DO',
                                          'SV', 'GD', 'GT', 'HT', 'HN', 'JM', 'NI', 'PA', 'KN', 'LC', 'VC', 'TT'])
REG_AMC_CENTRAL = ('CAM', 'Central America', ['BZ', 'CR', 'SV', 'GT', 'HN', 'NI', 'PA'])
# Curaçao and Aruba are technically part of the Netherlands but geographically should be part of SAM.
REG_AMC_SOUTH = ('SAM', 'South America', ['AR', 'BO', 'BR', 'CL', 'CO', 'EC', 'GY', 'PY', 'PE', 'SR', 'UY', 'VE', 'CW',
                                          'AW'])
REG_AMS = ('AMS', 'Americas', list(set(REG_AMC_CENTRAL[2] + REG_AMC_NORTH[2] + REG_AMC_SOUTH[2])))

# As of Nov 2019: No bands in TL (Timor Leste).
REG_ASE = ('ASE', 'South East Asia', ['BN', 'KH', 'ID', 'LA', 'MY', 'MM', 'PH', 'SG', 'TH', 'VN'])
# As of Nov 2019: No bands in Bhutan and Pakistan.
REG_ASA = ('ASA', 'South Asia', ['AF', 'BD', 'IN', 'MV', 'NP', 'LK'])
REG_ACA = ('ACA', 'Central Asia', ['KZ', 'KG', 'TJ', 'TM', 'UZ'])
# Will there ever be metal in North Korea?
REG_AEA = ('AEA', 'East Asia', ['CN', 'JP', 'MN', 'KR', 'TW'])
# As of Nov 2019: No bands in Palestine and Yemen.
REG_AWA = ('AWA', 'Western Asia', ['AM', 'AZ', 'BH', 'CY', 'EG', 'GE', 'IR', 'IQ', 'IL', 'JO', 'KW', 'LB', 'OM', 'QA',
                                   'SA', 'SY', 'TR', 'AE'])
REG_ASIA = ('ASIA', 'Asia', list(set(REG_ASE[2] + REG_ASA[2] + REG_ACA[2] + REG_AEA[2] + REG_AWA[2])))

# As of Dec 2019: No bands in Fiji (FJ), Papua New Guinea (PG), Solomon Islands (SB) and Vanuatu (VU).
REG_AAS = ('AAS', 'Australasia', ['AU', 'NZ', 'NC'])
# As of Dec 2019: No bands in Fiji (FJ), Kiribati (KI), Marshall Islands (MH), Micronesia (FM), Nauru (NR), Palau (PW),
# Papua New Guinea (PG), Samoa (WS), Solomon Islands (SB), Tonga (TO), Tuvalu (TV) and Vanuatu (VU).
REG_OCE = ('OCE', 'Oceania', ['PF', 'ID', 'AU', 'NZ', 'NC', ])

# As of Dec 2019: No bands in Benin (BJ), Burkina Faso (BF), Burundi (BI), Cameroon (CM), Cape Verde (CV), Central
# African Republic (CF), Chad (TD), Comoros (KM), DR Congo (CD), Congo (CG), Ivory Coast (CI), Djibouti (DJ), Equatorial
# Guinea (GQ), Eritrea (ER), Eswatini (SZ), Gabon (GA), The Gambia (GM), Ghana (GH), Guinea (GN), Guinea-Bissau (GW),
# Lesotho (LS), Liberia (LR), Malawi (MW), Mali (ML), Mauritania (MR), Niger (NE), Nigeria (NG), Rwanda (RW), São Tomé
# and Príncipe (ST), Senegal (SN), Seychelles (SC), Sierra Leone (SL), Somalia (SO), South Sudan (SS), Tanzania (TZ),
# Togo (TG), Zambia (ZM).
REG_AFR = ('AFR', 'Africa', ['DZ', 'AO', 'BW', 'EG', 'ET', 'KE', 'LY', 'MG', 'MU', 'MA', 'MZ', 'NA', 'ZA', 'TN', 'UG',
                             'ZW'])

REG_TST = ('TST', 'Test', ['IS', 'GL', 'FO', 'AX', 'SJ'])

REGIONS = {
    REG_NC[0]: REG_NC,
    REG_SCA[0]: REG_SCA,
    REG_EUR_NORTH[0]: REG_EUR_NORTH,
    REG_EUR_WEST[0]: REG_EUR_WEST,
    REG_EUR_CENTRAL[0]: REG_EUR_CENTRAL,
    REG_EUR_EAST[0]: REG_EUR_EAST,
    REG_EUR_SOUTH[0]: REG_EUR_SOUTH,
    REG_EUR_SOUTH_EAST[0]: REG_EUR_SOUTH_EAST,
    REG_EURO[0]: REG_EURO,
    REG_AMC_NORTH[0]: REG_AMC_NORTH,
    REG_AMC_CENTRAL[0]: REG_AMC_CENTRAL,
    REG_AMC_SOUTH[0]: REG_AMC_SOUTH,
    REG_AMS[0]: REG_AMS,
    REG_ASE[0]: REG_ASE,
    REG_ASA[0]: REG_ASA,
    REG_ACA[0]: REG_ACA,
    REG_AEA[0]: REG_AEA,
    REG_AWA[0]: REG_AWA,
    REG_ASIA[0]: REG_ASIA,
    REG_AAS[0]: REG_AAS,
    REG_OCE[0]: REG_OCE,
    REG_AFR[0]: REG_AFR,
    REG_TST[0]: REG_TST
}

# Hardcoded file paths for the countries.
COUNTRY_FILE_PATH = Path('data/iso_countries.csv')

if not COUNTRY_FILE_PATH.exists():
    # Unit Test
    COUNTRY_FILE_PATH = Path('../data/iso_countries.csv')
    if not COUNTRY_FILE_PATH.exists():
        # Bail out.
        print(f'{COUNTRY_FILE_PATH} cannot be found. Bailing Out...')
        exit(-10)


def load_data_file(file_name: Path, value_column, key_column=0):
    """Loads two columns of a CSV into a lookup table (dictionary).

    :param file_name: Path object for the file to be loaded.
    :param value_column: The column number which will be used as value.
    :param key_column: The column from which the value will be read. Standard is the first column (0).
    :return: A dict with key/value pairs or an empty dict if the file was not readable.
    """
    collection = {}
    file = file_name.open(encoding='utf-8')
    line = file.readline().rstrip()

    while line is not '':
        split_line = line.split(';')
        collection[split_line[key_column]] = split_line[value_column]
        line = file.readline().rstrip()

    return collection


# Bootstrap data.
COUNTRY_NAMES = load_data_file(COUNTRY_FILE_PATH, 1)
COUNTRY_POPULATION = load_data_file(COUNTRY_FILE_PATH, 2)


def print_countries(columns_count: int, country_links):
    """Uses `crawl_countries` to get a list of all available countries and their ISO codes from MA. The list is then
    used to prepare a formatted printable string with all countries.

    :param columns_count: The amount of columns for the formatted printout. The column width depends on the length
    of the longest country name. An amount of three or four should work fine.
    :param country_links: A list of ISO country shorts.
    :return: A string with all ISO country codes and their names neatly formatted in columns.
    """
    if columns_count < 1:
        print('Cannot list countries with columns count smaller than one. Defaulting to one.')
        columns_count = 1

    longest_country = 0

    for key, value in COUNTRY_NAMES.items():
        if len(value) > longest_country and key in country_links:
            longest_country = len(value)

    line_format = '[{}] {:' + str(longest_country) + '}'
    counter = 0
    country_text = '    '

    for key, country_name in COUNTRY_NAMES.items():
        if key in country_links:
            country_text += line_format.format(key, country_name)
            counter += 1
            if counter is columns_count:
                counter = 0
                country_text += '\n    '

    return country_text


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


def clean_short_links(unclean_shorts: str):
    """Splits a string at every comma, removes all whitespaces and tests the resulting ISO country shorts for existence.

    :param unclean_shorts: A comma separated string with ISO country shorts.
    :return: A list of valid countries from the given string.
    """
    not_yet_clean_short_links = unclean_shorts.upper().replace(' ', '').split(',')

    cleaned_short_links = []

    for short in not_yet_clean_short_links:
        if short in REGIONS.keys():
            region_elements = REGIONS[short][2]
            for country in region_elements:
                cleaned_short_links.append(country)
        elif short in COUNTRY_NAMES.keys():
            cleaned_short_links.append(short)
        else:
            if short is not '':
                print(f'Ignoring {short}; not found in countries or regions.')

    return cleaned_short_links


def split_locations(locations: str):
    """Determines and returns the first city or city/state pair it finds.

    Takes the first city or city/state pair it can find in the provided string and returns it in a two element list.
    The hierarchy normally goes from a semicolon separating early and later locations to a comma to separate cities and
    states to a slash as the weakest to be a kind of 'and' for cities.

    :param locations: An untreated string that is expected to contain a pair of values, a city and a state in the
    country of origin. It gets complicated from there on.
    :return: A List containing at least one empty string (in case of errors). If the first element is not an empty
    string or "N/A", it's guaranteed to be a city. If followed by a second element it is (should be) a state or territory.
    """
    cleaned_locations = []

    # Early return if the string is empty.
    if locations is '':
        cleaned_locations.append('')
        return cleaned_locations
    elif locations == 'N/A':
        cleaned_locations.append('N/A')
        return cleaned_locations

    search_early = '(early)'
    search_mid = '(mid)'
    search_later = '(later)'
    # Always contains at least one element.
    split_locs = locations.split(';')

    # Only consider the first item.
    cleaned_pair = []
    city_state_pair = split_locs[0].split(',')
    cities = city_state_pair[0].split('/')

    # Only take the first city.
    city = cities[0].strip().rstrip()

    if search_early in city:
        early_idx = city.index(search_early)
        cleaned_pair.append(city[:early_idx - 1])
    elif search_mid in city or search_later in city:
        # Not needed (yet).
        pass
    else:
        cleaned_pair.append(city)

    if len(city_state_pair) > 1:
        cleaned_state = city_state_pair[1].strip().rstrip()
        # Might still contain an 'early'.
        if search_early in cleaned_state:
            early_idx = cleaned_state.index(search_early)
            cleaned_state = cleaned_state[:early_idx - 1]
        elif search_mid in city or search_later in city:
            # Not needed.
            pass

        # There still might be something messed up in the hierarchy (see test case #5). Just ignore it.
        cleaned_state = cleaned_state.split('/')[0].rstrip().strip()

        # In some cases the band's origin is in more than one country. M-A does not support that natively so users
        # enter location strings like 'Lisbon, Portugal / Sollentuna, Sweden (early)'. In this case we only take
        # 'Lisbon' and throw the rest away. See test case #7.
        if cleaned_state not in COUNTRY_NAMES.values():
            cleaned_pair.append(cleaned_state)

    # The city cannot contain any invalid letters because of the three splits (first ';', then ',', and last ';').
    # The state is split by '/'. This guarantees both strings not containing any of these letter.
    return cleaned_pair
