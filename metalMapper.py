#!/usr/bin/python
import os
import sys
import getopt
import logging
import logging.config
import yaml
from enum import Enum
from metalCrawler import *
from metalAnalyzer import *
import json
from pathlib import Path
import pprint
import datetime

link_extension = ".lnks"
bandsListFileName = "bands" + link_extension
bandLinkFileName = "bands-{}" + link_extension

FOLDER_LINKS = Path("links")
FOLDER_DB = Path("databases")
folders = [FOLDER_LINKS, FOLDER_DB]
REG_NORDIC = ("NC", "Nordic Countries", ["DK", "SE", "NO", "IS", "FI", "GL", "FO", "AX", "SJ"])
REG_TST = ("TST", "Test", ["IS", "GL", "FO", "AX", "SJ"])
REGIONS = {REG_NORDIC[0]: REG_NORDIC,
           REG_TST[0]: REG_TST}

countries = {}


class CrawlMode(Enum):
    Error = -1
    CrawlCountry = 0
    CrawlAllCountries = 1
    CrawlBands = 2
    AnalyseDatabase = 3
    DisplayInfo = 4
    CrawlRegion = 5
    Test = 6


def load_countries():
    if len(countries) is not 0:
        return

    country_path = Path("countries.csv")

    if not country_path.is_file():
        return

    with country_path.open(encoding="utf-8") as f:
        line = f.readline().rstrip()
        while line is not "":
            split_line = line.split(';')
            countries[split_line[0]] = split_line[1]
            line = f.readline().rstrip()


def print_countries(columns):
    if type(columns) is not int:
        print("Cannot list countries with parameters type other than int.")
        return
    elif columns < 1:
        print("Cannot list countries with columns count smaller than one.")
        return

    longest_country = 0
    country_links = crawl_countries()

    for key, value in countries.items():
        if len(value) > longest_country and key in country_links:
            longest_country = len(value)

    line_format = "[{}] {:" + str(longest_country) + "}"
    counter = 0
    actual_line = "    "

    for key, country_name in countries.items():
        if key in country_links:
            actual_line += line_format.format(key, country_name)
            counter += 1
            if counter is columns:
                counter = 0
                actual_line += '\n    '

    return actual_line


def print_regions():
    lines = ''
    for key, value in REGIONS.items():
        lines += f'  [{value[0]}] {value[1]}: '
        for country_key in value[2]:
            lines += countries[country_key] + ', '
        lines = lines[0:lines.rfind(',')]
        lines += '\n'

    return lines


def print_help():
    file_name_a = bandLinkFileName.format('XX')
    # TODO: Move two letter country names to description section.
    print('Supported modes:')
    print(f'  -a: Crawls all countries for bands and saves them in files named {file_name_a}')
    print('    (where XX is the two letter short form of a given country). The files are put')
    print(f'    into sub-folder {FOLDER_LINKS}. This action can take almost 10 minutes.')
    print('  -b: Crawls all bands in the generated files from option -a')
    print('    (or -c if you specify your own file with -f).')
    print('  -c <country ID>: Crawls the supplied country (e.g. NO for Norway)')
    print('    and uses the standard file name together with the ID to write a')
    print('    file with all band links from the given country. See list below.')
    print('  -y: Prints a report about the genres of a database.')
    print('  -f <filename>: filename is a parameter to override the standard file name')
    print('    for -b or -c and is used either to write an output file or to read an')
    print('    input file.')
    print('  -l: List available countries and regions.')
    print('  -r <region ID>: Crawls a predefined region (call -l for example IDs or try NC).')


def flush_queue(country_short):
    """Flushes the contents of ``bandsQueue`` (band addresses of a country or region) into the sub-folder named
    ``links``.

    The function effectively empties the bandsQueue and leaves it with zero items for further calls of
    metalCrawler.crawl_country.

    :param country_short: ISO country code used in the file name.
    :return: A filename with the format links/bands-NN.lnks.
    """
    logger = logging.getLogger('Crawler')
    country_filename = Path(f"{FOLDER_LINKS}/bands-{country_short}{link_extension}")

    if bandsQueue.qsize() != 0:
        band_links_file = open(country_filename, "w", encoding="utf-8")
        counter = 0
        while bandsQueue.qsize() != 0:
            band_links_file.write(bandsQueue.get_nowait() + '\n')
            counter += 1
        band_links_file.close()
        logger.info(f"Saved {str(counter)} bands of {country_short} in file '{country_filename}'.")
    else:
        logger.warning(f"No bands in country {country_short}. To check country manually, use above link.")

    return country_filename


