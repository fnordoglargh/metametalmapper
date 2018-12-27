#!/usr/bin/python
import os
import sys
import getopt
import logging
import logging.config
import yaml
from enum import Enum
from metalCrawler import *
import json
import pprint

# FORMAT = '%(asctime)-15s - %(message)s'
# logging.basicConfig(filename='crawler.log', level=logging.DEBUG, format=FORMAT)
link_extension = ".lnks"
bandsListFileName = "bands" + link_extension


class CrawlMode(Enum):
    Error = -1
    CrawlCountry = 0
    CrawlAllCountries = 1
    CrawlBands = 2


def print_help():
    print('Supported modes:')
    print('  -a: Crawls all countries for bands and saves them in a file named {}.'.format(bandsListFileName))
    print('      This action can take almost 10 minutes.')
    print('  -b: Crawls all bands in the generated file {} from option -c.'.format(bandsListFileName))
    print('  -c <country ID>: Crawls the supplied country (e.g. NO for Norway)')
    print('     and uses the standard file name together with the ID to write a')
    print('     file with all band links from the given country. See Wikipedia for examples:')
    print('     https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes')
    print('  -f <filename>: filename is a parameter to override the standard file name')
    print('     for -b or -c and is used either to write an output file or to read an')
    print('     input file.')


def main(argv):
    with open('loggerConfig.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    logger = logging.getLogger('MAIN')

    try:
        # TODO: Fix defect while using -c and -f together.
        opts, args = getopt.getopt(argv, "bac:hf:t")
    except getopt.GetoptError:
        logger.exception("There's an issue with the parameters.")
        print_help()
        sys.exit(2)

    # Change to a terminal size in which everything fits.
    os.system('mode con: cols=153 lines=9999')
    logger.debug('***************************************************************')
    logger.debug('Starting up...')
    mode = CrawlMode.Error
    filename = ""

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
        else:
            mode = CrawlMode.Error

    if mode is CrawlMode.CrawlAllCountries:
        logger.info("Crawling all countries...")
        country_links = crawl_countries()

        for countryLink in country_links:
            crawl_country(countryLink)

        band_links_file = open(bandsListFileName, "w", encoding="utf-8")

        while bandsQueue.qsize() != 0:
            band_links_file.write(bandsQueue.get_nowait() + '\n')

        band_links_file.close()
    elif mode is CrawlMode.CrawlCountry:
        logger.info("Crawling a single country: " + country)
        country_link = 'https://www.metal-archives.com/browse/ajax-country/c/' + country
        crawl_country(country_link)
        country_filename = "bands-{}{}".format(country, link_extension)
        if bandsQueue.qsize() != 0:
            band_links_file = open(country_filename, "w", encoding="utf-8")
            while bandsQueue.qsize() != 0:
                band_links_file.write(bandsQueue.get_nowait() + '\n')
            band_links_file.close()
            logger.info("Saved bands of {} in file {}.".format(country, country_filename))
        else:
            logger.warning("No bands in country {}. To check country manually, use above link.".format(country))
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

        # bands_json_file2 = open(filename + ".json", 'r', encoding="utf-8")
        # read_json_string = bands_json_file2.read()
        # bands_json_file2.close()
        # database_from_file = json.loads(read_json_string)

    input('...ending')
    logging.shutdown()


if __name__ == "__main__":
    main(sys.argv[1:])
