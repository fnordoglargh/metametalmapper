import argparse
import textwrap
from global_helpers import *
from country_helper import COUNTRY_NAMES

description_text = "Crawls and (meta) analyzes date from M-A.\n\nIt's run in two to three stages:\n1. Get a list of" \
                   "band"

file_name_a = BAND_LINK_FILE_NAME.format('NN')
all_links_text = f'Crawls all countries for bands and saves them in files named {file_name_a} (where NN is the two ' \
                 f'letter short form of a given country). The files are put into sub-folder "{FOLDER_LINKS}". This action can take ' \
                 'almost 10 minutes.'
all_countries_text = 'Crawls the supplied countries (e.g. NO for Norway) and uses the standard file name together with' \
                     ' the ID to write a file with all band links from the given country. See list (-l) below. The country shorts must ' \
                     'always be separated by commas without spaces or be enclosed by quotation-marks if they contain spaces.'

# Indication of a parameter
not_set = 'not set'
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
arg_parser.add_argument('-s', '--single', nargs='?', const=not_set,
                        help='Crawls the given short link (e.g. Darkthrone/146) and all connected bands.')
arg_parser.add_argument('-a', '--all_links', nargs='?', const=not_set, help=all_links_text)
arg_parser.add_argument('-c', '--iso_countries', nargs='*', help=all_countries_text, choices=choices)
args = arg_parser.parse_args()

# Test the arguments
if args.all_links is not_set:
    print('-a is set with no params.')

# Check if single mode can be used.
if args.single is not_set and args.single is not None:
    print('-s needs a band short link (e.g. Darkthrone/146).')
elif args.single is not None:
    print(f'-s {args.single}')

# Check if -c --iso_countries can be used.
if args.iso_countries is not None and len(args.iso_countries) > 0:
    for country in args.iso_countries:
        country = country.upper()
        if country not in COUNTRY_NAMES.keys():
            print(f'{country} is not a valid ISO country short.')
        else:
            print(f'-c: {args.iso_countries}')
else:
    print('-c needs at least one ISO country short. Print a list of available countries with -l. ')



