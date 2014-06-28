#! /usr/bin/env python

import urllib2,os
from lxml import etree

bandsToVisit = ['http://www.metal-archives.com/bands/Entombed/7']
bandsVisited = list()

while (searchDepth > 0):

    bandCurrentlyVisiting = bandsToVisit.pop()
    bandsVisited.append(bandCurrentlyVisiting)

    website = urllib2.urlopen(bandCurrentlyVisiting).read()

    searchDepth-=1

print 'Visited [' + str(len(bandsVisited)) + '] bands.'

