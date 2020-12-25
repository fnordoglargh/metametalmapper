"""Implements helper functions to make programming meta_metal_mapper easier."""

from pathlib import Path
from datetime import datetime
from exporting import FOLDER_EXPORTS

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2020, Martin Woelke'
__version__ = '0.97.5'
__status__ = 'Development'

LINK_EXTENSION = ".lnks"
BAND_LINK_FILE_NAME = "{}" + LINK_EXTENSION

FOLDER_LINKS = Path("links")
FOLDER_LINKS_MISSING = Path("links_missing")
FOLDER_LINKS_INVALID = Path("links_invalid")
FOLDER_DB = Path("databases")

FOLDER_REPORTS = Path("reports")
FOLDERS_MAIN = [FOLDER_LINKS, FOLDER_LINKS_MISSING, FOLDER_LINKS_INVALID, FOLDER_DB, FOLDER_EXPORTS, FOLDER_REPORTS]


def get_time_stamp():
    """Makes a timestamp e.g. to be used for file names. The format format is "YYYY-MM-DD_hhmmss" and may look like
        "2019-08-17_125427".

    :return: A string timestamp of the described format.
    """
    actual_time = datetime.now()
    return f'{actual_time.date()}_{actual_time.time().strftime("%H%M%S")}'


def get_dict_key(source_dict, value):
    """Gets the key for a given value from a dict.

    :param source_dict: The dict for which we want the key.
    :param value: The value which is searched for in the dict.
    :return: The key for the provided value.
    """
    return list(source_dict.keys())[list(source_dict.values()).index(value)]


def append_genitive_s(string: str):
    """Appends an "'s" to any string if it is not empty and an "'" if it already ends with an "s".

    :param string: The string to be converted to genitive.
    :return: The converted string. Stays empty if string was empty.
    """
    if string is '':
        genitive_text = string
    elif string[-1] is 's' or string[-1] is 'x' or string[-1] is 'z':
        genitive_text = f"{string}'"
    else:
        genitive_text = f"{string}'s"

    return genitive_text
