from neomodel import StructuredNode, StringProperty, IntegerProperty, ArrayProperty, DateProperty, RelationshipTo, \
    RelationshipFrom, StructuredRel, config, core
from neomodel.match import *
from neo4j import exceptions
from graph.choices import *
from graph.metalGraph import GraphDatabaseStrategy, POP_BANDS, POP_PER_100K, POP_POPULATION, RAW_GENRES, POP_COUNTRY
from country_helper import COUNTRY_NAMES, COUNTRY_POPULATION
import logging
import settings
import progressbar
from graph.report import CountryReport, DatabaseReport


class MemberRelationship(StructuredRel):
    # TODO: Try to use multiple connections for each stint.
    time_frame = ArrayProperty()
    # start_date = DateProperty()
    # end_date = DateProperty()
    pseudonym = StringProperty()
    instrument = StringProperty()
    status = StringProperty(max_length=2, choices=MEMBER_STATUS)


class Band(StructuredNode):
    emid = IntegerProperty(unique_index=True)
    link = StringProperty()
    visited = DateProperty()
    name = StringProperty()
    country = StringProperty(max_length=2, choices=COUNTRY_NAMES)
    locations = ArrayProperty()
    status = StringProperty(max_length=1, choices=BAND_STATUS)
    formed = DateProperty()
    # active = ArrayProperty()
    themes = ArrayProperty()  # Should a theme be a node?
    genres = ArrayProperty()
    current_lineup = RelationshipFrom("Member", "PLAYED_IN", model=MemberRelationship)
    releases = RelationshipTo('Release', 'RECORDED')


class Label(StructuredNode):
    emid = IntegerProperty(unique_index=True)
    name = StringProperty()
    status = StringProperty(max_length=1, choices=LABEL_STATUS)
    releases = RelationshipFrom('Release', 'RELEASED_ON')


class Release(StructuredNode):
    emid = IntegerProperty(unique_index=True)
    name = StringProperty()
    type = StringProperty(max_lenght=1, choices=RELEASE_TYPES)
    rating = IntegerProperty()
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
    origin = StringProperty(max_length=2, choices=COUNTRY_NAMES)
    gender = StringProperty(max_length=1, choices=GENDER)
    played_in = RelationshipTo("Band", "PLAYED_IN", model=MemberRelationship)


