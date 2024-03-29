# Databases

Meta Metal Mapper uses graph databases to store data and currently only uses
Neo4j.

A [graph database](https://en.wikipedia.org/wiki/Graph_database) is ideal to
store data from M-A for further analysis. Entities like e.g. bands and their
members are called nodes. They are connected through edges storing e.g. data,
like the pseudonym a member used in a certain band or which instruments were
played.

Other databases can easily be added through implementing the
`GraphDatabaseStrategy` ([Strategy pattern](https://en.wikipedia.org/wiki/Strategy_pattern))
found in `metalGraph.py`.

## Neo4j database

### Settings file

Use `settings.py` to set the following properties:

    NEO4J_USERNAME = "neo4j"
    NEO4J_PASSWORD = "CHANGEME"
    NEO4J_IP_ADDRESS = "localhost"

### Nodes

Meta Metal Mapper defines the following nodes and properties.

#### Band

A _band_ is a node connected to members through a `played_in` relationship and
has the following properties:

* `emid`: The band ID used on M-A.
* `name`: Name of the band.
* `country`: The country of origin as a two letter ISO code. Uses
  `COUNTRY_NAMES` from `country_helper.py` to ensure validity.
* `locations`: Locations where the bands was active in.
* `status`: Short form of the `BAND_STATUS`. One of six possible values.
* `formed`: M-A only uses years in for dates on the band page. To get it somehow
  right, we use Jan 1st and Dec 31st for as start and end dates.
* `themes`: Themes used in the lyrics.
* `genres`: Genres the band played. This could be a relationship or a
  collection.  Need to learn a bit more about the string and how to cut it up.
* `current_lineup`: Relationship (PLAYED_IN) from a `Member`.
* `releases`: Relationship (RECORDED) from a `Release`.

#### Member

A _member_ is a node connected to bands through a `played_in` relationship and
has the following properties:

* `emid`:  The artist ID used on M-A.
* `name`: Name of the band member. Note that pseudonyms or instruments are part
  of the `MemberRelationship`.
* `age`: Age of the member at the time of crawling. It might contain -1 as a
  value if the age is unknown.
* `gender`: Gender from `GENDER` dictionary.
* `played_in`: Relationship to a band.

#### Release

A _release_ is a node connected to a band through a _recorded_ relationship and
has the following properties:

* `emid`: The release ID used on M-A.
* `name`: Name of the release.
* `type`: The type of the release. Validity ensured by `RELEASE_TYPES`.
* `rating`: The rating of the release (in percent). If it has not been rated on
  M-A, the value is set to -1.
* `release_date`: The _year_ when the release first was available.
* `recorded_by`: Relationship to a band.

### Relationships

#### PLAYED_IN

Is directed from a Member to a Band and uses the model `MemberRelationship`.

### Abbreviations/Lookup Dictionaries

The Keys are used inside the database and line up with the value which is used
in M-A.

#### GENDER

    'M': 'Male',
    'F': 'Female',
    'U': 'Unknown',
    'O': 'Other',
    'N': 'Non-binary'

#### COUNTRY_NAMES

    ...
    'NF': 'Norfolk Island',
    'MP': 'Northern Mariana Islands',
    'NO': 'Norway',
    ...

#### BAND_STATUS

    'A': 'Active',
    'H': 'On hold',
    'C': 'Changed name',
    'S': 'Split-up',
    'U': 'Unknown',
    'D': 'Disputed'

#### RELEASE_TYPES

    'D': 'Demo',
    'F': 'Full-length',
    'S': 'Single',
    'T': 'Split',
    'L': 'Live album',
    'C': 'Compilation',
    'E': 'EP',
    'V': 'Video',
    'B': 'Boxed set',
    'P': 'Split video',
    'O': 'Collaboration'

#### MEMBER_STATUS

    'C': 'Current',
    'L': 'Last known',
    'P': 'Past',
    'CL': 'Current (Live)',
    'PL': 'Past (Live)',
    'LL': 'Last known (Live)'

