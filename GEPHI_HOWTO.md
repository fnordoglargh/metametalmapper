# How to use Gephi

_[Gephi](https://gephi.org/)_ is one of the tools to render graphs from the `.graphml` exported by _mmm_. This page 
gives a short introduction how to massage a graph into something useful.  

## Preparing a graph

For this example we use Lebanon with its manageable 51 bands (Dec 2019). Call `metal_mapper` three times with the 
following parameters:

1. `-c LB`
2. `-b -F LB`
3. `-y`

Open the resulting `.graphml` in Gephi and make the following changes. They are going to change the node size based on
their degree (amount of connections to other nodes). Bands with no connection will be small, the ones with most 
connections will be larger.

![Node Degree](img/gephi_node_degree.png)

The random layout is not very pretty. Let's apply the _ForceAtlas 2_ with these settings and hit the _Run_ button.

![Node Degree](img/gephi_forceatlas2_small.png)

This leaves us with a graph that might look like the next picture. There's a network of connected bands and a lot of
either unconnected or less connected bands.

![Middle East unfiltered - Lebanon](img/middle_east_1_unfiltered.png)


## Filter unconnected bands

1. Open _Topology_ from _Filters_. Drag a _Giant Component_ into _Queries_ located under the Filters.
2. Hit the play button.

This leaves you with a smaller network of 20 connected bands. Bands which are not connected to the main graph won't
be shown.

![Middle East filtered - Lebanon](img/middle_east_1_filtered.png)
