#!/usr/bin/env python

"""_Meta Metal Mapper_ is a Python3 program and intended to be the basis to develop a toolset to crawl data of
[Encyclopaedia Metallum: The Metal Archives](https://www.metal-archives.com/) (M-A), write it into a database  and query
said data.
"""

import sys
import logging.config
import yaml
import argparse
import textwrap

from global_helpers import *
from country_helper import COUNTRY_NAMES, REGIONS, print_regions, print_countries
from metal_crawler import crawl_country, crawl_countries, crawl_bands
from graph.graph_neomodel_impl import NeoModelStrategy
from graph.metal_graph import GraphDatabaseContext
from graph.report import ReportMode
from graph.export_graph import GraphExportContext, GraphMLExporter
from genre import save_genres
from html_exporter import generate_html_report

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2020, Martin Woelke'
# https://opensource.org/licenses/NPOSL-3.0
__version__ = '0.97.3'
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


def flush_queue(country_short, link_list):
    """Flushes the contents of ``link_list`` (band addresses of a country or region) into the sub-folder named
    ``links``.

    :param country_short: ISO country code used in the file name.
    :param link_list: A list of short band links.
    :return: A filename with the format ``links/NN.lnks``.
    """
    logger = logging.getLogger('Mapper')
    country_filename = Path(f"{FOLDER_LINKS}/" + BAND_LINK_FILE_NAME.format(country_short))
    country_or_region_code = country_short

    if len(country_short) == 2:
        country_or_region_name = COUNTRY_NAMES[country_short]
    else:
        country_or_region_name = REGIONS[country_short][1]

    if len(link_list) > 0:
        band_links_file = open(country_filename, 'w', encoding='utf-8')
        counter = 0
        for link in link_list:
            band_links_file.write(link + '\n')
            counter += 1

        band_links_file.close()
        logger.info(
            f'Saved {str(counter)} bands of {country_or_region_name} ({country_or_region_code}) in file '
            f'"{country_filename}".'
        )
    else:
        logger.warning(f'No bands found for {country_or_region_name} ({country_or_region_code}).')

    return country_filename


def init_db():
    logger = logging.getLogger('Mapper')
    db_handle = None
    try:
        db_handle = GraphDatabaseContext(NeoModelStrategy())
    except:
        logger.error('  Need a database to function properly. Exiting...')

    return db_handle


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
        logger.info('Crawling countries...')

        # This starts bootstrapping from the actual country list as it is on EM.
        country_links = crawl_countries()

        for country_short in country_links:
            link_list = crawl_country(country_short)
            flush_queue(country_short, link_list)
    # Single mode
    elif args.s is not None:
        db_handle = init_db()

        if db_handle is not None:
            crawl_bands([args.s], db_handle, is_single_mode=True)
            save_genres()
    # ISO countries
    elif args.i is not None and len(args.i) > 0:
        countries = []
        for country in args.i:
            country = country.upper()

            if country not in COUNTRY_NAMES.keys():
                print(f'{country} is not a valid ISO country short.')
            else:
                countries.append(country)

        if len(countries) > 0:
            for country in countries:
                link_list = crawl_country(country)
                flush_queue(country, link_list)
        else:
            print('No valid countries given.')

    # Region
    elif args.r is not None:
        region = args.r
        if region not in REGIONS:
            print(f'The region key {region} is invalid. Try one from the following list:')
            print()
            print(print_regions())
        else:
            print(f'Crawling region: {REGIONS[region][1]}')
            link_list = []
            for country_short in REGIONS[region][2]:
                link_list_temp = crawl_country(country_short)
                link_list = list(set(link_list_temp + link_list))
            flush_queue(region, link_list)
    # Crawl country, region or file.
    elif args.c is not None:
        # Test if parameter is a valid region or country.
        if args.c in COUNTRY_NAMES.keys() or args.c in REGIONS.keys():
            country_region_file = Path(f'{FOLDER_LINKS}/{args.c}{LINK_EXTENSION}')
        # ...or take it as file name unconditionally.
        else:
            country_region_file = Path(args.c)

        sanitized_bands = []

        if country_region_file.is_file():
            band_links = country_region_file.read_text(encoding='utf-8').split('\n')
            # Remove last element from list if it's a lonely, empty string.
            if band_links[-1] == '':
                del band_links[-1]

            # For testing a  file may contain hash commented lines. Here we filter for those.
            for line in band_links:
                if not line.startswith('#'):
                    sanitized_bands.append(line)
        else:
            logger.error(f'File {country_region_file} was not readable.')

        if len(sanitized_bands) is not 0:
            db_handle = init_db()
            if db_handle is not None:
                crawl_bands(sanitized_bands, db_handle)
                save_genres()
        else:
            logger.error(
                'No bands to crawl. Check your input files.')
    elif args.y is not None or args.z:
        if args.z:
            report_mode = ReportMode.CountryOff
        else:
            report_mode = ReportMode.CountryOn

        country_links = []

        if args.y is not None:
            if len(args.y) is 1 and args.y[0].upper() == 'ALL':
                print('Analyse entire DB.')
            else:
                for country in args.y:
                    if country in COUNTRY_NAMES.keys():
                        country_links.append(country)
                    elif country in REGIONS.keys():
                        country_links = list(set(country_links + REGIONS[country][2]))
                    else:
                        print(f'Unknown country/region: {country}')

        db_handle = init_db()

        if db_handle is None:
            sys.exit(-9)

        country_info = 'Generating report for: '

        for clean_short in country_links:
            country_info += f'{COUNTRY_NAMES[clean_short]}, '

        if len(country_links) is 0:
            print(f'{country_info}Entire database.')
        else:
            print(country_info[:-2])

        raw_report = db_handle.generate_report(country_links, report_mode)
        print(raw_report)

        if report_mode is ReportMode.CountryOn:
            logger.info(f'Country report saved to: {raw_report.export_csv_country()}')
        release_export_path = raw_report.album_report.export_csv_releases_per_year()
        logger.info(f'Release reports saved to:')
        logger.info(f'  {release_export_path}')
        release_json_export_path = raw_report.album_report.export_json_releases_per_year()
        logger.info(f'  {release_json_export_path}')
        release_all_json_export_path = raw_report.album_report.export_all_releases()
        logger.info(f'  {release_all_json_export_path}')
        bands_formed_export_path = raw_report.export_csv_bands_formed()
        logger.info(f'Bands formed per year report saved to: {bands_formed_export_path}')
        export_data = [
            (release_json_export_path, 'marker_releases_year'),
            (release_all_json_export_path, 'marker_releases_all')
        ]
        html_report_location = generate_html_report(export_data)
        logger.info(f'HTML report saved to: {html_report_location}')
        genre_export_paths = raw_report.export_csv_genres()
        logger.info(f'Genre reports saved to:')
        logger.info(f'  All : {genre_export_paths[0]}')
        logger.info(f'  Core: {genre_export_paths[1]}')
        export_handle = GraphExportContext(GraphMLExporter())
        relationships = db_handle.export_bands_network(country_links)
        export_handle.export_graph(relationships)
    elif args.l:
        country_string = print_countries(4, crawl_countries())
        print()
        print('Available countries:')
        print(country_string)
        regions = print_regions()
        print()
        print('Available regions:')
        print(regions)
    else:
        arg_parser.print_help()


if __name__ == '__main__':
    main()
