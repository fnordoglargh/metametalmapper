# Metal Mapper
_Metal Mapper_ is Python program and intended to be the basis to develop a toolset to access data of 
[Encyclopaedia Metallum: The Metal Archives](https://www.metal-archives.com/) (MA) and query said data. The
_Others_ section of [Add-ons](https://www.metal-archives.com/content/tools) links to two projects showcasing
interesting ways to visualize the _Metal Archives'_ data:

* [Metal Map](https://metal-map.com/): A visualization of bands by country displayed on a map, with data from M-A.
* [Metal Graph](http://metal-graph.com/): A graph showing the connections between Norwegian black metal bands, 
    with data from M-A. 

## Highlights

* Generates lists for bands to crawl based on countries, regions or the entire database.
* Extracts information on bands, their band members and releases.
* Links the information with the ME IDs of the entities.
* Saves everything in a JSON file for further analysis. 

## Basics

### Countries

Countries on MA and this tool are represented in [ISO 3166](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
two letter format. Whenever you read _NN_ in context with countries, a two letter country code is meant.

A list of all countries with at least one band is shown on calling with the switch `-l`.

### Regions

A _region_ is a group of countries defined inside the main python file. Available regions can shown on calling 
with the switch `-l`.

A popular region is are the nordic countries *NC* (containing Denmark, Sweden, Norway, Iceland, Finland, 
Greenland, Faroe Islands, Åland Islands, Svalbard and Jan Mayen).

## How to use

`metalMaper.py`, when called without switches, shows a list of compiler switches and some hints
how to use them.

### Use Case: Crawl Norway

1. Get all Norwegian bands: `metalMaper.py -c NO`
2. Crawl all bands in Norway: `metalMaper.py -b -f bands-NO.lnks`
3. Do a rudimentary of all distinct music styles in the resulting database: 
`metalMaper.py -y databases\db-2019-01-02_22-32-25.json`. (Make sure you use the the name of your generated
JSON file.)

### Bootstrapping: Crawl _all_ available countries

Calling with the switch `-a` will:

1. Generate a list of all countries (from MA's [by country page](https://www.metal-archives.com/browse/country))
with at least one band entry.
2. Extract the link for every band in every country and save the links in a folder with the same name.
    The name of the files follows this simple scheme: `bands-NN.lnks` where NN is the two letter short form.
    The contents of an `.lnks` file looks like this:
    ```
    Akollonizer/3540362756
    Among_the_Mist/7576
    Nami/3540321763
    Persefone/12779
    ```
    Together with `https://www.metal-archives.com/bands/` a fully fledged link to every band can be generated.
    
### Boostrapping at smaller scale: Crawl a country or a region

If you're not interested in getting the band links for all countries you can either 

* start with the switch `-c NN` to crawl all bands in exactly one country **or** 
* call with `-r NN` where NN is the key of the region you want to crawl.

### JSON database layout

```
.
├── artists
│  └── id
│     ├── bands
│     │  └── id
│     │     ├── Current
│     │     │  ├── [list]
│     │     │  └── instrument
│     │     │     └── [list]
│     │     ├── Current (Live)
│     │     │  ├── [list]
│     │     │  └── instrument
│     │     │     └── [list]
│     │     ├── Past
│     │     │  ├── [list]
│     │     │  └── instrument
│     │     │     └── [list]
│     │     ├── Past (Live)
│     │     │  ├── [list]
│     │     │  └── instrument
│     │     │     └── [list]
│     │     └── pseudonym
│     └── link
├── bands
│  └── id
│     ├── active
│     │  └── [list]
│     ├── country
│     ├── formed
│     ├── genre
│     │  └── [list]
│     ├── lineup
│     │  ├── Current
│     │  │  └── [list]
│     │  ├── Current (Live)
│     │  │  └── [list]
│     │  ├── Past
│     │  │  └── [list]
│     │  └── Past (Live)
│     │     └── [list]
│     ├── link
│     ├── location
│     ├── name
│     ├── status
│     └── theme
│        └── [list]
└── labels
   └── id
      ├── link
      └── name
```

## Known Issues

* Countries for bands are saved as:
    ```
    "country": {
      "Netherlands": "https://www.metal-archives.com/lists/NL"
    }
    ```
    But we only need the ISO key (here it is _NL_). AFAIK there are no bands with multiple countries
    of origin on MA. The collection may not be needed.
* The instruments of artists are a string separated by commas. This might be
    inconvenient for any analysis on the individual instruments.
* The hierarchy of the instrument structure for artists may be in the wrong order.
* Crawling the whole database of almost 130.000 bands will take a very long time (one or two days). 
    You will probably run out of memory before that. There is no flushing of intermittent results. Which 
    brings us to the...

## Backlog

* Save intermittent results into a database.
* Memorize which bands wre already visited (e.g. for long runs or when it crashes). 