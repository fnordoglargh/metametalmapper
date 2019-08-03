from neomodel import StructuredNode, StringProperty, IntegerProperty, ArrayProperty, DateProperty, RelationshipTo, \
    RelationshipFrom, StructuredRel, config, core
from neomodel.match import *
from neo4j import exceptions
from graph.choices import *
from graph.metalGraph import GraphDatabaseStrategy
from country_helper import COUNTRY_NAMES
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

    def export_bands_network_interface(self, country_short):
        if country_short is not None:
            bands = Band.nodes.filter(country__exact=country_short)
        else:
            bands = Band.nodes.all()

        self.logger.info('Starting export of band network...')
        progress_bar = progressbar.ProgressBar(max_value=len(bands))
        band_relationships = {}

        for band in bands:
            # We have a band; let's create an entry and see if it's linked no anything.
            band_relationships[band.emid] = {
                'name': band.name,
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
