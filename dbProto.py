from neomodel import StructuredNode, StringProperty, RelationshipTo, RelationshipFrom, config

from graph.implNeoModel import *
from graph.metalGraph import *

db = GraphDatabaseContext(NeoModelStrategy())

actual_band = {'emid': 3540294014,
               'name': 'Barren Earth',
               'country': 'FI',
               'locations': ['Helsinki, Uusimaa'],
               'status': 'A',
               'themes': ['Darkness', 'Loss', 'Despair', 'Death'],
               'genres': ['Progressive Melodic Death', 'Doom Metal'],
               'formed': date(2007, 1, 1)
               }

db.add_band(actual_band)

actual_band = {'emid': 1,
               'name': 'Amorphis',
               'country': 'FI',
               'locations': ['Helsinki'],
               'status': 'A',
               'themes': ['War (early)', 'Death', 'Finnish legends', 'Kalevala'],
               'genres': ['Progressive/Death/Doom Metal (early)', 'Melodic Heavy Metal/Rock (later)'],
               'formed': date(1990, 1, 1)
               }

db.add_band(actual_band)

actual_label = {'emid': 8,
                'name': "Relapse Records",
                'status': "A"
                }

db.add_label(actual_label)

actual_label = {'emid': 2,
                'name': "Nuclear Blast",
                'status': "A"}

db.add_label(actual_label)

actual_album = {'emid': 295,
                'name': "The Karelian Isthmus",
                'type': "F",
                'release_date': date(1992, 11, 1),
                'rating': 85
                }

db.add_release(actual_album)
band_id = actual_band['emid']
db.band_recorded_release(actual_band['emid'], actual_album['emid'])

actual_album = {'emid': 226394,
                'name': "Skyforger",
                'type': "F",
                'release_date': date(2009, 5, 29),
                'rating': 87
                }

db.add_release(actual_album)
band_id = actual_band['emid']
db.band_recorded_release(actual_band['emid'], actual_album['emid'])


actual_member = {'emid': 2042,
                 'name': 'Olli-Pekka Laine'
                 }

db.add_member(actual_member)

actual_member = {'emid': 2012,
                 'name': 'Esa Holopainen'
                 }

db.add_member(actual_member)
db.member_played_in_band(2042, 1, 'Bass', 'Olli-Pekka Laine', [date(1990, 1, 1), date(2000, 1, 1), date(2017, 1, 1), date.today()])
db.member_played_in_band(2042, 3540294014, 'Bass, Vocals (backing)', 'Olli-Pekka Laine', [])
db.member_played_in_band(2012, 1, 'Guitars (lead)', 'Esa Holopainen', [])
db.label_issued_release(8, 295)
db.label_issued_release(2, 226394)

# config.DATABASE_URL = 'bolt://neo4j:em1@localhost:7687'
#
# class Book(StructuredNode):
#     title = StringProperty(unique_index=True)
#     author = RelationshipTo('Author', 'AUTHOR')
#
#
# class Author(StructuredNode):
#     name = StringProperty(unique_index=True)
#     books = RelationshipFrom('Book', 'AUTHOR')


