from neomodel import StructuredNode, StringProperty, IntegerProperty, ArrayProperty, DateProperty, RelationshipTo, RelationshipFrom, StructuredRel, config
import time
from datetime import date

config.DATABASE_URL = 'bolt://neo4j:em1@localhost:7687'

COUNTRIES = (
    ('AF', 'Afghanistan'),
    ('AX', 'Åland Islands'),
    ('AL', 'Albania'),
    ('DZ', 'Algeria'),
    ('AS', 'American Samoa'),
    ('AD', 'Andorra'),
    ('AO', 'Angola'),
    ('AI', 'Anguilla'),
    ('AQ', 'Antarctica'),
    ('AG', 'Antigua and Barbuda'),
    ('AR', 'Argentina'),
    ('AM', 'Armenia'),
    ('AW', 'Aruba'),
    ('AU', 'Australia'),
    ('AT', 'Austria'),
    ('AZ', 'Azerbaijan'),
    ('BS', 'Bahamas'),
    ('BH', 'Bahrain'),
    ('BD', 'Bangladesh'),
    ('BB', 'Barbados'),
    ('BY', 'Belarus'),
    ('BE', 'Belgium'),
    ('BZ', 'Belize'),
    ('BJ', 'Benin'),
    ('BM', 'Bermuda'),
    ('BT', 'Bhutan'),
    ('BO', 'Bolivia'),
    ('BQ', 'Bonaire), Sint Eustatius and Saba'),
    ('BA', 'Bosnia and Herzegovina'),
    ('BW', 'Botswana'),
    ('BV', 'Bouvet Island'),
    ('BR', 'Brazil'),
    ('IO', 'British Indian Ocean Territory'),
    ('BN', 'Brunei Darussalam'),
    ('BG', 'Bulgaria'),
    ('BF', 'Burkina Faso'),
    ('BI', 'Burundi'),
    ('KH', 'Cambodia'),
    ('CM', 'Cameroon'),
    ('CA', 'Canada'),
    ('CV', 'Cape Verde'),
    ('KY', 'Cayman Islands'),
    ('CF', 'Central African Republic'),
    ('TD', 'Chad'),
    ('CL', 'Chile'),
    ('CN', 'China'),
    ('CX', 'Christmas Island'),
    ('CC', 'Cocos (Keeling) Islands'),
    ('CO', 'Colombia'),
    ('KM', 'Comoros'),
    ('CG', 'Congo'),
    ('CD', 'Congo'),
    ('CK', 'Cook Islands'),
    ('CR', 'Costa Rica'),
    ('CI', "Côte d'Ivoire"),
    ('HR', 'Croatia'),
    ('CU', 'Cuba'),
    ('CW', 'Curaçao'),
    ('CY', 'Cyprus'),
    ('CZ', 'Czech Republic'),
    ('DK', 'Denmark'),
    ('DJ', 'Djibouti'),
    ('DM', 'Dominica'),
    ('DO', 'Dominican Republic'),
    ('EC', 'Ecuador'),
    ('EG', 'Egypt'),
    ('SV', 'El Salvador'),
    ('GQ', 'Equatorial Guinea'),
    ('ER', 'Eritrea'),
    ('EE', 'Estonia'),
    ('ET', 'Ethiopia'),
    ('FK', 'Falkland Islands (Malvinas)'),
    ('FO', 'Faroe Islands'),
    ('FJ', 'Fiji'),
    ('FI', 'Finland'),
    ('FR', 'France'),
    ('GF', 'French Guiana'),
    ('PF', 'French Polynesia'),
    ('TF', 'French Southern Territories'),
    ('GA', 'Gabon'),
    ('GM', 'Gambia'),
    ('GE', 'Georgia'),
    ('DE', 'Germany'),
    ('GH', 'Ghana'),
    ('GI', 'Gibraltar'),
    ('GR', 'Greece'),
    ('GL', 'Greenland'),
    ('GD', 'Grenada'),
    ('GP', 'Guadeloupe'),
    ('GU', 'Guam'),
    ('GT', 'Guatemala'),
    ('GG', 'Guernsey'),
    ('GN', 'Guinea'),
    ('GW', 'Guinea-Bissau'),
    ('GY', 'Guyana'),
    ('HT', 'Haiti'),
    ('HM', 'Heard Island and McDonald Islands'),
    ('VA', 'Holy See (Vatican City State)'),
    ('HN', 'Honduras'),
    ('HK', 'Hong Kong'),
    ('HU', 'Hungary'),
    ('IS', 'Iceland'),
    ('IN', 'India'),
    ('ID', 'Indonesia'),
    ('IR', 'Iran'),
    ('IQ', 'Iraq'),
    ('IE', 'Ireland'),
    ('IM', 'Isle of Man'),
    ('IL', 'Israel'),
    ('IT', 'Italy'),
    ('JM', 'Jamaica'),
    ('JP', 'Japan'),
    ('JE', 'Jersey'),
    ('JO', 'Jordan'),
    ('KZ', 'Kazakhstan'),
    ('KE', 'Kenya'),
    ('KI', 'Kiribati'),
    ('KP', 'North Korea'),
    ('KR', 'South Korea'),
    ('KW', 'Kuwait'),
    ('KG', 'Kyrgyzstan'),
    ('LA', 'Laos'),
    ('LV', 'Latvia'),
    ('LB', 'Lebanon'),
    ('LS', 'Lesotho'),
    ('LR', 'Liberia'),
    ('LY', 'Libya'),
    ('LI', 'Liechtenstein'),
    ('LT', 'Lithuania'),
    ('LU', 'Luxembourg'),
    ('MO', 'Macao'),
    ('MK', 'Macedonia'),
    ('MG', 'Madagascar'),
    ('MW', 'Malawi'),
    ('MY', 'Malaysia'),
    ('MV', 'Maldives'),
    ('ML', 'Mali'),
    ('MT', 'Malta'),
    ('MH', 'Marshall Islands'),
    ('MQ', 'Martinique'),
    ('MR', 'Mauritania'),
    ('MU', 'Mauritius'),
    ('YT', 'Mayotte'),
    ('MX', 'Mexico'),
    ('FM', 'Micronesia'),
    ('MD', 'Moldova'),
    ('MC', 'Monaco'),
    ('MN', 'Mongolia'),
    ('ME', 'Montenegro'),
    ('MS', 'Montserrat'),
    ('MA', 'Morocco'),
    ('MZ', 'Mozambique'),
    ('MM', 'Myanmar'),
    ('NA', 'Namibia'),
    ('NR', 'Nauru'),
    ('NP', 'Nepal'),
    ('NL', 'Netherlands'),
    ('NC', 'New Caledonia'),
    ('NZ', 'New Zealand'),
    ('NI', 'Nicaragua'),
    ('NE', 'Niger'),
    ('NG', 'Nigeria'),
    ('NU', 'Niue'),
    ('NF', 'Norfolk Island'),
    ('MP', 'Northern Mariana Islands'),
    ('NO', 'Norway'),
    ('OM', 'Oman'),
    ('PK', 'Pakistan'),
    ('PW', 'Palau'),
    ('PS', 'Palestine), State of'),
    ('PA', 'Panama'),
    ('PG', 'Papua New Guinea'),
    ('PY', 'Paraguay'),
    ('PE', 'Peru'),
    ('PH', 'Philippines'),
    ('PN', 'Pitcairn'),
    ('PL', 'Poland'),
    ('PT', 'Portugal'),
    ('PR', 'Puerto Rico'),
    ('QA', 'Qatar'),
    ('RE', 'Réunion'),
    ('RO', 'Romania'),
    ('RU', 'Russian Federation'),
    ('RW', 'Rwanda'),
    ('BL', 'Saint Barthélemy'),
    ('SH', 'Saint Helena), Ascension and Tristan da Cunha'),
    ('KN', 'Saint Kitts and Nevis'),
    ('LC', 'Saint Lucia'),
    ('MF', 'Saint Martin (French part)'),
    ('PM', 'Saint Pierre and Miquelon'),
    ('VC', 'Saint Vincent and the Grenadines'),
    ('WS', 'Samoa'),
    ('SM', 'San Marino'),
    ('ST', 'Sao Tome and Principe'),
    ('SA', 'Saudi Arabia'),
    ('SN', 'Senegal'),
    ('RS', 'Serbia'),
    ('SC', 'Seychelles'),
    ('SL', 'Sierra Leone'),
    ('SG', 'Singapore'),
    ('SX', 'Sint Maarten (Dutch part)'),
    ('SK', 'Slovakia'),
    ('SI', 'Slovenia'),
    ('SB', 'Solomon Islands'),
    ('SO', 'Somalia'),
    ('ZA', 'South Africa'),
    ('GS', 'South Georgia and the South Sandwich Islands'),
    ('SS', 'South Sudan'),
    ('ES', 'Spain'),
    ('LK', 'Sri Lanka'),
    ('SD', 'Sudan'),
    ('SR', 'Suriname'),
    ('SJ', 'Svalbard and Jan Mayen'),
    ('SZ', 'Swaziland'),
    ('SE', 'Sweden'),
    ('CH', 'Switzerland'),
    ('SY', 'Syrian Arab Republic'),
    ('TW', 'Taiwan), Province of China'),
    ('TJ', 'Tajikistan'),
    ('TZ', 'Tanzania), United Republic of'),
    ('TH', 'Thailand'),
    ('TL', 'Timor-Leste'),
    ('TG', 'Togo'),
    ('TK', 'Tokelau'),
    ('TO', 'Tonga'),
    ('TT', 'Trinidad and Tobago'),
    ('TN', 'Tunisia'),
    ('TR', 'Turkey'),
    ('TM', 'Turkmenistan'),
    ('TC', 'Turks and Caicos Islands'),
    ('TV', 'Tuvalu'),
    ('UG', 'Uganda'),
    ('UA', 'Ukraine'),
    ('AE', 'United Arab Emirates'),
    ('GB', 'United Kingdom'),
    ('US', 'United States'),
    ('UM', 'United States Minor Outlying Islands'),
    ('UY', 'Uruguay'),
    ('UZ', 'Uzbekistan'),
    ('VU', 'Vanuatu'),
    ('VE', 'Venezuela'),
    ('VN', 'Viet Nam'),
    ('VG', 'Virgin Islands), British'),
    ('VI', 'Virgin Islands), U.S.'),
    ('WF', 'Wallis and Futuna'),
    ('EH', 'Western Sahara'),
    ('YE', 'Yemen'),
    ('ZM', 'Zambia'),
    ('ZW', 'Zimbabwe')
)

