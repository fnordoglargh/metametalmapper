import argparse
import textwrap
from global_helpers import *
from country_helper import COUNTRY_NAMES, REGIONS, print_regions, print_countries
from metal_crawler import crawl_countries

file_name_a = BAND_LINK_FILE_NAME.format('NN')
all_links_text = f'Crawls all countries for bands and saves them in files named {file_name_a} (where NN is the two ' \
    f'letter short form of a given country). The files are put into sub-folder "{FOLDER_LINKS}". This action can take '\
    'almost 10 minutes.'
all_countries_text = 'Crawls the supplied countries (e.g. NO for Norway) and uses the standard file name together ' \
    'with the ID to write a file with all band links from the given country. See list (-l) below. The country shorts ' \
    'must always be separated by commas without spaces or be enclosed by quotation-marks if they contain spaces.'
region_text = '-r <region ID>: Crawls a predefined region (call -l for example IDs or try NCO to get short links of ' \
    'all Nordic Countries).'
crawl_text = 'Crawls a file with short links either from running -a, -i, -c or your own. If a region or country short '\
    f'(see -l) is specified, it will try finding a generated file in sub-folder "{FOLDER_LINKS}".'

list_text = 'List available countries and regions.'

# Indication of a parameter
not_set = 'not_set'
default_text = 'lazy_default'
choices = COUNTRY_NAMES.keys()

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
arg_parser.add_argument('-s', '--single',
                        help='Crawls the given short link (e.g. Darkthrone/146) and all connected bands.')
arg_parser.add_argument('-a', '--all_links', action="store_true", help=all_links_text)
arg_parser.add_argument('-i', '--iso_countries', nargs='+', help=all_countries_text)
arg_parser.add_argument('-r', '--region', help=region_text)
arg_parser.add_argument('-c', '--crawl', nargs='?', const=not_set, help=crawl_text)
arg_parser.add_argument('-l', '--list', action="store_true", help=list_text)
args = arg_parser.parse_args()

# Test the arguments
if args.all_links:
    print('-a is set with no params.')

# Check if single mode can be used.
if args.single is not None:
    print(f'-s {args.single}')

# Check if -c --iso_countries can be used.
if args.iso_countries is not None and len(args.iso_countries) > 0:
    for country in args.iso_countries:
        country = country.upper()
        if country not in COUNTRY_NAMES.keys():
            print(f'{country} is not a valid ISO country short.')
        else:
            print(f'-c: {args.iso_countries}')

if args.region is not None:
    if args.region in REGIONS:
        print(args.region)
    else:
        print(f'Not a valid region: {args.region}')

if args.list:
    country_string = print_countries(4, crawl_countries())
    print()
    print('Available countries:')
    print(country_string)
    regions = print_regions()
    print()
    print('Available regions:')
    print(regions)

if args.crawl is not None:
    if args.crawl is not not_set:
        # Test if parameter is a valid region or country.
        if args.crawl in COUNTRY_NAMES.keys() or args.crawl in REGIONS.keys():
            country_region_file = Path(f'{FOLDER_LINKS}/{args.crawl}{LINK_EXTENSION}')

            if country_region_file.is_file():
                print('Valid region/country file.')
            else:
                print('File not found.')

            print(f'  {country_region_file}')
        else:
            link_file = Path(args.crawl)

            if link_file.is_file():
                print(f'Seems to be a link file: {link_file}')
            else:
                print('Not a valid file, country or region short.')
    else:
        print('Parameter missing.')
