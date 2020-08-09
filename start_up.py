#!/usr/bin/env python

import sys
import logging.config
import yaml
import argparse
import textwrap

from global_helpers import *
from country_helper import COUNTRY_NAMES, REGIONS, print_regions, print_countries
from metal_crawler import crawl_countries

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2020, Martin Woelke'
# https://opensource.org/licenses/NPOSL-3.0
__version__ = '0.97.2'
__status__ = 'Development'

file_name_a = BAND_LINK_FILE_NAME.format('NN')
single_text = 'Crawls the given short link (e.g. Darkthrone/146) and all connected bands.'
all_links_text = f'Crawls all countries for bands and saves them in files named {file_name_a} (where NN is the two ' \
    f'letter short form of a given country). The files are put into sub-folder "{FOLDER_LINKS}". This action can take '\
    'almost 10 minutes.'
all_countries_text = 'Crawls the supplied countries (e.g. NO for Norway) and uses the standard file name together ' \
    'with the ID to write a file with all band links from the given country. See list (-l) below.'
region_text = '-r <region ID>: Crawls a predefined region (call -l for sample IDs or try NCO to get short links of ' \
    'all Nordic Countries).'
crawl_text = 'Crawls a file with short links either from running -a, -i, -c or your own. If a region or country short '\
    f'(see -l) is specified, it will try finding a generated file in sub-folder "{FOLDER_LINKS}".'
analyze_full_text = 'Prints and exports a raw data report of the active database and also exports a GraphML file of ' \
    'all bands (including their implicit connections through artists). Either use "ALL" for the entire database or a ' \
    'list of country shorts or regions as parameter. Note: The country analysis depends on having all bands for a ' \
    'given country. It will function properly but calculate bogus numbers.'
analyze_light_text = 'The "diet version" of -y without the country report. Use this mode to analyze data from the ' \
    'crawl mode -s.'

list_text = 'List available countries and regions.'

# Indication of a parameter
not_set = 'not_set'


def main():
    with open('loggerConfig.yaml', 'r') as log_config:
        log_config = yaml.safe_load(log_config.read())
        logging.config.dictConfig(log_config)

    # Change to a terminal size in which everything fits.
    # os.system('mode con: cols=153 lines=9999')
    logger = logging.getLogger('MAIN')
    logger.debug('***************************************************************')
    logger.info(f'meta metal mapper {__version__}')

    # Check necessary FOLDERS_MAIN exist, try to create them otherwise.
    for folder in FOLDERS_MAIN:
        if not folder.exists() and not folder.is_dir():
            try:
                folder.mkdir()
                logger.info(f'Successfully created the directory {folder}.')
            except:
                logger.fatal(f'Creation of the directory {folder} failed.')
                sys.exit(3)
        else:
            logger.debug(f'Standard directory {folder} exists.')

    arg_parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description=textwrap.dedent('''\
            Crawls and (meta) analyzes date from M-A.
    
            It's run in two to three stages:
                1.  Get a list of bands (-a, -c, -r).
                2a. Crawl one band through its short link (-s <link>) without stage 1.
                2b. Crawl a list of bands generated in stage 1 (by filename).
                3.  Analyze the gathered data  
    
            NOTE: Parameters are given priority based on their stage and cannot be mixed.
        '''))
    arg_parser.add_argument('-s', help=single_text, metavar='MA_SHORT_LINK')
    arg_parser.add_argument('-a', action="store_true", help=all_links_text)
    arg_parser.add_argument('-i', nargs='+', help=all_countries_text, metavar='COUNTRY_SHORT')
    arg_parser.add_argument('-r', help=region_text, metavar='REGION_ID')
    arg_parser.add_argument('-c', help=crawl_text, metavar='FILE_OR_REGION_OR_COUNTRY_SHORT')
    arg_parser.add_argument('-y', nargs='+', help=analyze_full_text, metavar='REGION_OR_COUNTRY_SHORT')
    arg_parser.add_argument('-z', action="store_true", help=analyze_light_text)
    arg_parser.add_argument('-l', action="store_true", help=list_text)
    args = arg_parser.parse_args()

    # All countries
    if args.a:
        print('-a is set with no params.')

    # Single mode
    if args.s is not None:
        print(f'-s {args.s}')

    # ISO countries
    if args.i is not None and len(args.i) > 0:
        for country in args.i:
            country = country.upper()
            if country not in COUNTRY_NAMES.keys():
                print(f'{country} is not a valid ISO country short.')
            else:
                print(f'-c: {country}')

    # Region
    if args.r is not None:
        if args.r in REGIONS:
            print(args.r)
        else:
            print(f'Not a valid region: {args.r}')

    if args.l:
        country_string = print_countries(4, crawl_countries())
        print()
        print('Available countries:')
        print(country_string)
        regions = print_regions()
        print()
        print('Available regions:')
        print(regions)

    if args.c is not None:
        if args.c is not not_set:
            # Test if parameter is a valid region or country.
            if args.c in COUNTRY_NAMES.keys() or args.c in REGIONS.keys():
                country_region_file = Path(f'{FOLDER_LINKS}/{args.c}{LINK_EXTENSION}')

                if country_region_file.is_file():
                    print('Valid region/country file.')
                else:
                    print('File not found.')

                print(f'  {country_region_file}')
            else:
                link_file = Path(args.c)

                if link_file.is_file():
                    print(f'Seems to be a link file: {link_file}')
                else:
                    print('Not a valid file, country or region short.')
        else:
            print('Parameter missing.')

    if args.y is not None:
        if len(args.y) is 1 and args.y[0].upper() == 'ALL':
            print('Analyse entire DB.')
        else:
            for country in args.y:
                if country in COUNTRY_NAMES.keys() or country in REGIONS.keys():
                    print(f'Analyze {country}.')
                else:
                    print(f'Unknown country/region: {country}')

    if args.z:
        print('Small Analysis.')

    # arg_parser.print_help()


if __name__ == '__main__':
    main()
