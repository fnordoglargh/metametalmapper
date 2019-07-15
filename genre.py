from pathlib import Path
import json

genres_file_path = Path('genres.json')


def load_genres():
    if not genres_file_path.exists():
        return dict()
    else:
        genre_string = genres_file_path.read_text(encoding="utf-8")
        return json.loads(genre_string)


GENRE_CACHE = load_genres()
GENRE_BLACKLIST = ['(early)', '(mid)', '(later)', 'Metal']


def split_genres(genre_string):
    if genre_string in GENRE_CACHE:
        return GENRE_CACHE[genre_string]

    genre_list = []
    split_genres_1st = genre_string.split(', ')

    for outer_genre in split_genres_1st:
        split_genres_2nd = outer_genre.split('/')
        for inner_genre in split_genres_2nd:
            temp = inner_genre
            for blacked in GENRE_BLACKLIST:
                if inner_genre.find(blacked) > 0:
                    temp = temp[:temp.find(blacked)].rstrip()
            if temp not in genre_list:
                genre_list.append(temp)

    GENRE_CACHE[genre_string] = genre_list
    return GENRE_CACHE[genre_string]


def save_genres():
    actual_genre_file = open(genres_file_path, "w", encoding="utf-8")
    json_database_string = json.dumps(GENRE_CACHE)
    actual_genre_file.write(json_database_string)
    actual_genre_file.close()
