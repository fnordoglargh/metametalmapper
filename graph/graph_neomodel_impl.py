"""Implements the `GraphDatabaseStrategy` and a set of classes to define data in the neomodel context."""

from collections import defaultdict
import settings

import logging
from neomodel import StringProperty, IntegerProperty, ArrayProperty, DateProperty, RelationshipTo, \
    RelationshipFrom, StructuredRel, config, core, db
from neo4j import exceptions
from neomodel.match import *
import progressbar

from country_helper import COUNTRY_NAMES, COUNTRY_POPULATION
from graph.choices import *
from graph.metal_graph import GraphDatabaseStrategy, POP_BANDS, POP_PER_100K, POP_POPULATION, RAW_GENRES, POP_COUNTRY
from graph.report import CountryReport, DatabaseReport, ReleaseReport, ReportMode
from export_data import ExportData

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2020, Martin Woelke'


class MemberRelationship(StructuredRel):
    # TODO: Try to use multiple connections for each stint.
    time_frame = ArrayProperty()
    # start_date = DateProperty()
    # end_date = DateProperty()
    pseudonym = StringProperty()
    instrument = StringProperty()
    status = StringProperty(choices=MEMBER_STATUS)


class Band(StructuredNode):
    emid = IntegerProperty(unique_index=True)
    link = StringProperty()
    visited = DateProperty()
    name = StringProperty()
    country = StringProperty(choices=COUNTRY_NAMES)
    locations = ArrayProperty()
    status = StringProperty(choices=BAND_STATUS)
    formed = DateProperty()
    active = ArrayProperty(DateProperty())
    themes = ArrayProperty()  # Should a theme be a node?
    genres = ArrayProperty()
    current_lineup = RelationshipFrom("Member", "PLAYED_IN", model=MemberRelationship)
    releases = RelationshipTo('Release', 'RECORDED')


class Label(StructuredNode):
    emid = IntegerProperty(unique_index=True)
    name = StringProperty()
    status = StringProperty(choices=LABEL_STATUS)
    releases = RelationshipFrom('Release', 'RELEASED_ON')


class Release(StructuredNode):
    emid = IntegerProperty(unique_index=True)
    name = StringProperty()
    link = StringProperty()
    release_type = StringProperty(choices=RELEASE_TYPES)
    rating = IntegerProperty()
    review_count = IntegerProperty()
    release_date = DateProperty()
    recorded_by = RelationshipFrom('Band', 'RECORDED')
    # released_on = RelationshipTo('Label', 'RELEASED_ON')
    # Don't forget to crawl for the label!


class Member(StructuredNode):
    emid = IntegerProperty(unique_index=True)
    link = StringProperty()
    visited = DateProperty()
    name = StringProperty()
    age = IntegerProperty()
    origin = StringProperty(choices=COUNTRY_NAMES)
    gender = StringProperty(choices=GENDER)
    played_in = RelationshipTo("Band", "PLAYED_IN", model=MemberRelationship)

    def get_origins(self):
        results, meta = db.cypher_query("MATCH (m:Member) return m.origin, count(*)")
        return results


