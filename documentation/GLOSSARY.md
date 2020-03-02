# Glossary

Certain words are used throughout the documentation. This short section explains what _countries_,
_regions_ and _graph databases_ in the Meta Metal Mapper context mean.

## Countries

Countries on M-A and this tool are represented in [ISO 3166](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
two letter format. Whenever you read _NN_ in context with countries, a two letter country code is meant. Two special
countries exist: XX (international) and YY (unknown).

A list of all countries with at least one band is shown on calling with the switch `-l`.

## Regions

A _region_ is a group of countries defined inside the file `country_helper.py`. Available regions are shown on calling 
`meta_metal_mapper.py` with the switch `-l`.

Popular regions are *NCO*; nordic countries (containing Denmark, Sweden, Norway, Iceland, Finland, Greenland, Faroe
Islands, Åland Islands, Svalbard and Jan Mayen) and *SCA*; Scandinavia (as above but _without_  Åland Islands, Svalbard
and Jan Mayen).

## Graph Database

Head over to [dedicated page](DATABASES.md) which explains how graph databases are used in Meta Metal Mapper. 