def main(argv):
    try:
        # TODO: Fix defect while using -c and -f together.
        opts, args = getopt.getopt(argv, "bac:hf:tylr:")
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    if not opts:
        print_help()
        sys.exit(0)

    with open('loggerConfig.yaml', 'r') as log_config:
        config = yaml.safe_load(log_config.read())
        logging.config.dictConfig(config)

    load_countries()

    # Change to a terminal size in which everything fits.
    os.system('mode con: cols=153 lines=9999')
    logger = logging.getLogger('MAIN')
    logger.debug('***************************************************************')
    logger.debug('Starting up...')
    mode = CrawlMode.Error
    filenames = []

    # Check necessary folders exist, try to create them otherwise.
    for folder in folders:
        if not folder.exists() and not folder.is_dir():
            try:
                folder.mkdir()
                logger.info(f"Successfully created the directory {folder}.")
            except:
                logger.fatal(f"Creation of the directory {folder} failed.")
                sys.exit(3)
        else:
            logger.debug(f"Standard directory {folder} exists.")

    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt == '-c':
            country = arg.upper()
            mode = CrawlMode.CrawlCountry
        elif opt == '-a':
            mode = CrawlMode.CrawlAllCountries
        elif opt == '-b':
            mode = CrawlMode.CrawlBands
        elif opt == '-f':
            filename = arg
            filenames.append(Path(arg))
            logger.info(f"Supplied file name: '{arg}'.")
        elif opt == '-y':
            mode = CrawlMode.AnalyseDatabase
        elif opt == '-l':
            mode = CrawlMode.DisplayInfo
        elif opt == '-r':
            mode = CrawlMode.CrawlRegion
            region = arg.upper()
        elif opt == '-t':
            mode = CrawlMode.Test
            filenames.append(Path("testLinks.txt"))
        elif opt == '-m':
            result = cut_instruments('Drums(1988-1993, 1994-present)')
            print()
        else:
            mode = CrawlMode.Error

    # No filename argument given; read all files in links folder. Results in path plus filename.
    if len(filenames) == 0:
        for file_link in FOLDER_LINKS.iterdir():
            filenames.append(file_link)

    if mode is CrawlMode.CrawlAllCountries:
        logger.info("Crawling all countries...")
        # This starts bootstrapping from the actual country list as it is on EM.
        country_links = crawl_countries()

        for country_short in country_links:
            country_link = "https://www.metal-archives.com/browse/ajax-country/c/" + country_short
            crawl_country(country_link)
            flush_queue(country_short)
    elif mode is CrawlMode.CrawlCountry:
        logger.info("Crawling a single country: " + country)
        country_link = 'https://www.metal-archives.com/browse/ajax-country/c/' + country
        crawl_country(country_link)
        flush_queue(country)
    elif mode is CrawlMode.CrawlRegion:
        if region not in REGIONS:
            print(f'The region {region} is invalid. Try one from the following list:')
            print()
            print(print_regions())
        else:
            print(f'Crawling region: {region}')
            for country in REGIONS[region][2]:
                country_link = 'https://www.metal-archives.com/browse/ajax-country/c/' + country
                crawl_country(country_link)
            flush_queue(region)
    elif mode in [CrawlMode.CrawlBands, CrawlMode.Test]:
        database = {"artists": {}, "bands": {}, "labels": {}}
        lock = threading.Lock()

        for path in filenames:
            if path.is_file():
                band_links = path.read_text(encoding="utf-8").split('\n')
                # Remove last element from list if it's a lonely, empty string.
                if band_links[-1] == '':
                    del band_links[-1]

                sanitized_bands = []
                # The test mode contains hash commented lines. Here we filter for those.
                if mode is CrawlMode.Test:
                    for line in band_links:
                        if not line.startswith('#'):
                            sanitized_bands.append(line)
                else:
                    sanitized_bands = band_links

                # TODO: Get the country from filename and pass as parameter.
                crawl_bands(sanitized_bands, database, lock)
            else:
                logger.error(f"File {path} was not readable.")

        date_format = f"{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}"
        db_path = FOLDER_DB / f"db-{date_format}.json"
        band_links_file = open(db_path, "w", encoding="utf-8")
        json_database_string = json.dumps(database)
        band_links_file.write(json_database_string)
        band_links_file.close()
        logger.info(f"Database is now available as {db_path}.")
    elif mode is CrawlMode.AnalyseDatabase:
        for path in filenames:
            if path.is_file():
                string_database = path.read_text(encoding="utf-8")

            can_analyse = False

            try:
                database = json.loads(string_database)
                can_analyse = True
            except:
                # We know that the json.load() failed. No need to log exception details.
                logger.error("Loading the JSON database failed. Make sure you selected a valid JSON database.")

            if can_analyse:
                analyse_band_genres(database["bands"])
    elif mode is CrawlMode.DisplayInfo:
        countries = print_countries(4)
        print()
        print('Available countries:')
        print(countries)
        regions = print_regions()
        print()
        print('Available regions:')
        print(regions)

    input('...ending')
    logging.shutdown()


if __name__ == "__main__":
    main(sys.argv[1:])
