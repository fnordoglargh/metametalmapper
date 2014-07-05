#! /usr/bin/env python

import urllib2,os
import lxml.html
from lxml import etree
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def has_class(tag):
	return tag.has_attr('class')

bandsToVisit = ['http://www.metal-archives.com/bands/Entombed/7']
bandsVisited = list()

searchDepth = 1

while (searchDepth > 0):

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

		print '***'
		
		link = bandLink.a

		# Loop through all bands in person lineup.
		while link != None:
			if "," in link: # Bands without DB entries have no links.
				bandsLoop = link.split(",")
				for s in bandsLoop:
					print '['+s.lstrip()+']'
			else: # This is the actual link and text.
				print link
			
			link = link.next_sibling


		#		print '>>>' + str(bandLink) + '<<<'

#    print '*** Next Sibling ***'
#    print(bandLinks[0].a.previous_sibling)
#    print '*** Next Sibling ***'

#    print(s.next_element)

#    html = lxml.html.fromstring(website)
#    root = ET.fromstring(html)
#    print(tree.xpath("//h1[@class=\"band_name\"]/text()"))
#    print(html.xpath("//div"))


#    print lxml.html.tostring(html)
	searchDepth-=1

print 'Visited [' + str(len(bandsVisited)) + '] bands.'

