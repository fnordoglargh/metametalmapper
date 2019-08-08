from neomodel import StructuredNode, StringProperty, IntegerProperty, ArrayProperty, DateProperty, RelationshipTo, \
    RelationshipFrom, StructuredRel, config, core
from neomodel.match import *
from neo4j import exceptions
from graph.choices import *
from graph.metalGraph import GraphDatabaseStrategy, POP_BANDS, POP_PER_100K, POP_POPULATION, prettify_calc_result
from country_helper import COUNTRY_NAMES, COUNTRY_POPULATION
import logging
import settings
import progressbar


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
            # We have a band; let's create an entry and see if it's linked no anything.
            band_relationships[band.emid] = {
                'name': band.name,
                'country': COUNTRY_NAMES[band.country],
                'relations': []
            }

            # Get the relationships of all members linked to the actual band and see if they're connected to other
            # bands.
            outer_rel_definition = dict(node_class=Member, direction=INCOMING, relation_type=None, model=None)
            outer_rel_traversal = Traversal(band, Band.__label__, outer_rel_definition)
            actual_band_relations = outer_rel_traversal.all()

            # For each band member we get all connections to all bands (including the actual one).
            for rel in actual_band_relations:
                inner_rel_definition = dict(node_class=Band, direction=OUTGOING, relation_type=None, model=None)
                inner_rel_traversal = Traversal(rel, Member.__label__, inner_rel_definition)
                all_linked_bands = inner_rel_traversal.all()

                for linked_band in all_linked_bands:
                    is_already_connected = band.emid is linked_band.emid
                    is_already_connected |= linked_band.emid in band_relationships.keys()
                    is_already_connected |= linked_band.emid in band_relationships[band.emid]['relations']

                    if not is_already_connected:
                        band_relationships[band.emid]['relations'].append(linked_band.emid)

            progress_bar.update(len(band_relationships))

        progress_bar.finish()
        print()
        return band_relationships

    def calc_bands_per_pop_interface(self, country_short) -> dict:
        """Calculates the number of bands per 100k people for a given country and puts the data into a dict. The result
            will be empty for two error cases: The country population is smaller than one or if there are no bands
            available in the requested country.

        :param country_short: The country's ISO code to get the data from the database.
        :return: A dictionary with the the calculated data. Keys to data are the country short and the constants above.
            The dict will be empty for the above described error cases.
        """
        result = {}
        bands = Band.nodes.filter(country__exact=country_short)

        if len(bands) is 0:
            return result

        population = COUNTRY_POPULATION[country_short]

        if int(population) <= 1:
            return result

        country_long = COUNTRY_NAMES[country_short]
        result[country_long] = {}
        result[country_long][POP_BANDS] = str(len(bands))
        result[country_long][POP_POPULATION] = population
        bands_per_100k = len(bands) / (int(population) / 100000)
        result[country_long][POP_PER_100K] = f'{bands_per_100k:.2f}'

        unique_members = []
        genders = {}

        for gender in GENDER:
            genders[gender] = 0

        progress_bar = progressbar.ProgressBar(max_value=len(bands))
        band_counter = 0
        member_counter = 0
        print(f'Iterating {COUNTRY_NAMES[country_short]}\'s bands for gender statistics.')

        for band in bands:
            # Get the relationships of all members linked to the actual band and see if they're connected to other
            # bands.
            for member in band.current_lineup:
                if member.emid not in unique_members:
                    unique_members.append(member.emid)
                    genders[member.gender] += 1
                    member_counter += 1

            band_counter += 1
            progress_bar.update(band_counter)

        progress_bar.finish()
        result[country_long]['Artists'] = member_counter

        for key, value in genders.items():
            percentage = (value / member_counter) * 100
            result[country_long][f'  {GENDER[key]}'] = f'{value} ({percentage:.2f}%).'

        return result

    def raw_analysis_interface(self):
        """Prints some raw analysis of the entire database to the std out: The amount of bands and artists and the
            number of countries they are from plus a gender breakdown of all artists.
        """
        print('Prepping bands.')
        bands = Band.nodes.all()
        band_per_country = []
        calc_results = []

        for band in bands:
            if band.country not in band_per_country:
                band_per_country.append(band.country)
                calc_results.append(self.calc_bands_per_pop_interface(band.country))

        print(f'The database contains {len(bands)} bands from {len(band_per_country)} countries.')

        for calc_result in calc_results:
            print(prettify_calc_result(calc_result))

        print('Prepping artists.')
        all_artists = Member.nodes.all()
        amount_artists = len(all_artists)
        artist_per_country = []

        for artist in all_artists:
            if artist.origin not in artist_per_country:
                artist_per_country.append(artist.origin)

        print(f'The database contains {amount_artists} artists from {len(artist_per_country)} countries.')

        for key, value in GENDER.items():
            artist_gender = Member.nodes.filter(gender__exact=key)
            percentage = (len(artist_gender) / amount_artists) * 100
            print(f'  {len(artist_gender)} ({percentage:.2f}%) artists are {value}.')
