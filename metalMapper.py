#!/usr/bin/python
import os
import sys
import getopt
import logging
import logging.config
import yaml
from enum import Enum
from metalCrawler import *

#FORMAT = '%(asctime)-15s - %(message)s'
#logging.basicConfig(filename='crawler.log', level=logging.DEBUG, format=FORMAT)

class MapMode(Enum):
    Error = -1
    SingleCrawl = 0

def printHelp():
    print('Supported modes:')
    print('  Crawl mode: metalMapper.py -c')

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
        opts, args = getopt.getopt(argv, "ch")
    except getopt.GetoptError:
        printHelp()
        sys.exit(2)

    mode = MapMode.Error

    if not opts:
        printHelp()

    for opt, arg in opts:
        if opt == '-h':
            printHelp()
            sys.exit()
        elif opt == '-c':
            #crawlBands()
            #crawlBand('Darkthrone')
            #crawlBand('Bathory')
            #crawlBand('Sepultura')
            #crawlBand('LIK')
            #crawlCountry("https://www.metal-archives.com/browse/ajax-country/c/AF/")
            #crawlCountry("https://www.metal-archives.com/browse/ajax-country/c/DE/")
            crawlCountry("https://www.metal-archives.com/browse/ajax-country/c/US/")

    input('...ending')
    logging.shutdown()

if __name__ == "__main__":
   main(sys.argv[1:])


