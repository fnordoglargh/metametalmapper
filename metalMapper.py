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
    
    bandName = website[indexBand+2:indexBandEnd]
    print 'Band: ' + bandName

    isEndReached = False
    loopBandLink = 'Empty'
    loopBandName = 'Empty'
    seeAlsoIndex = website.find('See also:')
    tableElementEndIndex = 0
    loopbands = 'Empty'

    while (not isEndReached):
    
        if (seeAlsoIndex != -1):
            equalIndex = website.find('="',seeAlsoIndex)
            tableElementEndIndex = website.find('</td>',equalIndex)
            loopBands = website[equalIndex:tableElementIndex]
            bandsListRaw = loopBands.split(',')

            for s in BandsListRaw:
                linkIndex = s.find('http:')
                # Look here for "ex"-Bands

                if linkIndex != -1:
                    linkEndIndex = s.find('"', linkIndex)
                    loopBandLink = s[linkIndex:linkEndIndex]
                    bandsToVisit.append(loopBandLink)
                    loopBandName = s[s.find('">')+2:s.find('</a>')]
                else:
                    loopBandName = s.lstrip().rstrip()
                    
                    if(loopBandName.find('ex') != -1):
                        loopBandName[loopBandName.find('ex')+3:]
                        # get rid of trailing "live"
                bandsList.append('\t"' + bandName + '" -- "' + loopBandName+ '":')
        else:
            isEndReached = True

        seeAlsoIndex = website.find('See also:', seeAlsoIndex + 1)

    searchDepth-=1

bandsList.append('}')
bandsFile = open('bandsGraph.dot', 'w')

for s in bandsList:
    bandsFile.write("%s\n" % s)

print 'Visited [' + str(len(bandsVisited)) + '] bands.'

bandsFile.close()
os.System("fdp -Tpng bandsGraph.dot -o bandsGraph.png")
    
