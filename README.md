# Metal Mapper
_Metal Mapper_ is Python program and intended to be the basis to develop a toolset to access data of 
[Encyclopaedia Metallum: The Metal Archives](https://www.metal-archives.com/) (MA) and query said data. The
_Others_ section of [Add-ons](https://www.metal-archives.com/content/tools) links to two projects showcasing
interesting ways to visualize the _Metal Archives'_ data:

* [Metal Map](https://metal-map.com/): A visualization of bands by country displayed on a map, with data from M-A.
* [Metal Graph](http://metal-graph.com/): A graph showing the connections between Norwegian black metal bands, 
    with data from M-A. 

## Features



## How to use

`metalMaper.py`, when called without switches, shows a list of compiler switches and some hints
how to use them.

### Countries

Countries on MA and this tool are represented in [ISO 3166](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
two letter format. Whenever you read _XX_ in context with countries, a two letter country code is meant.

A list of all countries with at least one band is shown on calling with the switch `-l`.

### Regions

A _region_ is a group of countries defined inside the main python file. Available regions can shown on calling 
with the switch `-l`.

A popular region is are the nordic countries *NC* (containing Denmark, Sweden, Norway, Iceland, Finland, Greenland, 
Faroe Islands, Åland Islands, Svalbard and Jan Mayen).

### Bootstrapping: Crawl _all_ available countries

Calling with the switch `-a` will:

1. Generate a list of all countries (from EM's [by country page](https://www.metal-archives.com/browse/country))
with at least one band entry.
2. Extract the link for every band in every country and save the links in a folder with the same name.
    The name of the files follows this simple scheme: `bands-XX.lnks` where XX is the two letter short form.
    The contents of a `.lnks` file looks like this:
    ```
    Akollonizer/3540362756
    Among_the_Mist/7576
    Nami/3540321763
    Persefone/12779
    ```
    Together with `https://www.metal-archives.com/bands/` a fully fledged link to every band can be generated.
    
### Boostrapping at smaller scale: Crawl a country or a region

If you're not interested in getting the band links for all countries you can either 

* start with the switch `-c XX` to crawl all bands in exactly one country **or** 
* call with `-r XX` where XX is the key of the region you want to crawl.