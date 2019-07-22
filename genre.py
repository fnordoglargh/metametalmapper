from pathlib import Path
import json

# Hardcoded file path for the genre cache.
GENRES_FILE_PATH = Path('genre_cache.json')


def load_genres():
    """Loads the JSON genre cache from disk or returns an empty dict if there is no cache yet.

    :return: A dictionary with keys of all known genre strings and as value a list of all genres.
    """
    if not GENRES_FILE_PATH.exists():
        return dict()
    else:
        genre_string = GENRES_FILE_PATH.read_text(encoding="utf-8")
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

        This function is written in way that always considers the core genres of MA. A composite genre like
        'Experimental Black Metal' will be split into a list with the following genres: 'Experimental Black', 'Black'
        and 'Experimental/Avant-garde'. The first in the list is the raw extracted string. The other two are the core
        genres we deduct from the first part.

    :param genre_string: A string with genres. Could be something really simple like 'Black Metal' or more complex like
        'Experimental Black Metal/Dark Ambient'. From the latter we extract: 'Experimental Black', 'Black',
        'Experimental/Avant-garde', 'Dark Ambient'. See the test for more examples.
    :return: A list of all genres detected in the given genre_string.
    """
    # Early return if the string is cached.
    if genre_string in GENRE_CACHE:
        return GENRE_CACHE[genre_string]

    genre_list = []

    # Iterate over the split genre_string.
    for outer_genre in genre_string.split(', '):
        # Each outer_genre may consist of multiple genres (separated by a '/'). So we split those too.
        for inner_genre in outer_genre.split('/'):
            temp_genre = inner_genre
            # Remove the blacklisted strings at the end.
            for blacked in GENRE_BLACKLIST:
                position = temp_genre.find(blacked)
                #  The second condition is necessary to detect genres with a leading 'Metal' in them.
                if position > 0 and position + len(blacked) == len(temp_genre):
                    temp_genre = temp_genre[:position].rstrip()
            if temp_genre not in genre_list:
                genre_list.append(temp_genre)
                for key, value in GENRE_CORE.items():
                    # Add the value from the core genre dict if it is not already there.
                    if key in temp_genre and value not in genre_list:
                        genre_list.append(value)

    GENRE_CACHE[genre_string] = genre_list
    return genre_list


def save_genres():
    """Dumps the cache into a JSON file.
    """
    actual_genre_file = open(GENRES_FILE_PATH, "w", encoding="utf-8")
    json_database_string = json.dumps(GENRE_CACHE)
    actual_genre_file.write(json_database_string)
    actual_genre_file.close()
