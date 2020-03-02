# Getting Started

To use Meta Metal Mapper you first need to clone this repository, install Python libraries and Neo4j.

## Python3

A Python3 installation >= 3.6 is needed to execute Meta Metal Mapper.

If you see output like this

      File "meta_metal_mapper.py", line 36
        f'Supported modes:\n'
                            ^
    SyntaxError: invalid syntax

you need to run the program explicitly with `python3 meta_metal_mapper.py`.

## Libraries

Meta Metal Mapper depends on the following packages:
* [certifi](https://certifi.io/en/latest/)
* [urllib3](https://urllib3.readthedocs.io/en/latest/)
* [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [neomodel](https://neomodel.readthedocs.io/en/latest/)
* [progressbar2](https://pypi.org/project/progressbar2/)

Install them with `pip3`:

    pip3 install -r requirements.txt

## Neo4j

All data is stored in a [Neo4j database](https://neo4j.com/product/). You have to download and install the
[desktop version (Windows)](https://neo4j.com/download/) to use any meaningful functionality. The downside for some 
users might be the mandatory use of a Google or Facebook account to authorize the desktop app. However a 30 day trial
period for the software is granted. If you know what you're doing you may simply set up Neo4j from other available 
editions. There is e.g. the official 
[Linux guide](https://neo4j.com/docs/operations-manual/current/installation/linux/debian/).

Fire it up and create a database. Change the database credentials as needed in `settings.py`.
