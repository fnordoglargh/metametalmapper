from abc import ABC, abstractmethod
from export_data import ExportData
from global_helpers import *


def get_file_path(name: str, sub_folder: str, extension: str):
    """Helper function to create off the shelf Path objects to export data. Data is always exported into the folder
        FOLDER_REPORTS. The complete path to a file may look like "exports/name_timestamp.extension".

    :param name: Name of the category of date you want to to safe. Empty strings will be overridden with
        "no_name_given".
    :param sub_folder: The given sub folder will be created if it does not exist and is used on top of the
        FOLDER_REPORTS.
    :param extension: Name of the file extension. A dot will be provided if it's missing.
    :return: A ready made Path object to safe data in.
    """
    if len(name) is 0:
        name = 'no_name_given'

    if len(sub_folder) is 0:
        name = 'no_sub_folder_given'

    if len(extension) > 0 and extension[0] != '.':
        extension = f'.{extension}'

    return Path(f'{FOLDER_REPORTS}/{sub_folder}/{name}_{get_time_stamp()}{extension}')


class ExportingStrategy(ABC):
    def __init__(self, name):
        self.name = name
        self.folder = Path(f'{FOLDER_REPORTS}/{name}')
        logger = logging.getLogger('ExportingStrategy')
        # Check folder existence, try to create them otherwise.

        if not self.folder.exists() and not self.folder.is_dir():
            try:
                self.folder.mkdir()
                logger.info(f'Successfully created the directory {self.folder}.')
            except:
                logger.fatal(f'Creation of the directory {self.folder} failed.')
                sys.exit(3)
        else:
            logger.debug(f'Reports directory {self.folder} exists.')


    @abstractmethod
    def do_export(self, export_data: ExportData) -> list:
        pass

    def generate_file_name(self, category, extension):
        return get_file_path(category, self.name, extension)

