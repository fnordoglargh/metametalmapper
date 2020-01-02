"""Some helper functions needed in several places.
"""

from pathlib import Path
from datetime import datetime

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019, Martin Woelke'

LINK_EXTENSION = ".lnks"
BAND_LINK_FILE_NAME = "{}" + LINK_EXTENSION

FOLDER_LINKS = Path("links")
FOLDER_DB = Path("databases")
FOLDER_EXPORTS = Path("exports")
FOLDER_REPORTS = Path("reports")
FOLDERS_MAIN = [FOLDER_LINKS, FOLDER_DB, FOLDER_EXPORTS, FOLDER_REPORTS]


def get_time_stamp():
    """Makes a timestamp e.g. to be used for file names. The format format is "YYYY-MM-DD_hhmmss" and may look like
        "2019-08-17_125427".

    :return: A string timestamp of the described format.
    """
    actual_time = datetime.now()
    return f'{actual_time.date()}_{actual_time.time().strftime("%H%M%S")}'


def get_export_path(name: str, extension: str):
    """Helper function to create off the shelf Path objects to export data. Data is always exported into the folder
        FOLDER_EXPORTS. The complete path to a file may look like "exports/name_timestamp.extension".

    :param name: Name of the category of date you want to to safe. Empty strings will be overridden with
        "no_name_given".
    :param extension: Name of the file extension. A dot will be provided if it's missing.
    :return: A ready made Path object to safe data in.
    """
    if len(name) is 0:
        name = 'no_name_given'

    if len(extension) > 0 and extension[0] != '.':
        extension = f'.{extension}'

    return Path(f'{FOLDER_EXPORTS}/{name}_{get_time_stamp()}{extension}')


def get_dict_key(source_dict, value):
    """Gets the key for a given value from a dict.

    :param source_dict: The dict for which we want the key.
    :param value: The value which is searched for in the dict.
    :return: The key for the provided value.
    """
    return list(source_dict.keys())[list(source_dict.values()).index(value)]


def escape_band_names(unclean_band_name):
    """Removes (some) XML/HTML control characters from the band name.

    :param unclean_band_name: The band name which may be invalid for XML/HTML exports.
    :return: A clean and valid band name.
    """
    clean_band_name = unclean_band_name

    if '&' in clean_band_name:
        clean_band_name = clean_band_name.replace('&', '&amp;')
    elif '\'' in clean_band_name:
        clean_band_name = clean_band_name.replace('\'', '&apos;')
    elif '"' in clean_band_name:
        clean_band_name = clean_band_name.replace('"', '&quot;')

    return clean_band_name
