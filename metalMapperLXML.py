#! /usr/bin/env python

from bs4 import BeautifulSoup
import urllib2,os

def has_class(tag):
	return tag.has_attr('class')

def isNotEmptyStringOrLive(s):
	if len(s) == 0 or "live" in s:
		return False
	else:
		return True

bandsToVisit = ['http://www.metal-archives.com/bands/Entombed/7']
bandsVisited = list()
searchDepth = 1
searchLevel = 0
bandsList = list()

while searchLevel < searchDepth:

	bandCurrentlyVisiting = bandsToVisit.pop()
	bandsVisited.append(bandCurrentlyVisiting)
	website = urllib2.urlopen(bandCurrentlyVisiting).read()
	soup = BeautifulSoup(website)

	# Finds band name; needs to extract link.
	s = soup.find_all(attrs={"class": "band_name"})
	print 'Visiting [' + str(s[0].next_element.next_element) + ']...'

	# Takes all bands which belong to a person. 
	bandLinks = soup.find_all(attrs={"class": "lineupBandsRow"})
	print '[' + str(len(bandLinks)) + '] persons in lineup found.'

	for bandLink in bandLinks:
		
		if "ex-" in str(bandLink.a.previous_sibling):
			firstBandIsEx = True
		else:
			firstBandIsEx = False

		link = bandLink.a

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
							print '['+loopingBand+']'
			else: # This is the actual link and text.
				if str(link).rstrip() != "" and "live" not in link:
					refLink = link.get('href')
					if refLink not in bandsToVisit:
						bandsToVisit.append(refLink)
						print "Found: [" + link.next_element + "] and added [" + link.get('href') + "] to list."
					
			link = link.next_sibling

	searchLevel+=1

print 'Visited [' + str(len(bandsVisited)) + '] bands.'

