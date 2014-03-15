! /usr/bin/env python

import urllib2

website = urllib2.urlopen("http://www.metal-archives.com/bands/Entombed/7").read()
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
