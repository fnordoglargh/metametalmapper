from graph.implNeoModel import *
from country_helper import *

POP_PER_100K = 'Bands per 100k people'
POP_POPULATION = 'Population'
POP_BANDS = 'Bands'


def calc_bands_per_pop(country_short) -> dict:
    """Calculates the number of bands per 100k people for a given country and puts the data into a dict. The result will
        be empty for two error cases: The country population is smaller than one or if there are no bands available in
        the requested country.

    :param country_short: The country's ISO code to get the data from the database.
    :return: A dictionary with the the calculated data. Keys to data are the country short and the constants above. The
        dict will be empty for the above described error cases.
    """
    result = {}
    bands = Band.nodes.filter(country__exact=country_short)

    if len(bands) is 0:
        return result

    population = COUNTRY_POPULATION[country_short]

    if int(population) <= 1:
        return result

    country_long = COUNTRY_NAMES[country_short]
    result[country_long] = {}
    result[country_long][POP_BANDS] = str(len(bands))
    result[country_long][POP_POPULATION] = population
    bands_per_100k = len(bands) / (int(population) / 100000)
    result[country_long][POP_PER_100K] = f'{bands_per_100k:.2f}'

    return result


def prettify_calc_result(calc_dict) -> str:
    """Prettifies the raw data from the dict returned by calc_bands_per_pop.

    :param calc_dict: Takes a dict with the format supplied by calc_bands_per_pop.
    :return: A string representation of the given dict.
    """
    pretty_string = ""

    for inner_key, inner_value in calc_dict.items():
        pretty_string += f'  {inner_key}\n'
        for outer_key, outer_value in inner_value.items():
            pretty_string += f'    {outer_key}: {outer_value}\n'

    return pretty_string[:-1]


def raw_analysis():
    """Prints some raw analysis of the entire database to the std out: The amount of bands and artists and the number of
        countries they are from plus a gender breakdown of all artists.
    """
    print('Prepping bands.')
    bands = Band.nodes.all()
    band_per_country = []
    calc_results = []

    for band in bands:
        if band.country not in band_per_country:
            band_per_country.append(band.country)
            calc_results.append(calc_bands_per_pop(band.country))

    print(f'The database contains {len(bands)} bands from {len(band_per_country)} countries.')

    for calc_result in calc_results:
        print(prettify_calc_result(calc_result))

    print('Prepping artists.')
    all_artists = Member.nodes.all()
    amount_artists = len(all_artists)
    artist_per_country = []

    for artist in all_artists:
        if artist.origin not in artist_per_country:
            artist_per_country.append(artist.origin)

    print(f'The database contains {amount_artists} artists from {len(artist_per_country)} countries.')

    for key, value in GENDER.items():
        artist_gender = Member.nodes.filter(gender__exact=key)
        percentage = (len(artist_gender) / amount_artists) * 100
        print(f'  {len(artist_gender)} ({percentage:.2f}%) artists are {value}.')
