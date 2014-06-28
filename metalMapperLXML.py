#! /usr/bin/env python

import urllib2,os
import lxml.html

bandsToVisit = ['http://www.metal-archives.com/bands/Entombed/7']
bandsVisited = list()

searchDepth = 1

while (searchDepth > 0):

    bandCurrentlyVisiting = bandsToVisit.pop()
    bandsVisited.append(bandCurrentlyVisiting)

    website = urllib2.urlopen(bandCurrentlyVisiting).read()
    html = lxml.html.fromstring(website)#.getroot()
    print(html.xpath("//@class='band_name'"))


#    print lxml.html.tostring(html)
    searchDepth-=1

print 'Visited [' + str(len(bandsVisited)) + '] bands.'

