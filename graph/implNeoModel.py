from neomodel import StructuredNode, StringProperty, IntegerProperty, ArrayProperty, DateProperty, RelationshipTo, RelationshipFrom, StructuredRel, config
from datetime import date
from graph.choices import *
from graph.metalGraph import *

class MemberRelationship(StructuredRel):
    # start_date = DateProperty()
    # end_date = DateProperty()
    pseudonym = StringProperty()
    instrument = StringProperty()


class Band(StructuredNode):
    emid = IntegerProperty(unique_index=True)
    name = StringProperty()
    country = StringProperty(max_length=2, choices=COUNTRIES)
    locations = ArrayProperty()
    status = StringProperty(max_length=1, choices=STATUS)
    formed = DateProperty()

    themes = ArrayProperty()  # Should a theme be a node?
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
    released_on = RelationshipTo('Label', 'RELEASED_ON')
    recorded_by = RelationshipFrom('Band', 'RECORDED')
    # Don't forget to crawl for the label!


class Member(StructuredNode):
    emid = IntegerProperty(unique_index=True)
    name = StringProperty()
    played_in = RelationshipTo("Band", "PLAYED_IN", model=MemberRelationship)


class NeoModelStrategy(GraphDatabaseStrategy):

    config.DATABASE_URL = 'bolt://neo4j:em2@localhost:7687'

    def add_band_interface(self, band_dict):
        bands = Band.create_or_update(band_dict)

    def add_label_interface(self, label_dict):
        labels = Label.create_or_update(label_dict)

    def add_release_interface(self, release_dict):
        albums = Release.create_or_update(release_dict)

    def band_recorded_release_interface(self, band_id, release_id):
        band = Band.nodes.get(emid=band_id)
        release = Release.nodes.get(emid=release_id)
        band.releases.connect(release)
        release.recorded_by.connect(band)

    # label = Label.nodes.get(emid=8)
    # label.delete()