class NeoModelStrategy(GraphDatabaseStrategy):

    config.DATABASE_URL = f'bolt://{settings.NEO4J_USERNAME}:{settings.NEO4J_PASSWORD}@{settings.NEO4J_IP_ADDRESS}:7687'
    config.ENCRYPTED_CONNECTION = False

    def __init__(self):
        self.logger = logging.getLogger('NeoModel')
        error_text = 'Cannot connect to the Neo4j database.'
        # Cheap test to test if the DB is available.
        try:
            Label.nodes.get(emid=-1)
        # No node with 'emid' of -1 available means the DB is up and running.
        except core.DoesNotExist:
            self.logger.info('Neo4j database is up and running.')
            pass
        except exceptions.AuthError:
            self.logger.error(f'{error_text} Check the credentials in the settings.py.')
            raise
        except exceptions.ServiceUnavailable:
            self.logger.error(f'{error_text} Make sure the database is up and running.')
            raise
        # Could happen while using an unsupported 4.x database.
        except exceptions.CypherSyntaxError as cse:
            if 'no longer supported' in cse.message:
                self.logger.error(f'{error_text} Make sure a 3.5.x database is used.')
            else:
                self.logger.error(f'{error_text}')
            raise
        except Exception as e:
            self.logger.error(f'{error_text}')
            raise

    def add_band_interface(self, band_dict):
        bands = Band.create_or_update(band_dict)

    def add_label_interface(self, label_dict):
        labels = Label.create_or_update(label_dict)

    def add_release_interface(self, release_dict):
        releases = Release.create_or_update(release_dict)

    def add_member_interface(self, member_dict):
        members = Member.create_or_update(member_dict)

    def band_recorded_release_interface(self, band_id, release_id):
        band = Band.nodes.get(emid=band_id)
        release = Release.nodes.get(emid=release_id)
        band.releases.disconnect(release)
        band.releases.connect(release)

    def member_played_in_band_interface(self, member_id, band_id, instrument, pseudonym, time_frame, status):
        member = Member.nodes.get(emid=member_id)
        band = Band.nodes.get(emid=band_id)
        member.played_in.disconnect(band)
        relation = member.played_in.connect(band)
        relation.instrument = instrument
        relation.pseudonym = pseudonym
        relation.time_frame = time_frame
        relation.status = status
        relation.save()

    def label_issued_release_interface(self, label_id, release_id):
        label = Label.nodes.get(emid=label_id)
        release = Release.nodes.get(emid=release_id)
        label.releases.connect(release)

    def get_all_links_interface(self) -> dict:
        all_links = {'bands': {}, 'artists': {}}

        self.logger.info('  Fetching known bands from database..')
        query = 'MATCH (b:Band) RETURN b.link, b.visited'
        bands, meta = db.cypher_query(query)
        for band_entry in bands:
            all_links['bands'][band_entry[0]] = band_entry[1]
        self.logger.info(f'    ...found {len(bands)}')

        self.logger.info('  Fetching known artists from database.')
        query = 'MATCH (n:Member) RETURN n.link, n.visited'
        artists, meta = db.cypher_query(query)
        for artist_entry in artists:
            all_links['artists'][artist_entry[0]] = artist_entry[1]
        self.logger.info(f'    ...found {len(artists)}')

        return all_links

    def export_bands_network_interface(self, country_shorts: list):
        if len(country_shorts) is not 0:
            bands = Band.nodes.filter(country__in=country_shorts)
        else:
            bands = Band.nodes.all()

        self.logger.info('Starting export of band network...')
        progress_bar = progressbar.ProgressBar(max_value=len(bands))
        band_relationships = {}
        relationship_filter = []

        # If IS_LIVE_MEMBER_IN_BAND is False all entries containing 'Live' will be filtered.
        for key, value in MEMBER_STATUS.items():
            if not settings.IS_LIVE_MEMBER_IN_BAND and 'Live' in value:
                pass
            else:
                relationship_filter.append(key)

        for band in bands:
            # We have a band; let's create an entry and see if it's linked to anything.
            band_relationships[band.emid] = {
                'name': band.name,
                'country': COUNTRY_NAMES[band.country],
                'relations': []
            }

            # Iterate over all members linked to the actual band and see if they're connected to other bands.
            for member in band.current_lineup.match(status__in=relationship_filter):
                for outer_band in member.played_in.match(status__in=relationship_filter):
                    is_already_connected = band.emid == outer_band.emid
                    # WARNING: This makes the graph undirected. We deliberately connect only the first instance:
                    # E.g. the connection from A to B is recorded but not the connection from B to A. This is extremely
                    # Fragile and does not work well (exporting is more complicated and the order of the dict matters).
                    # is_already_connected |= outer_band.emid in band_relationships.keys()
                    is_already_connected |= outer_band.emid in band_relationships[band.emid]['relations']

                    if not is_already_connected:
                        band_relationships[band.emid]['relations'].append(outer_band.emid)

            progress_bar.update(len(band_relationships))

        progress_bar.finish()
        print()
        return band_relationships

    def generate_country_report(self, country_short, bands):
        """ Generate a CountryReport from the given country short and list of bands.

        :param country_short: An ISO country short string.
        :param bands: A list of Band objects.
        :return: An instantiated CountryReport or None if any of the parameters were invalid.
        """

        if country_short not in COUNTRY_NAMES.keys():
            return None

        number_bands = len(bands)

        # No need to go further if there are no bands.
        if number_bands is 0:
            return None

        population = COUNTRY_POPULATION[country_short]

        # Bands per capita cannot be calculated with 0 people.
        if int(population) == 0:
            return None

        unique_members = {}
        progress_bar = progressbar.ProgressBar(max_value=number_bands)
        band_counter = 0
        member_counter = 0
        print(f'    Iterating {COUNTRY_NAMES[country_short]}\'s bands for gender and genre statistics.')

        # Init genders dict outside. Will be set in CountryReport object manually.
        genders = {}

        for gender in GENDER:
            genders[gender] = 0

        genres = {}
        gender_per_country = defaultdict(int)
        bands_per_year = defaultdict(int)
        sanity_bands = []

        for band in bands:
            sanity_bands.append(band.link)
            for genre in band.genres:
                if genre not in genres.keys():
                    genres[genre] = 1
                else:
                    genres[genre] += 1
            # Get the relationships of all members linked to the actual band.
            for member in band.current_lineup:
                if member.emid not in unique_members.keys():
                    unique_members[member.emid] = ""
                    # TODO: Fix multiple counting of artists.
                    genders[member.gender] += 1
                    member_counter += 1
                    gender_per_country[member.origin] += 1

            if band.formed is not None:
                bands_per_year[band.formed.year] += 1
            else:
                pass
                # Commented until I know what to do with unknown formation dates.
                # bands_per_year[-1] += 1
            band_counter += 1
            progress_bar.update(band_counter)

        progress_bar.finish()
        genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
        report = CountryReport(country_short, population, sanity_bands, genders, gender_per_country, genres, bands_per_year)

        return report

    def calc_bands_per_pop_interface(self, country_short, bands) -> dict:
        """Calculates the number of bands per 100k people for a given country and puts the data into a dict. The result
            will be empty for two error cases: The country population is smaller than one or if there are no bands
            available in the requested country.

        :param country_short: The country's ISO code to get the data from the database.
        :param bands: A list of bands used as basis for the calculation for the given country.
        :return: A dictionary with the the calculated data. Keys to data are the country short and the constants above.
            The dict will be empty for the error cases described above.
        """
        result = {}

        if len(bands) is 0:
            return result

        population = COUNTRY_POPULATION[country_short]

        if int(population) <= 1:
            return result

        result[POP_COUNTRY] = COUNTRY_NAMES[country_short]
        result[POP_BANDS] = str(len(bands))
        result[POP_POPULATION] = population
        bands_per_100k = len(bands) / (int(population) / 100000)
        result[POP_PER_100K] = f'{bands_per_100k:.2f}'

        unique_members = {}
        genders = {}

        for gender in GENDER:
            genders[gender] = 0

        progress_bar = progressbar.ProgressBar(max_value=len(bands))
        band_counter = 0
        member_counter = 0
        self.logger.info(f'Iterating {COUNTRY_NAMES[country_short]}\'s bands for gender and genre statistics.')
        genres = defaultdict(int)

        for band in bands:
            for genre in band.genres:
                genres[genre] += 1
            # Get the relationships of all members linked to the actual band.
            for member in band.current_lineup:
                if member.emid not in unique_members.keys():
                    unique_members[member.emid] = ""
                    # TODO: Fix multiple counting of artists.
                    genders[member.gender] += 1
                    member_counter += 1

            band_counter += 1
            progress_bar.update(band_counter)

        progress_bar.finish()
        result['Artists'] = member_counter

        for key, value in genders.items():
            percentage = (value / member_counter) * 100
            result[f'  {GENDER[key]}'] = f'{value} ({percentage:.2f}%).'

        result[RAW_GENRES] = genres

        return result

    def prepare_export_data(self, country_shorts: list, report_mode: ReportMode) -> ExportData:
        prepped_data = ExportData()
        self.logger.info('Preparing data export:')

        # Prep origin data.
        self.logger.info(' ┣ Fetching origins')
        origins, meta = db.cypher_query('MATCH (m:Member) return m.origin, count(*)')
        for origin in origins:
            prepped_data.origins[origin[0]] = origin[1]

        # Prep the gender raw data
        self.logger.info(' ┣ Fetching genders')
        if len(country_shorts) is 0:
            query = 'MATCH (b:Band)--(m:Member) RETURN b.country, m.origin, m.gender, count(*)'
        else:
            query = f'MATCH (b:Band)--(m:Member) WHERE b.country IN {country_shorts} RETURN b.country, m.origin, m.gender, count(*)'
        genders, meta = db.cypher_query(query)
        for gender_entry in genders:
            prepped_data.add_gender_country(band_origin=gender_entry[0], artist_origin=gender_entry[1],
                                            gender=gender_entry[2], count=gender_entry[3])

        # Prep the band origins.
        self.logger.info(' ┣ Fetching bands per country')
        if len(country_shorts) is 0:
            query = 'MATCH (b:Band) return b.country, count(*)'
        else:
            query = f'MATCH (b:Band) WHERE b.country IN {country_shorts} RETURN b.country, count(*)'
        bands, meta = db.cypher_query(query)
        for band_entry in bands:
            prepped_data.add_bands_per_country(band_entry[0], band_entry[1])

        # Prep the raw genre data.
        self.logger.info(' ┣ Fetching genres')
        if len(country_shorts) is 0:
            query = 'MATCH (b:Band) return b.country, b.genres, count(*)'
        else:
            query = f'MATCH (b:Band) WHERE b.country IN {country_shorts} RETURN b.country, b.genres, count(*)'
        genres, meta = db.cypher_query(query)
        for genre_entry in genres:
            prepped_data.add_genre_country(country=genre_entry[0], genres=genre_entry[1], count=genre_entry[2])

        # Prep the releases.
        self.logger.info(' ┣ Fetching releases')
        if len(country_shorts) is 0:
            query = 'MATCH (b:Band)--(r:Release) return b.country, b.name, r.name, r.rating, r.review_count, r.link,'
            'r.release_type, r.release_date'
        else:
            query = (f'MATCH (b:Band)--(r:Release) WHERE b.country IN {country_shorts} return b.country, b.name, '
                     'r.name, r.rating, r.review_count, r.link, r.release_type, r.release_date')
        releases, meta = db.cypher_query(query)

        for release in releases:
            prepped_data.add_release(country=release[0], band_name=release[1], release_name=release[2],
                                     rating=release[3], review_count=release[4], link=release[5],
                                     release_type=release[6], date=release[7])

        self.logger.info(' ┗ Data prepped.')

        return prepped_data

    def generate_report_interface(self, country_shorts: list, report_mode: ReportMode) -> DatabaseReport:
        """Generates a report with an analysis of the entire database into an handy object.

        :param country_shorts: The list either contains the ISO names of countries to analyze or it is empty. In that
            case we take all countries of all bands into account.
        :param report_mode: Determines the grade of details. E.g. if a detailed country report is needed or wanted
            because that only makes sense if all bands of all countries are in the database.
        :return: An initialized DatabaseReport object which can be processed further. Printing it is an obvious choice.
        """

        genders = {}
        artists_total = 0
        artists_per_country = defaultdict(int)

        self.logger.info('  Getting all artists.')

        for gender_key in GENDER:
            artists = Member.nodes.filter(gender__exact=gender_key)
            for artist in artists:
                artists_per_country[artist.origin] += 1

            genders[gender_key] = len(artists)
            artists_total += genders[gender_key]

        self.logger.info(f'    ...found {artists_total}')
        self.logger.info('  Getting all bands.')
        bands_all = Band.nodes.all()
        band_count = len(bands_all)
        bands_filtered = defaultdict(list)
        self.logger.info(f'    ...found {band_count}')
        self.logger.info('  Filtering bands.')

        # Two sets of bands are needed: First the bands from the requested countries and second all bands to calculate
        # e.g. percentages.
        if len(country_shorts) is 0:
            for band in bands_all:
                bands_filtered[band.country].append(band)
        else:
            for short in country_shorts:
                temp_bands = Band.nodes.filter(country__exact=short)
                # This guarantees that every key also has data behind it.
                if len(temp_bands) > 0:
                    bands_filtered[short] = temp_bands

        genres = defaultdict(int)
        release_types = []

        for release_type in settings.RELEASE_TYPES_REVIEW:
            release_types.append(RELEASE_TYPES[release_type])

        release_report = ReleaseReport(release_types)
        self.logger.info('  Prep done. Processing releases and genres.')
        progress_bar = progressbar.ProgressBar(max_value=len(bands_all))
        band_counter = 0

        for band in bands_all:
            for genre in band.genres:
                genres[genre] += 1

            if band.country in bands_filtered.keys():
                for release in band.releases:
                    release_report.process_release(
                        COUNTRY_NAMES[band.country], band.emid, band.name, release.name, release.link,
                        RELEASE_TYPES[release.release_type], release.release_date, release.rating, release.review_count
                    )

            band_counter += 1
            progress_bar.update(band_counter)

        progress_bar.finish()
        self.logger.info('  Releases processed. Creating database report.')
        db_report = DatabaseReport(band_count, genders, artists_total, artists_per_country, genres, release_report,
                                   report_mode)
        country_diff = set(country_shorts) - set(bands_filtered.keys())

        if len(country_diff) > 0:
            diff_report = 'No bands were found for: '

            for country in country_diff:
                diff_report += COUNTRY_NAMES[country] + ', '

            if len(country_diff) > 1:
                diff_report = diff_report[:-2]

            print(diff_report)

        if report_mode is ReportMode.CountryOn:
            self.logger.info('  Creating country reports.')
        # Prepping such a loop with 11k bands may well take 2.5s to 3.2s.
        for iso_short, bands in bands_filtered.items():
            db_report.add_country_report(self.generate_country_report(iso_short, bands))

        return db_report
