"""Implements helper functions to make programming meta_metal_mapper easier."""

from pathlib import Path
from datetime import datetime
import logging.config
import sys

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2023, Martin Woelke'
__version__ = '0.97.8'
__status__ = 'Development'

LINK_EXTENSION = ".lnks"
BAND_LINK_FILE_NAME = "{}" + LINK_EXTENSION

FOLDER_LINKS = Path("links")
FOLDER_LINKS_MISSING = Path("links_missing")
FOLDER_LINKS_INVALID = Path("links_invalid")
FOLDER_DB = Path("databases")

FOLDER_REPORTS = Path("reports")
FOLDER_EXPORTS = Path("exports")
FOLDERS_MAIN = [FOLDER_LINKS, FOLDER_LINKS_MISSING, FOLDER_LINKS_INVALID, FOLDER_DB, FOLDER_EXPORTS, FOLDER_REPORTS]


def get_export_path(name: str, extension: str):
    """Helper function to create off the shelf Path objects to export data. Data is always exported into the folder
        FOLDER_EXPORTS. The complete path to a file may look like "exports/name_timestamp.extension".

    :param name: Name of the category of date you want to safe. Empty strings will be overridden with
        "no_name_given".
    :param extension: Name of the file extension. A dot will be provided if it's missing.
    :return: A ready-made Path object to safe data in.
    """
    if len(name) == 0:
        name = 'no_name_given'

    if len(extension) > 0 and extension[0] != '.':
        extension = f'.{extension}'

    return Path(f'{FOLDER_EXPORTS}/{name}_{get_time_stamp()}{extension}')


def get_time_stamp():
    """Makes a timestamp e.g. to be used for file names. The format is "YYYY-MM-DD_hhmmss" and may look like
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
    if string == '':
        genitive_text = string
    elif string[-1] == 's' or string[-1] == 'x' or string[-1] == 'z':
        genitive_text = f"{string}'"
    else:
        genitive_text = f"{string}'s"

    return genitive_text
