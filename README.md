# Meta Metal Mapper

_Meta Metal Mapper_ is a Python3 program to crawl 
[Encyclopaedia Metallum: The Metal Archives](https://www.metal-archives.com/) (M-A) for bands, artists and albums. The
data is stored in a in a local database and can be analysed and exported into band networks.

The first time I saw a band network was in the liner notes of the 7" EP compilation
[True Kings of Norway](https://www.metal-archives.com/albums/Immortal/True_Kings_of_Norway/111142) almost 20 years ago.
Networks and info graphics fascinated me ever since. My interest in band networks and statistics was renewed when I 
found two projects in the _Others_ section of [Add-ons](https://www.metal-archives.com/content/tools) on M-A:

* [Metal Map](https://metal-map.com/): A visualization of bands statistics by country displayed on a map, with data from
    M-A.
* [Metal Graph](http://metal-graph.com/): A graph showing the connections between Norwegian black metal bands, 
    again with data from M-A. 
    
Neither project release the means of _how_ they acquire the presented data. The Metal Graph is limited to Norwegian
black metal and the Metal Map lacks e.g. album or gender statistics. Meta Metal Mapper closes these gaps and add even 
more analyzed data. It's not flashy but it's the base for your own data science projects.

## Highlight Reel

This is what Meta Metal Mapper already delivers:

* Generates lists for bands to crawl based on countries, regions or the entire database.
    It also accepts handcrafted files with bands of your choice.
* Extracts information about bands, their band members and releases from M-A.
* Saves ~~everything~~ a lot of the retrieved data into a Neo4j database for further analysis.
    The desktop version of Neo4j brings a graphical browser to examine small networks around
    1000 nodes ([examples](EXAMPLES.md)).
* Extracts band networks in [GraphML](http://graphml.graphdrawing.org/) for use in other tools.
* Exports CSV files with country or database reports of all countries and their genres.
* Exports HTML pages of the best albums, EPs and demos.

And to rule out any disappointments; a list of things it is not:

* It won't automatically generate websites like the above Metal Map for you.

## Getting Started

To use Meta Metal Mapper you first need to clone this repository, install Python libraries and Neo4j.

### Tool Installation

This here is the short version, a [longer version](GETTING_STARTED.md) is also available.

Install the following tools:

1. Python >= 3.6.
2. Libraries: `pip3 install -r requirements.txt`.
3. Neo4j [Windows](https://neo4j.com/download/) or 
    [Linux](https://neo4j.com/docs/operations-manual/current/installation/linux/debian/).

### Setup

1. Start Neo4j Desktop and [create a graph](USAGE.md).
2. Start the created graph. 
3. In the Neo4j Desktop application use _Add Application_ to install the Neo4j Browser. 
4. Open `settings.py` and change `NEO4J_PASSWORD`.

### First Crawl and Analysis

This rather short section uses example data, but gives an idea what it is about. A detailed [usage page](USAGE.md)
explains what the parameters mean and what to do with them.   

Call `python meta_metal_mapper.py` each time with one of the following parameters:

1. `-b -f data/true_kings.lnks`: Uses the supplied file with band names, crawls all of them and puts data in to the 
    database.
2. `-y`: Prints analysis into terminal and saves several files with data.

Please note that the analysis is across the entire database and might result in meaningless data e.g. when data is put
into relation to a country. 

### Inspect the graph

1. Open the Neo4j Browser you installed during setup.
2. Click on the cog (lower left) and change _Initial Node Display_ to a number >= 2000.
3. Copy `MATCH (n) RETURN n` into the command text field (starting with a $) and hit the play button.
  1. The displayed graph contains all crawled band, artist and album nodes.
  2. Click on some of the nodes or edges to see the individual properties.

To filter the albums try `MATCH (b:Band)--(m:Member) RETURN b, m` and hit the play button. The resulting graph is a bit
slimmer.

### Inspect the report

Browse to the folder named `reports` and open a report in a web browser to see the best albums, EPs and demos.

### Where to go from here?

Install [Gephi](GEPHI_HOWTO.md), load a `.graphml` file (see exports folder) and experiment with the available data. 

See the detailed [usage page](USAGE.md), the [glossary](GLOSSARY.md) or the [examples](EXAMPLES.md) for inspiration.

## Known Issues

* `PLAYED_IN` relationships are be overwritten with the last one found. An artist, which was a regular
    band member and helped out live in the past will be considered to be "only" `PL` [past (live)]. 
* The hierarchy of the instrument structure for artists may be in the wrong order.

### Starting Neo4j Appimage on Linux

If the Neo4j Appimage does not start the desktop window, check the console log for:

    The name org.freedesktop.secrets was not provided by any .service files
    
Installation of the gnome-keyring helped me in that case:

    sudo apt install gnome-keyring

### Library Hack

While crawling band links on Windows I encountered a defect in `Lib/http/client.py`. The percent escaped characters were
not resolved correctly. The solution for me was to change `putrequest()` (before `self._output()` is called). The line
looks like this:

    url = rfc3986.uri_reference(url).unsplit()
    
This hack needs to import `rfc3986` to function.

## Backlog

* Add mode to visit single band and their immediate connections.
* Notify user on calling analysis if a country has not been mapped entirely. 
* Implement a flag to overwrite data unconditionally.
* Implement option to overwrite data based on its age.
* Connecting releases with labels. The screenshot shows additional label nodes (and their connections) from prototyping.
    ![Prototype including labels and Albums](img/intro_graph_2.png)