STATUS = (
    ('A', 'Active'),
    ('H', 'On hold'),
    ('C', 'Changed name'),
    ('S', 'Split-up'),
    ('U', 'Unknown')
)


LABEL_STATUS = (
    ('A', 'active'),
    ('C', 'closed'),
    ('U', 'unknown')
)


ALBUM_TYPES = (
    ('D', 'Demo'),
    ('F', 'Full-length'),
    ('S', 'Single'),
    ('T', 'Split'),
    ('L', 'Live album'),
    ('C', 'Compilation'),
    ('E', 'EP'),
    ('V', 'Video'),
    ('B', 'Boxed set')
)


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
    current_lineup = RelationshipTo("Member", "MEMBER", model=MemberRelationship)
    releases = RelationshipFrom('Album', 'RELEASED_ON')


class Label(StructuredNode):
    emid = IntegerProperty(unique_index=True)
    name = StringProperty()
    status = StringProperty(max_length=1, choices=LABEL_STATUS)
    releases = RelationshipFrom('Album', 'RELEASED')


class Album(StructuredNode):
    emid = IntegerProperty(unique_index=True)
    name = StringProperty()
    type = StringProperty(max_lenght=1, choices=ALBUM_TYPES)
    rating = IntegerProperty()
    release_date = DateProperty()
    released_on = RelationshipTo('Label', 'RELEASED_ON')
    recorded_by = RelationshipTo('Band', 'RECORDED_BY')
    # Don't forget to crawl for the label!