#
# album = Album.nodes.get(emid=295)
# album.delete()
#
# albums = Album.create_or_update(
#     {
#         'emid': 295,
#         'name': "The Karelian Isthmus",
#         'type': "F",
#         'release_date': date(1992, 11, 1),
#         'rating': 85
#
#     }
# )
#
# albums[0].released_on.connect(labels[0])
# labels[0].releases.connect(albums[0])
#
# band = Band.nodes.get(emid=1)
# band.delete()
# band = Band.nodes.get(emid=3540294014)
# band.delete()
#
# bands = Band.create_or_update(
#     {
#         'emid': 1,
#         'name': 'Amorphis',
#         'country': 'FI',
#         'locations': [ 'Helsinki' ],
#         'status': 'A',
#         'themes': [ 'War (early)', 'Death', 'Finnish legends', 'Kalevala' ]
#
#     },
#     {
#         'emid': 3540294014,
#         'name': 'Barren Earth',
#         'country': 'FI',
#         'locations': ['Helsinki, Uusimaa'],
#         'status': 'A',
#         'themes': ['Progressive Melodic Death', 'Doom Metal']
#
#     }
# )
#
# bands[0].releases.connect(albums[0])
# albums[0].recorded_by.connect(bands[0])
# bands[0].releases.connect(albums[0])
#
# # band = Band.nodes.get(emid=3540294014)
# # band.delete()
#
# band = Band.nodes.get(emid=1)
# # band.delete()
#
# member = Member.nodes.get(emid=2042)
# member.delete()
# member = Member.nodes.get(emid=2012)
# member.delete()
#
#
# members = Member.create_or_update(
#     {
#         'emid': 2042,
#         'name': 'Olli-Pekka Laine'
#     },
#     {
#         'emid': 2012,
#         'name': 'Esa Holopainen'
#     }
# )
#
# # band.current_lineup.disconnect_all()
# # rel1 = band.current_lineup.connect(members[0])
# # rel1.instrument = 'Bass'
# # rel1.pseudonym = 'Olli-Pekka Laine'
# # rel1.save()
# # rel2 = band.current_lineup.connect(members[1])
# # rel2.instrument = 'Guitars (lead)'
# # rel2.pseudonym = 'Esa Holopainen'
# # rel2.save()
# rel1 = members[0].played_in.connect(band)
# rel1.instrument = 'Bass'
# rel1.pseudonym = 'Olli-Pekka Laine'
# rel1.save()
# members[0].save()
# rel2 = members[1].played_in.connect(band)
# rel2.instrument = 'Guitars (lead)'
# rel2.pseudonym = 'Esa Holopainen'
# rel2.save()
# members[1].save()
# # rel saves needed!
#
# for i_release in band.releases:
#     print(f"band release: {i_release}")
#
# for i_release in labels[0].releases:
#     print(f"label release: {i_release}")
#
# print(band.name)
# for i_member in band.current_lineup:
#     print(f"  member: {i_member}")
#
# band = Band.nodes.get(emid=3540294014)
# rel = members[0].played_in.connect(band)
# rel.instrument = 'Bass, Vocals (backing)'
# rel.pseudonym = 'Olli-Pekka Laine'
# rel.save()
# # rel = band.current_lineup.connect(members[0])
# # rel.instrument = 'Bass, Vocals (backing)'
# # rel.pseudonym = 'Olli-Pekka Laine'
# # rel.save()
#
# print(band.name)
# for i_member in band.current_lineup:
#     print(f"  member: {i_member}")
#
#
#
#
# # author = Author.nodes.get(name='J. K. Rowling')
# # book = Book.nodes.get(title='Harry potter and the..')
# # author.books.connect(book)
# # author.save()
# # book.save()
# #
# # for i_book in author.books:
# #     print(f"book: {i_book}")
# #
# # for i_author in book.author:
# #     print(f"author: {i_author}")
#
# # band.current_lineup.disconnect_all()
# # members[0].played_in.disconnect_all()
# # members[1].played_in.disconnect_all()
# #
# #
# # rel = members[0].played_in.connect(band)
# # rel.instrument = 'Bass'
# # rel.save()
# # rel = members[1].played_in.connect(band)
# # rel.instrument = 'Guitars (lead)'
# # rel.save()
#
#
# # harry_potter = Book(title='Harry potter and the..').save()
# # rowling =  Author(name='J. K. Rowling').save()
# # harry_potter.author.connect(rowling)
#
# # rowling = Author(name='J. K. Rowling').delete()
# #
# authors = Author.nodes.all()
# books = Book.nodes.all()
#
# for author in authors:
#     author.delete()
#
# for book in books:
#     book.delete()
#
# # harry_potter.author.connect(authors)
#
#
#
# print()
