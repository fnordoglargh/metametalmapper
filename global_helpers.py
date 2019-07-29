from pathlib import Path

LINK_EXTENSION = ".lnks"
BAND_LINK_FILE_NAME = "bands-{}" + LINK_EXTENSION

FOLDER_LINKS = Path("links")
FOLDER_DB = Path("databases")
FOLDERS_MAIN = [FOLDER_LINKS, FOLDER_DB]

REG_NORDIC = ("NC", "Nordic Countries", ["DK", "SE", "NO", "IS", "FI", "GL", "FO", "AX", "SJ"])
REG_TST = ("TST", "Test", ["IS", "GL", "FO", "AX", "SJ"])
REGIONS = {
    REG_NORDIC[0]: REG_NORDIC,
    REG_TST[0]: REG_TST
}


def get_dict_key(source_dict, value):
    return list(source_dict.keys())[list(source_dict.values()).index(value)]