class Member(StructuredNode):
    emid = IntegerProperty(unique_index=True)
    name = StringProperty()
    played_in = RelationshipTo("Band", "PLAYED_IN", model=MemberRelationship)


class Book(StructuredNode):
    title = StringProperty(unique_index=True)
    author = RelationshipTo('Author', 'AUTHOR')


class Author(StructuredNode):
    name = StringProperty(unique_index=True)
    books = RelationshipFrom('Book', 'AUTHOR')


label = Label.nodes.get(emid=8)
label.delete()

labels = Label.create_or_update(
    {
        'emid': 8,
        'name': "Relapse Records",
        'status': "A"
    }
)

album = Album.nodes.get(emid=295)
album.delete()

albums = Album.create_or_update(
    {
        'emid': 295,
        'name': "The Karelian Isthmus",
        'type': "F",
        'release_date': date(1992, 11, 1),
        'rating': 85

    }
)

albums[0].released_on.connect(labels[0])
labels[0].releases.connect(albums[0])

bands = Band.create_or_update(
    {
        'emid': 1,
        'name': 'Amorphis',
        'country': 'FI',
        'locations': [ 'Helsinki' ],
        'status': 'A',
        'themes': [ 'War (early)', 'Death', 'Finnish legends', 'Kalevala' ]

    },
    {
        'emid': 3540294014,
        'name': 'Barren Earth',
        'country': 'FI',
        'locations': ['Helsinki, Uusimaa'],
        'status': 'A',
        'themes': ['Progressive Melodic Death', 'Doom Metal']

    }
)

