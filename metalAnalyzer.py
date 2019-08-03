from collections import OrderedDict
from graph.implNeoModel import *
from country_helper import *

style_later = "(later)"
style_early = "(early)"

POP_PER_100K = 'Bands per 100k people'
POP_POPULATION = 'Population'
POP_BANDS = 'Bands'


def calc_bands_per_pop(country_short):
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


def prettify_calc_result(calc_dict):
    pretty_string = ""
    for inner_key, inner_value in calc_dict.items():
        pretty_string += f'  {inner_key}\n'
        for outer_key, outer_value in inner_value.items():
            pretty_string += f'    {outer_key}: {outer_value}\n'

    return pretty_string[:-1]


def raw_analysis():
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


def style_stripper(style):
    if style_later in style:
        style = style[0:style.find(style_later)].rstrip()
    elif style_early in style:
        style = style[0:style.find(style_early)].rstrip()

    return style


def analyse_band_genres(bands_database):
    genres = {}
    longest_genre = 0

    for band_id, band_data in bands_database.items():
        for genre in band_data["genre"]:
            genre_clean = style_stripper(genre)

            if genre_clean not in genres:
                genres[genre_clean] = 1
            else:
                genres[genre_clean] += 1

            if len(genre_clean) > longest_genre:
                longest_genre = len(genre_clean)

    length_genre_count = 0

    for genre_id, genre_count in genres.items():
        # I know a solution using log 10 would be faster. This is good enough for he lengths we will get here.
        temp_length = len(str(genre_count))

        if temp_length > length_genre_count:
            length_genre_count = temp_length

    # We're going to enclose the number in parentheses: Add two to the count.
    length_genre_count += 2

    print("{} bands play {} distinct genres.".format(str(len(bands_database)), str(len(genres))))
    format_genre = "  {:" + str(
        longest_genre) + "} {:>" + str(length_genre_count) + "}: {:.2f}% of genres, {:.2f}% of bands."
    genres_sorted = OrderedDict(sorted(genres.items(), key=lambda t: t[1], reverse=True))

    for genre_id, genre_count in genres_sorted.items():
        percentage_of_genre = 100 * genre_count / len(genres)
        percentage_of_bands = 100 * genre_count / len(bands_database)
        print(format_genre.format(genre_id, "(" + str(genre_count) + ")", percentage_of_genre, percentage_of_bands))
