import certifi
import urllib3
import os
import logging
import json
import threading
import queue
from bs4 import BeautifulSoup
from diagramCreator import *

linkMain = 'http://www.metal-archives.com/'
bands = 'bands/'
bandsQueue = queue.Queue()

class visitBandListThread(threading.Thread):

    def __init__(self, threadID, name, countryLink, startIndex, bandLinks):
        self.logger = logging.getLogger('Crawler')
        self.logger.debug("Initing " + name)
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.countryLink = countryLink
        self.startIndex = startIndex
        self.bandLinks = bandLinks

    def run(self):
        self.logger.debug("Running " + self.name)
        linkCountryTemp = self.countryLink + str(self.startIndex)
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        countryJson = http.request('GET', linkCountryTemp)
        jsonDataString = countryJson.data.decode("utf-8")
        jsonDataString = jsonDataString.replace("\"sEcho\": ,", '')
        jsonData = json.loads(jsonDataString)

        for band in jsonData["aaData"]:
            indexFirstApostrophe = band[0].find("'")
            indexSecondApostrophe = band[0].find("'", indexFirstApostrophe + 1)
            bandLink = band[0][indexFirstApostrophe + 1:indexSecondApostrophe]
            self.logger.debug("  link: " + bandLink)
            indexFirstClosingBracket = band[0].find(">")
            indexSecondOpeningBracket = band[0].find("<", indexFirstClosingBracket)
            bandName = band[0][indexFirstClosingBracket + 1:indexSecondOpeningBracket]
            self.logger.debug("  name: " + bandName)
            self.bandLinks[bandName] = bandLink
            bandsQueue.put(bandLink)

        self.logger.debug("Finished" + self.name)


def displayChildren(c):
    if c is not None:
        print(c)
        for e in c:
            displayChildren(e)

def isNotEmptyStringOrLive(s):
    if not s:
        return False
    elif "(live)" in s:
        if s[0:6] == "(live)":
            return False
        else:
            return True
    else:
        return True

def visitBandList(countryLink, startIndex, bandLinks):
    logger = logging.getLogger('Crawler')
    linkCountryTemp = countryLink + str(startIndex)
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    countryJson = http.request('GET', linkCountryTemp)
    jsonDataString = countryJson.data.decode("utf-8")
    jsonDataString = jsonDataString.replace("\"sEcho\": ,", '')
    jsonData = json.loads(jsonDataString)

    for band in jsonData["aaData"]:
        indexFirstApostrophe = band[0].find("'")
        indexSecondApostrophe = band[0].find("'", indexFirstApostrophe + 1)
        bandLink = band[0][indexFirstApostrophe + 1:indexSecondApostrophe]
        logger.debug("  link: " + bandLink)
        indexFirstClosingBracket = band[0].find(">")
        indexSecondOpeningBracket = band[0].find("<", indexFirstClosingBracket)
        bandName = band[0][indexFirstClosingBracket + 1:indexSecondOpeningBracket]
        logger.debug("  name: " + bandName)
        bandLinks[bandName] = bandLink

def crawlCountry():
    linkCountry = "https://www.metal-archives.com/browse/ajax-country/c/NO/"
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    countryJson = http.request('GET', linkCountry)
    jsonDataString = countryJson.data.decode("utf-8")
    jsonDataString = jsonDataString.replace("\"sEcho\": ,", '')
    jsonData = json.loads(jsonDataString)

    logger = logging.getLogger('Crawler')
    logger.debug(">>> Crawling Country: " + linkCountry)

    amountEntries = jsonData["iTotalRecords"]
    displayConstant = 500
    amountRetries = amountEntries / displayConstant
    linkSuffix = "json/1?sEcho=1&iDisplayStart="

    bandLinks = {}
    threads = []

    for i in range(0, amountEntries, displayConstant):
        thread = visitBandListThread(str(i), str(i), linkCountry + linkSuffix, i , bandLinks)
        thread.start()
        threads.append(thread)
     
    for t in threads:
        t.join()

    logger.debug("queue element" + bandsQueue.get())
    logger.debug("<<< Crawling Country")

