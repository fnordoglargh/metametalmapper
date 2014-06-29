#! /usr/bin/env python

import urllib2,os
import lxml.html
from lxml import etree
import xml.etree.ElementTree as ET

bandsToVisit = ['http://www.metal-archives.com/bands/Entombed/7']
bandsVisited = list()

searchDepth = 1

while (searchDepth > 0):

    bandCurrentlyVisiting = bandsToVisit.pop()
    bandsVisited.append(bandCurrentlyVisiting)

    website = urllib2.urlopen(bandCurrentlyVisiting).read()
    html = lxml.html.fromstring(website)
    root = ET.fromstring(html)
    print(tree.xpath("//h1[@class=\"band_name\"]/text()"))
#    print(html.xpath("//div"))


#    print lxml.html.tostring(html)
    searchDepth-=1

print 'Visited [' + str(len(bandsVisited)) + '] bands.'

