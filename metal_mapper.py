#!/usr/bin/env python

"""_Metal Mapper_ is a Python3 program and intended to be the basis to develop a toolset to access data of
[Encyclopaedia Metallum: The Metal Archives](https://www.metal-archives.com/) (MA) and query said data.
"""

import sys
import getopt
import logging.config
import yaml
from enum import Enum
from metalCrawler import *
from graph.implNeoModel import *
from graph.metalGraph import *
from graph.exportGraph import *
from global_helpers import *
from country_helper import REGIONS, print_regions, print_countries, COUNTRY_NAMES
from genre import save_genres
from html_exporter import generate_html_report

__author__ = "Martin Woelke"
__copyright__ = "Copyright 2019, D-Test AG"
__license__ = ""
__version__ = "0.19"
__status__ = "Development"

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


def print_help():
    file_name_a = BAND_LINK_FILE_NAME.format('XX')
    # TODO: Move two letter country names to description section.
    print(
        f'Supported modes:\n'
        f'  -a: Crawls all countries for bands and saves them in files named {file_name_a}\n'
        f'    (where XX is the two letter short form of a given country). The files are put\n'
        f'    into sub-folder {FOLDER_LINKS}. This action can take almost 10 minutes.\n'
        f'  -b: Crawls all bands in the generated files from option -a\n'
        f'    (or -c if you specify your own file with -f).\n'
        f'  -c <country ID>: Crawls the supplied country (e.g. NO for Norway)\n'
        f'    and uses the standard file name together with the ID to write a\n'
        f'    file with all band links from the given country. See list below.\n'
        f'  -y: Prints a raw data report of the active database and exports a GraphML file\n'
        f'    of all bands (including their implicit connections through artists).\n'
        f'  -z: Does the same as "-y" but expects a list of 1 to n countries or regions.\n'
        f'    The list items must always be separated by commas without spaces or be\n'
        f'    enclosed by quotation-marks.\n'
        f'  -f <filename>: filename is a parameter to override the standard file name\n'
        f'    for -b or -c and is used either to write an output file or to read an\n'
        f'    input file.\n'
        f'  -l: List available countries and regions.\n'
        f'  -r <region ID>: Crawls a predefined region (call -l for example IDs or try NCO\n'
        f'    to get short links of all Nordic Countries.)\n'
    )


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
        band_links_file = open(country_filename, "w", encoding="utf-8")
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
        logger.warning(f"No bands found for {country_or_region_name} ({country_or_region_code}).")

    return country_filename


def init_db():
    logger = logging.getLogger('Mapper')
    db_handle = None
    try:
        db_handle = GraphDatabaseContext(NeoModelStrategy())
    except:
        logger.error("  Need database to function properly. Exiting...")

    return db_handle


