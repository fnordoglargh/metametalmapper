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

link_extension = ".lnks"
bandsListFileName = "bands" + link_extension

FOLDER_LINKS = Path("links")
FOLDER_DB = Path("databases")
folders = [FOLDER_LINKS, FOLDER_DB]


class CrawlMode(Enum):
    Error = -1
    CrawlCountry = 0
    CrawlAllCountries = 1
    CrawlBands = 2
    AnalyseDatabase = 3


def print_help():
    print('Supported modes:')
    print('  -a: Crawls all countries for bands and saves them in a file named {}.'.format(bandsListFileName))
    print('    This action can take almost 10 minutes.')
    print('  -b: Crawls all bands in the generated file {} from option -a'.format(bandsListFileName))
    print('    (or -c if you specify your own file with -f).')
    print('  -c <country ID>: Crawls the supplied country (e.g. NO for Norway)')
    print('    and uses the standard file name together with the ID to write a')
    print('    file with all band links from the given country. See Wikipedia for examples:')
    print('    https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes')
    print('  -y: Prints a report about the genres of a database.')
    print('  -f <filename>: filename is a parameter to override the standard file name')
    print('    for -b or -c and is used either to write an output file or to read an')
    print('    input file.')


def flush_queue(country_short):
    logger = logging.getLogger('Crawler')
    country_filename = Path(f"{FOLDER_LINKS}/bands-{country_short}{link_extension}")

    if bandsQueue.qsize() != 0:
        band_links_file = open(country_filename, "w", encoding="utf-8")
        counter = 0
        while bandsQueue.qsize() != 0:
            band_links_file.write(bandsQueue.get_nowait() + '\n')
            counter += 1
        band_links_file.close()
        logger.info("Saved {} bands of {} in file '{}'.".format(str(counter), country_short, country_filename))
    else:
        logger.warning("No bands in country {}. To check country manually, use above link.".format(country_short))


def main(argv):
    try:
        # TODO: Fix defect while using -c and -f together.
        opts, args = getopt.getopt(argv, "bac:hf:ty")
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    with open('loggerConfig.yaml', 'r') as log_config:
        config = yaml.safe_load(log_config.read())
        logging.config.dictConfig(config)

    # Change to a terminal size in which everything fits.
    os.system('mode con: cols=153 lines=9999')
    logger = logging.getLogger('MAIN')
    logger.debug('***************************************************************')
    logger.debug('Starting up...')
    mode = CrawlMode.Error
    filename = ""

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

    if not opts:
        print_help()

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
            logger.info("Supplied file name: " + filename)
        elif opt == '-t':
            result = cut_instruments('Drums(1988-1993, 1994-present)')
            print()
        elif opt == '-y':
            mode = CrawlMode.AnalyseDatabase
        else:
            mode = CrawlMode.Error

    if mode is CrawlMode.CrawlAllCountries:
        logger.info("Crawling all countries...")
        # This starts bootstrapping from the actual country list as it is on EM.
        country_links = crawl_countries()

        for countryLink in country_links:
            country_short = countryLink[countryLink.rfind('/') + 1:]
            crawl_country(countryLink)
            flush_queue(country_short)
    elif mode is CrawlMode.CrawlCountry:
        logger.info("Crawling a single country: " + country)
        country_link = 'https://www.metal-archives.com/browse/ajax-country/c/' + country
        crawl_country(country_link)
        flush_queue(country)
    elif mode is CrawlMode.CrawlBands:
        # Use standard file name if no -f has been supplied.
        if len(filename) is 0:
            filename = bandsListFileName

        database = {"artists": {}, "bands": {}, "labels": {}}
        lock = threading.Lock()
        crawl_bands(filename, database, lock)
        json_database_string = json.dumps(database)

        with open(filename + ".json", 'w', encoding="utf-8") as database_json_file:
            database_json_file.write(json_database_string)

        logger.info("Database is now available as {}.".format(filename + ".json"))
    elif mode is CrawlMode.AnalyseDatabase:
        # Use standard file name if no -f has been supplied.
        if len(filename) is 0:
            filename = bandsListFileName

        with open(filename + ".json", 'r', encoding="utf-8") as json_database_string:
            string_database = json_database_string.read()

        database = json.loads(string_database)
        analyse_band_genres(database["bands"])

    input('...ending')
    logging.shutdown()


if __name__ == "__main__":
    main(sys.argv[1:])
