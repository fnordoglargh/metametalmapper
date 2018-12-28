from collections import OrderedDict

style_later = "(later)"
style_early = "(early)"


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