class NeoModelStrategy(GraphDatabaseStrategy):

    config.DATABASE_URL = f'bolt://{settings.NEO4J_USERNAME}:{settings.NEO4J_PASSWORD}@{settings.NEO4J_IP_ADDRESS}:7687'

    def __init__(self):
        self.logger = logging.getLogger('NeoModel')
        error_text = "Cannot connect to Neo4j database."
        # Cheap test to test if the DB is available.
        try:
            Label.nodes.get(emid=-1)
        # No node with 'emid' of -1 available means the DB is up and running.
        except core.DoesNotExist:
            self.logger.info("Neo4j database is up and running.")
            pass
        except exceptions.AuthError:
            self.logger.error(f"{error_text} Check the credentials in the settings.py.")
            raise
        except exceptions.ServiceUnavailable:
            self.logger.error(f"{error_text} Make sure the database is up and running.")
            raise
        except Exception:
            self.logger.error(f"{error_text}")
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
        all_bands = Band.nodes.all()

        for band in all_bands:
            all_links['bands'][band.link] = band.visited

        all_artists = Member.nodes.all()

        for artist in all_artists:
            all_links['artists'][artist.link] = artist.visited

        return all_links

    def export_bands_network_interface(self, country_shorts: list):
        if len(country_shorts) is not 0:
            bands = Band.nodes.filter(country__in=country_shorts)
        else:
            bands = Band.nodes.all()

        self.logger.info('Starting export of band network...')
        progress_bar = progressbar.ProgressBar(max_value=len(bands))
        band_relationships = {}

        for band in bands:
            # We have a band; let's create an entry and see if it's linked to anything.
            band_relationships[band.emid] = {
                'name': band.name,
                'country': COUNTRY_NAMES[band.country],
                'relations': []
            }

            # Iterate over all members linked to the actual band and see if they're connected to other bands.
            for member in band.current_lineup:
                for outer_band in member.played_in:
                    is_already_connected = band.emid is outer_band.emid
                    is_already_connected |= outer_band.emid in band_relationships.keys()
                    is_already_connected |= outer_band.emid in band_relationships[band.emid]['relations']

                    if not is_already_connected:
                        band_relationships[band.emid]['relations'].append(outer_band.emid)

            progress_bar.update(len(band_relationships))

        progress_bar.finish()
        print()
        return band_relationships

    def generate_country_report(self, country_short, bands):
        number_bands = len(bands)
        if number_bands is 0:
            return None

        population = COUNTRY_POPULATION[country_short]

        if int(population) == 0:
            return None

        unique_members = {}
        progress_bar = progressbar.ProgressBar(max_value=number_bands)
        band_counter = 0
        member_counter = 0
        print(f'Iterating {COUNTRY_NAMES[country_short]}\'s bands for gender and genre statistics.')

        # Init genders dict outside. Will be set in CountryReport object manually.
        genders = {}
        for gender in GENDER:
            genders[gender] = 0

        genres = {}
        gender_per_country = {}

        for band in bands:
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
                    if member.origin not in gender_per_country:
                        gender_per_country[member.origin] = 1
                    else:
                        gender_per_country[member.origin] += 1

            band_counter += 1
            progress_bar.update(band_counter)

        progress_bar.finish()

        genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
        report = CountryReport(COUNTRY_NAMES[country_short], population, number_bands, genders, gender_per_country, genres)

        return report

    def calc_bands_per_pop_interface(self, country_short, bands) -> dict:
        """Calculates the number of bands per 100k people for a given country and puts the data into a dict. The result
            will be empty for two error cases: The country population is smaller than one or if there are no bands
            available in the requested country.

        :param country_short: The country's ISO code to get the data from the database.
        :param bands: A list of bands used as basis for the calculation for the given country.
        :return: A dictionary with the the calculated data. Keys to data are the country short and the constants above.
            The dict will be empty for the above described error cases.
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
        print(f'Iterating {COUNTRY_NAMES[country_short]}\'s bands for gender and genre statistics.')
        genres = {}

        for band in bands:
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

            band_counter += 1
            progress_bar.update(band_counter)

        progress_bar.finish()
        result['Artists'] = member_counter

        for key, value in genders.items():
            percentage = (value / member_counter) * 100
            result[f'  {GENDER[key]}'] = f'{value} ({percentage:.2f}%).'

        result[RAW_GENRES] = genres

        return result

    def generate_report_interface(self, country_shorts: list) -> DatabaseReport:
        """Generates a report with an analysis of the entire database into an handy object.

        :param country_shorts: The list either contains the ISO names of countries to analyse or it is empty. In that
            case we take all countries of all bands into account.
        :return: An initialized DatabaseReport object which can be processed further. Printing it is an obvious choice.
        """

        genders = {}
        artists_total = 0
        artists_per_country = {}

        for gender_key in GENDER:
            artists = Member.nodes.filter(gender__exact=gender_key)

            for artist in artists:
                if artist.origin not in artists_per_country:
                    artists_per_country[artist.origin] = 1
                else:
                    artists_per_country[artist.origin] += 1

            genders[gender_key] = len(artists)
            artists_total += genders[gender_key]

        band_count = len(Band.nodes.all())
        db_report = DatabaseReport(band_count, genders, artists_total, artists_per_country)

        self.logger.debug('>>> Getting all bands.')
        bands_all = Band.nodes.all()
        self.logger.debug('<<< Getting all bands.')
        bands_filtered = {}

        # Two sets of bands are needed: First the bands from the requested countries and second all bands to calculate
        # e.g. percentages.
        if len(country_shorts) is 0:
            for band in bands_all:
                if band.country not in bands_filtered.keys():
                    bands_filtered[band.country] = []
                bands_filtered[band.country].append(band)
        else:
            for short in country_shorts:
                temp_bands = Band.nodes.filter(country__exact=short)
                # This guarantees that every key also has data behind it.
                if len(temp_bands) > 0:
                    bands_filtered[short] = temp_bands

        country_diff = set(country_shorts) - set(bands_filtered.keys())

        if len(country_diff) > 0:
            diff_report = 'No bands were found for: '

            for country in country_diff:
                diff_report += COUNTRY_NAMES[country]

            if len(country_diff) > 1:
                diff_report = diff_report[:-2]

            print(diff_report)

        self.logger.debug('Bands prepped.')

        # Prepping such a loop with 11k bands may well take 2.5s to 3.2s.
        for iso_short, bands in bands_filtered.items():
            self.logger.debug(f'  Calc {iso_short}.')
            db_report.add_country_report(self.generate_country_report(iso_short, bands))

        return db_report
