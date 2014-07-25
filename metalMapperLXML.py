#! /usr/bin/env python

from bs4 import BeautifulSoup
import urllib2,os

def isNotEmptyStringOrLive(s):
	if len(s) == 0 or "live" in s:
		return False
	else:
		return True

def prepareGraph(bandToBandsDict):
	graph = []
	graph.append("strict graph Metal\n{\n\tedge [len=4];")
	for k, v in bandToBandsDict.items():
		for bandName in v:
			graph.append('\t"' + k + " -- " + bandName + '";\n')
	graph.append('}')

	return ''.join(graph)

def writeGraphAndCallGraphviz(graphvizString):
	bandsFile = open('bandsGraph.dot', 'w')
	bandsFile.write(graphvizString)
	bandsFile.close()
	os.system("fdp -Tpng bandsGraph.dot -o bandsGraph.png")

bandsToVisit = set()
bandsToVisit.add('http://www.metal-archives.com/bands/Haystack/116128')
#bandsToVisit.add('http://www.metal-archives.com/bands/Entombed/7')
bandsToVisitInNextRound = set()
bandsVisited = set()
searchDepth = 2
searchLevel = 0
graphBandToBands = dict()

while searchLevel < searchDepth:
	bandCurrentlyVisiting = bandsToVisit.pop()
	bandsVisited.add(bandCurrentlyVisiting)
	website = urllib2.urlopen(bandCurrentlyVisiting).read()
	soup = BeautifulSoup(website)

	# Finds band name; needs to extract link.
	s = soup.find_all(attrs={"class": "band_name"})
	actualBandName = str(s[0].next_element.next_element)
	print 'Visiting [' + actualBandName + ']...'

	# Takes all bands which belong to a person. 
	bandLinks = soup.find_all(attrs={"class": "lineupBandsRow"})
	print "Found [" + str(len(bandLinks)) + "] persons in lineup."
	graphBandNames = set();

	for bandLink in bandLinks:
		link = bandLink.a

		if link is None:
			continue
		elif "ex-" in str(bandLink.a.previous_sibling):
			firstBandIsEx = True
		else:
			firstBandIsEx = False

		# Loop through all bands in person lineup.
		while link != None:
			if "," in link: # Bands without DB entries have no links.
				bandsLoop = link.split(",")
				for s in bandsLoop:
					loopingBand = s.lstrip().rstrip()
					if isNotEmptyStringOrLive(loopingBand): # Test for "-ex" here.
						if "ex-" in loopingBand: # Handle flag later for different diagram.
							foundExBand = True
						else:
							graphBandNames.add(loopingBand)
							# print '['+loopingBand+']'
			else: # This is the actual link and text.
				if str(link).rstrip() != "" and "live" not in link:
					refLink = link.get('href')
					bandsToVisitInNextRound.add(refLink)
					graphBandNames.add(link.next_element)
					# print "Found: [" + link.next_element + "] and added [" + link.get('href') + "] to list."
					
			link = link.next_sibling
	
	if not bandsToVisit:
		bandsToVisit = bandsToVisitInNextRound
		bandsToVisitInNextRound = set()
		searchLevel+=1
	
	print "Found [" + str(len(graphBandNames)) + "] connected bands."
	graphBandToBands.update({actualBandName: graphBandNames})

# prepareGraph(graphBandToBands)
print 'Visited [' + str(len(bandsVisited)) + '] bands.'