def main(argv):
    try:
        # TODO: Fix defect while using -c and -f together.
        opts, args = getopt.getopt(argv, "dbac:hf:tyz:lr:")
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    if not opts:
        print_help()
        sys.exit(0)

    with open('loggerConfig.yaml', 'r') as log_config:
        log_config = yaml.safe_load(log_config.read())
        logging.config.dictConfig(log_config)

    # Change to a terminal size in which everything fits.
    os.system('mode con: cols=153 lines=9999')
    logger = logging.getLogger('MAIN')
    logger.debug('***************************************************************')
    logger.info(f'metal mapper {__version__}')
    mode = CrawlMode.Error
    filenames = []

    # Check necessary FOLDERS_MAIN exist, try to create them otherwise.
    for folder in FOLDERS_MAIN:
        if not folder.exists() and not folder.is_dir():
            try:
                folder.mkdir()
                logger.info(f"Successfully created the directory {folder}.")
            except:
                logger.fatal(f"Creation of the directory {folder} failed.")
                sys.exit(3)
        else:
            logger.debug(f"Standard directory {folder} exists.")

    country_links = []
    is_detailed = False

    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt == '-c':
            country_short = arg.upper()
            country_links.append(country_short)
            mode = CrawlMode.CrawlCountry
        elif opt == '-a':
            mode = CrawlMode.CrawlAllCountries
        elif opt == '-b':
            mode = CrawlMode.CrawlBands
        elif opt == '-f':
            filenames.append(Path(arg))
            logger.info(f"Supplied file name: '{arg}'.")
        elif opt == '-y':
            mode = CrawlMode.AnalyseDatabase
        elif opt == '-z':
            country_links = arg.upper().split(',')
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
        elif opt == '-d':
            is_detailed = True
        else:
            mode = CrawlMode.Error

    # No filename argument given; read all files in links folder. Results in path plus filename.
    if len(filenames) == 0:
        for file_link in FOLDER_LINKS.iterdir():
            filenames.append(file_link)

    if mode in [CrawlMode.CrawlAllCountries, CrawlMode.CrawlCountry]:
        logger.info("Crawling countries...")

        if len(country_links) is 0:
            # This starts bootstrapping from the actual country list as it is on EM.
            country_links = crawl_countries()

        for country_short in country_links:
            link_list = crawl_country(country_short)
            flush_queue(country_short, link_list)
    elif mode is CrawlMode.CrawlRegion:
        if region not in REGIONS:
            print(f'The region {region} is invalid. Try one from the following list:')
            print()
            print(print_regions())
        else:
            print(f'Crawling region: {region}')
            link_list = []
            for country_short in REGIONS[region][2]:
                link_list_temp = crawl_country(country_short)
                link_list = list(set(link_list_temp + link_list))
            flush_queue(region, link_list)
    elif mode in [CrawlMode.CrawlBands, CrawlMode.Test]:
        sanitized_bands = []

        for path in filenames:
            if path.is_file():
                band_links = path.read_text(encoding="utf-8").split('\n')
                # Remove last element from list if it's a lonely, empty string.
                if band_links[-1] == '':
                    del band_links[-1]

                # The test mode contains hash commented lines. Here we filter for those.
                if mode is CrawlMode.Test:
                    for line in band_links:
                        if not line.startswith('#'):
                            sanitized_bands.append(line)
                else:
                    sanitized_bands = band_links
            else:
                logger.error(f"File {path} was not readable.")

        if len(sanitized_bands) is not 0:
            db_handle = init_db()
            if db_handle is not None:
                # TODO: Get the country from filename and pass as parameter.
                crawl_bands(sanitized_bands, db_handle, is_detailed)
                save_genres()
        else:
            logger.error("No bands are available. Make sure that you crawled a country or regions before -b is used.")
    elif mode in [CrawlMode.AnalyseDatabase]:
        db_handle = init_db()

        if db_handle is None:
            sys.exit(-9)

        cleaned_shorts = []

        for short in country_links:
            stripped_short = short.rstrip().strip()
            if stripped_short in REGIONS.keys():
                region_elements = REGIONS[stripped_short][2]
                for country in region_elements:
                    cleaned_shorts.append(country)
            elif stripped_short in COUNTRY_NAMES.keys():
                cleaned_shorts.append(stripped_short)
            else:
                logger.error(f'Ignoring {stripped_short}; not found in countries or regions.')

        country_info = 'Generating report for: '

        for clean_short in cleaned_shorts:
            country_info += f'{COUNTRY_NAMES[clean_short]}, '

        if len(cleaned_shorts) is 0:
            print(f'{country_info}Entire database.')
        else:
            print(country_info[:-2])

        raw_report = db_handle.generate_report(cleaned_shorts)
        print(raw_report)

        logger.info(f'Country report saved to: {raw_report.export_csv_country()}')
        release_export_path = raw_report.album_report.export_csv_releases_per_year()
        logger.info(f'Release report saved to: {release_export_path}')
        release_json_export_path = raw_report.album_report.export_json_releases_per_year()
        logger.info(f'Release export saved to: {release_json_export_path}')
        release_all_json_export_path = raw_report.album_report.export_all_releases()
        logger.info(f'Release export saved to: {release_all_json_export_path}')
        export_data = [
            (release_json_export_path, "marker_releases_year"),
            (release_all_json_export_path, "marker_releases_all")
        ]
        html_report_location = generate_html_report(export_data)
        logger.info(f'HTML report saved to: {html_report_location}')
        genre_export_paths = raw_report.export_csv_genres()
        logger.info(f'Genre reports saved to:')
        logger.info(f'  All : {genre_export_paths[0]}')
        logger.info(f'  Core: {genre_export_paths[1]}')
        export_handle = GraphExportContext(GraphMLExporter())
        relationships = db_handle.export_bands_network(cleaned_shorts)
        export_handle.export_graph(relationships)
    elif mode is CrawlMode.DisplayInfo:
        country_string = print_countries(4, crawl_countries())
        print()
        print('Available countries:')
        print(country_string)
        regions = print_regions()
        print()
        print('Available regions:')
        print(regions)

    logging.shutdown()


if __name__ == "__main__":
    main(sys.argv[1:])
