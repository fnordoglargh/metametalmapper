"""Classes to export data into different formats."""
from enum import Enum
from pathlib import Path
from global_helpers import get_time_stamp

FOLDER_EXPORTS = Path("exports")


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


class ExportMode(Enum):
    Raw = 0
    Markdown = 1
