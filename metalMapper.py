! /usr/bin/env python

import urllib2,os

bandsToVisit = ['urllib2.urlopen("http://www.metal-archives.com/bands/Entombed/7']
bandsVisited = list()
searchDepth = 1

bandsList = list()
bandsList.append('strict graph G')
bandsList.append('{')
bandsList.append('\tedge [len=4];')

while (searchDepth > 0):

    bandCurrentlyVisiting = bandsToVisit.pop()
    bandsVsited.append(bandCurentlyBeingVisited)

    website = urllib2.urlopen(bandCurrentlyVisiting).read()
    indexBand = website.find('class="band_name"')
    indexBand = website.find('">',indexBand+1)
    indexBand = website.find('">',indexBand+1)
    indexBandEnd = website.find('</',indexBand)

print 'Band: ' + website[indexBand+2:indexBandEnd]

isEndReached = False

while (not isEndReached):
    seeAlsoIndex = website.find('See also:')
    print seeAlsoIndex

    if (seeAlsoIndex != -1):
        equalIndex = website.find('=')
        print equalIndex
    else:
        isEndReached = True
