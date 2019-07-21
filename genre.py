from pathlib import Path
import json

genres_file_path = Path('genres.json')


def load_genres():
    """Loads the JSON genre cache from disk or returns an empty dict if there is no cache yet.

    :return: A dictionary with keys of all known genre strings and as value a list of all genres.
    """
    if not genres_file_path.exists():
        return dict()
    else:
        genre_string = genres_file_path.read_text(encoding="utf-8")
        return json.loads(genre_string)


# Bootstrap: Call your own loading function.
GENRE_CACHE = load_genres()
# Known strings we want cut from the end of genre.
GENRE_BLACKLIST = ['(early)', '(mid)', '(later)', 'Metal']
# Hardcoded dict of all known genres considered on the MA page https://www.metal-archives.com/browse/genre.
# The key is used up to look up the fitting genre string as on above page.
GENRE_CORE = {
    'Black': 'Black',
    'Death': 'Death',
    'Doom': 'Doom/Stoner/Sludge',
    'Stoner': 'Doom/Stoner/Sludge',
    'Sludge': 'Doom/Stoner/Sludge',
    'Electronic': 'Electronic/Industrial',
    'Industrial': 'Electronic/Industrial',
    'Experimental': 'Experimental/Avant-garde',
    'Avant-garde': 'Experimental/Avant-garde',
    'Folk': 'Folk/Viking/Pagan',
    'Viking': 'Folk/Viking/Pagan',
    'Pagan': 'Folk/Viking/Pagan',
    'Gothic': 'Gothic',
    'Grindcore': 'Grindcore',
    'Groove': 'Groove',
    'Heavy': 'Heavy',
    'Metalcore': 'Metalcore/Deathcore',
    'Deathcore': 'Metalcore/Deathcore',
    'Power': 'Power',
    'Progressive': 'Progressive',
    'Speed': 'Speed',
    'Symphonic': 'Symphonic',
    'Thrash': 'Thrash'
}


def split_genres(genre_string):
    """Takes any genre string of an band entry on MA and separates the genres into a list. We always cut trailing
        strings defined in GENRE_BLACKLIST.

    :param genre_string: A string with genres. Could be something really simple like 'Black Metal' or more complex like
        'Experimental Black Metal/Dark Ambient'. From the latter we extract: 'Experimental Black', 'Black',
        'Experimental/Avant-garde', 'Dark Ambient'. See the test for more examples.
    :return: A list of all genres detected in the given genre_string.
    """
    if genre_string in GENRE_CACHE:
        return GENRE_CACHE[genre_string]

    genre_list = []
    split_genres_1st = genre_string.split(', ')

    for outer_genre in split_genres_1st:
        split_genres_2nd = outer_genre.split('/')
        for inner_genre in split_genres_2nd:
            temp = inner_genre
            for blacked in GENRE_BLACKLIST:
                position = temp.find(blacked)
                if position > 0:
                    if position + len(blacked) != len(temp):
                        print()
                    else:
                        temp = temp[:position].rstrip()
            if temp not in genre_list:
                genre_list.append(temp)
                for key, value in GENRE_CORE.items():
                    if key in temp and value not in genre_list:
                        genre_list.append(value)

    GENRE_CACHE[genre_string] = genre_list
    return GENRE_CACHE[genre_string]


def save_genres():
    actual_genre_file = open(genres_file_path, "w", encoding="utf-8")
    json_database_string = json.dumps(GENRE_CACHE)
    actual_genre_file.write(json_database_string)
    actual_genre_file.close()