bands[0].releases.connect(albums[0])
albums[0].recorded_by.connect(bands[0])
bands[0].releases.connect(albums[0])

# band = Band.nodes.get(emid=3540294014)
# band.delete()

band = Band.nodes.get(emid=1)
# band.delete()

member = Member.nodes.get(emid=2042)
member.delete()
member = Member.nodes.get(emid=2012)
member.delete()


members = Member.create_or_update(
    {
        'emid': 2042,
        'name': 'Olli-Pekka Laine'
    },
    {
        'emid': 2012,
        'name': 'Esa Holopainen'
    }
)

# band.current_lineup.disconnect_all()
rel1 = band.current_lineup.connect(members[0])
rel1.instrument = 'Bass'
rel1.pseudonym = 'Olli-Pekka Laine'
rel1.save()
rel2 = band.current_lineup.connect(members[1])
rel2.instrument = 'Guitars (lead)'
rel2.pseudonym = 'Esa Holopainen'
rel2.save()
rel1 = members[0].played_in.connect(band)
rel1.instrument = 'Bass'
rel1.pseudonym = 'Olli-Pekka Laine'
rel1.save()
members[0].save()
rel2 = members[1].played_in.connect(band)
rel2.instrument = 'Guitars (lead)'
rel2.pseudonym = 'Esa Holopainen'
rel2.save()
members[1].save()
# rel saves needed!

for i_release in band.releases:
    print(f"band release: {i_release}")

for i_release in labels[0].releases:
    print(f"label release: {i_release}")

band = Band.nodes.get(emid=3540294014)
rel = members[0].played_in.connect(band)
rel.instrument = 'Bass, Vocals (backing)'
rel.pseudonym = 'Olli-Pekka Laine'
rel.save()
rel = band.current_lineup.connect(members[0])
rel.instrument = 'Bass, Vocals (backing)'
rel.pseudonym = 'Olli-Pekka Laine'
rel.save()

for i_member in band.current_lineup:
    print(f"member: {i_member}")




# author = Author.nodes.get(name='J. K. Rowling')
# book = Book.nodes.get(title='Harry potter and the..')
# author.books.connect(book)
# author.save()
# book.save()
#
# for i_book in author.books:
#     print(f"book: {i_book}")
#
# for i_author in book.author:
#     print(f"author: {i_author}")

# band.current_lineup.disconnect_all()
# members[0].played_in.disconnect_all()
# members[1].played_in.disconnect_all()
#
#
# rel = members[0].played_in.connect(band)
# rel.instrument = 'Bass'
# rel.save()
# rel = members[1].played_in.connect(band)
# rel.instrument = 'Guitars (lead)'
# rel.save()


# harry_potter = Book(title='Harry potter and the..').save()
# rowling =  Author(name='J. K. Rowling').save()
# harry_potter.author.connect(rowling)

# rowling = Author(name='J. K. Rowling').delete()
#
authors = Author.nodes.all()
books = Book.nodes.all()

for author in authors:
    author.delete()

for book in books:
    book.delete()

# harry_potter.author.connect(authors)



print()
