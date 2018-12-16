#!/usr/bin/python
import os
import sys
import getopt
import logging
import logging.config
import yaml
from enum import Enum
from metalCrawler import *

# FORMAT = '%(asctime)-15s - %(message)s'
# logging.basicConfig(filename='crawler.log', level=logging.DEBUG, format=FORMAT)
bandsListFileName = "bandLinks.txt"


class MapMode(Enum):
    Error = -1
    SingleCrawl = 0


def print_help():
    print('Supported modes:')
    print('  -c: Crawls all countries for bands and saves them in a file named {}.'.format(bandsListFileName))
    print('      This action can take almost 10 minutes.')
    print('  -b: Crawls all bands in the generated file {} from option -c.'.format(bandsListFileName))


def main(argv):
    with open('loggerConfig.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    # Change to a terminal size in which everything fits.
    os.system('mode con: cols=153 lines=9999')
    logger = logging.getLogger('MAIN')
    logger.debug('***************************************************************')
    logger.debug('Starting up...')

    try:
        opts, args = getopt.getopt(argv, "bch")
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    mode = MapMode.Error

    if not opts:
        print_help()

    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt == '-c':
            countryLinks = crawl_countries()

            for countryLink in countryLinks:
                crawl_country(countryLink)

            bandLinks_file = open(bandsListFileName, "w", encoding="utf-8")

            while bandsQueue.qsize() != 0:
                bandLinks_file.write(bandsQueue.get_nowait() + '\n')

            bandLinks_file.close()

        elif opt == '-b':
            crawl_bands("bandLinksTest.txt")
            # crawlBands(bandsListFileName)

            # crawlBands()
            # crawlBand('Darkthrone')
            # crawlBand('Bathory')
            # crawlBand('Sepultura')
            # crawlBand('LIK')
            # result = crawlBand('LIK')

            # if result == -1:
            #    logger.error("The name alone was invalid. No bands page to scrape.")

    input('...ending')
    logging.shutdown()


if __name__ == "__main__":
    main(sys.argv[1:])
