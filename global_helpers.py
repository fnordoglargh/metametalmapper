from pathlib import Path

LINK_EXTENSION = ".lnks"
BAND_LINK_FILE_NAME = "bands-{}" + LINK_EXTENSION

FOLDER_LINKS = Path("links")
FOLDER_DB = Path("databases")
FOLDER_EXPORTS = Path("exports")
FOLDERS_MAIN = [FOLDER_LINKS, FOLDER_DB, FOLDER_EXPORTS]


def get_dict_key(source_dict, value):
    """Gets the key for a given value from a dict.

    :param source_dict: The dict for which we want the key.
    :param value: The value which is searched for in the dict.
    :return: The key for the provided value.
    """
    return list(source_dict.keys())[list(source_dict.values()).index(value)]