def crawlBand(bandName):
    linkBand = linkMain + bands + bandName
    logger = logging.getLogger('Crawler')
    logger.debug('>>> Crawling [' + bandName + ']')

    # Initialize the pool manager with certificates.  There will be nasty warnings for every call if you don't.
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    bandPage = http.request('GET', linkBand)
    soup = BeautifulSoup(bandPage.data, "html.parser")
    #soup = BeautifulSoup(bandPage.data, "lxml")

    # Finds band name; needs to extract the ID later.
    s = soup.find_all(attrs={"class": "band_name"})
    #s = soup.find_all(attrs={"id": "band_info"})

    actualBandName = s[0].next_element.next_element#.encode('utf-8')

    s = soup.find_all(attrs={"class": "float_left"})
    location = s[1].contents[7].contents[0]
    status = s[1].contents[11].contents[0]
    formed = s[1].contents[15].contents[0]

    s = soup.find_all(attrs={"class": "clear"})
    active = ""
    # This also contains earlier incarnations.  We take the last element for now.
    for element in s[3].contents[3].contents:
        active = element
    active = active.replace('\t', '')
    active = active.replace('),', '')
    active = active.replace('\n', '')
    active = active.replace(' ', '')

    s = soup.find_all(attrs={"class": "float_right"})
    genres = s[3].contents[3].contents[0]

    logger.debug('  Location : ' + location)
    logger.debug('  Status   : ' + status)
    logger.debug('  Formed in: ' + formed)
    logger.debug('  Active   : ' + active)
    logger.debug('  Genres   : ' + genres)
    logger.debug('<<< Crawling [' + bandName + ']')


def crawlBands():
    bandsToVisit = set()
    #bandsToVisit.add('http://www.metal-archives.com/bands/Bathory')
    bandsToVisit.add('https://www.metal-archives.com/bands/Obituary/165')
    #bandsToVisit.add('https://www.metal-archives.com/bands/Metallica')
    #bandsToVisit.add('http://www.metal-archives.com/bands/Haystack/116128')
    #bandsToVisit.add('http://www.metal-archives.com/bands/Entombed/7')
    bandsToVisitInNextRound = set()
    bandsVisited = set()
    searchDepth = 1
    searchLevel = 0
    graphBandToBands = dict()

    while searchLevel < searchDepth:
        # Initialize the pool manager with certificates.  There will be nasty warnings for every call if you don't.
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

        # Pop a band from the "to visit" collection and add to visited collection.
        bandCurrentlyVisiting = bandsToVisit.pop()
        bandsVisited.add(bandCurrentlyVisiting)
    
        website = http.request('GET', bandCurrentlyVisiting)
        soup = BeautifulSoup(website.data, "html.parser")

        # Finds band name; needs to extract link.
        s = soup.find_all(attrs={"class": "band_name"})
        actualBandName = s[0].next_element.next_element#.encode('utf-8')
        print('Visiting [' + actualBandName + ']...')

        # Takes all bands which belong to a person.
        bandLinks = soup.find_all(attrs={"class": "lineupBandsRow"})

        print("  Found [" + str(len(bandLinks) // 2) + "] persons with connected bands in lineup.")
        graphBandNames = set()
        #print(bandLinks)

        lineup = soup.find_all(attrs={"id": "band_tab_members_all"})
        lineup2 = soup.find(attrs={"id": "band_tab_members_all"})

    #    displayChildren(lineup)

        for bandLink in bandLinks:
            link = bandLink.a

            #print(bandLink.text.strip())

            if link is None:
                # TODO: Find solution for multiple bands with no link.
                graphBandNames.add(bandLink.text.split(':')[1].rstrip().lstrip().replace("ex-", ""))
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
                        # This can be anything (e.g.  "ex-" "(live)" or whitespaces).
                        # We want everything starting with "ex-" follwed by a band name.
                        # Or a band name followed by "(live)".
                        loopingBand = s.lstrip().rstrip() 

                        # TODO: Make this better: Handle live better.
                        # This will return true for legitimate bands followed by "(live)".
                        if isNotEmptyStringOrLive(loopingBand): 
                            print(loopingBand)
                            if loopingBand != "ex-": # Test for "-ex" here.  Handle flag later for different diagram.
                                loopingBand = loopingBand.replace("ex-", "")
                                loopingBand = loopingBand.replace("(live)", "")
                                graphBandNames.add(loopingBand)
                else: # This is the actual link and text.
                    if str(link).rstrip() != "" and "live" not in link:
                        refLink = link.get('href')
                        bandsToVisitInNextRound.add(refLink)
                        graphBandNames.add(link.next_element)
                        #print " Found: [" + link.next_element + "] and added [" + link.get('href') + "] to list."

                link = link.next_sibling

        if not bandsToVisit:
            bandsToVisit = bandsToVisitInNextRound
            bandsToVisitInNextRound = set()
            searchLevel+=1

        print("  Found [" + str(len(graphBandNames)) + "] connected bands.")
        graphBandToBands.update({actualBandName: graphBandNames})

    #    for e in graphBandNames:
    #        print e

    bandGraph = prepareGraph(graphBandToBands)
    writeGraphAndCallGraphviz(bandGraph)
    print('Visited [' + str(len(bandsVisited)) + '] bands.')
