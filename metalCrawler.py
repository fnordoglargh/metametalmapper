import certifi
import urllib3
import os
import logging
import json
import threading
import queue
import time
from bs4 import BeautifulSoup, NavigableString, Tag
from diagramCreator import *

linkMain = 'http://www.metal-archives.com/'
bands = 'bands/'
bandsQueue = queue.Queue()
ajaxLinks = queue.Queue()

# 8 might be a bit high (leaves some forbidden messages on getting the JSON
# data or the bands).
threadCount = 8

class visitBandThread(threading.Thread):

    def __init__(self, threadID, bandLinks):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = "BandVisiter_" + threadID
        self.bandLinks = bandLinks
        self.logger = logging.getLogger('Crawler')
        self.logger.debug("Initing " + self.name)

    def run(self):
        self.logger.debug("Running " + self.name)
        while self.bandLinks.qsize() != 0:
            linkBandTemp = self.bandLinks.get_nowait()
            crawlBand(linkBandTemp)

class visitBandListThread(threading.Thread):

    def __init__(self, threadID, countryLinks, bandLinks):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = "BandListVisiter_" + threadID
        self.countryLinks = countryLinks
        self.bandLinks = bandLinks
        self.logger = logging.getLogger('Crawler')
        self.logger.debug("Initing " + self.name)

    def run(self):
        self.logger.debug("Running " + self.name)
        linkCounter = 0

        while self.countryLinks.qsize() != 0:
            linkCountryTemp = self.countryLinks.get_nowait()
            http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
            countryJson = http.request('GET', linkCountryTemp)
            jsonDataString = countryJson.data.decode("utf-8")
            jsonDataString = jsonDataString.replace("\"sEcho\": ,", '')
            jsonData = None
            self.logger.debug("  Working on:" + linkCountryTemp)

            try:
                jsonData = json.loads(jsonDataString)
            except:
                self.logger.error("  JSON error for [" + linkCountryTemp + "]. Putting it back in circulation...")
                self.countryLinks.put(linkCountryTemp)
            
            if jsonData is not None:
                for band in jsonData["aaData"]:
                    indexFirstApostrophe = band[0].find("'")
                    indexSecondApostrophe = band[0].find("'", indexFirstApostrophe + 1)
                    bandLink = band[0][indexFirstApostrophe + 1:indexSecondApostrophe]
                    indexFirstClosingBracket = band[0].find(">")
                    indexSecondOpeningBracket = band[0].find("<", indexFirstClosingBracket)
                    bandName = band[0][indexFirstClosingBracket + 1:indexSecondOpeningBracket]
                    self.logger.debug("    {}: {}".format(bandName, bandLink))
                    # We do not need the leading "https://www.metal-archives.com/bands/".
                    self.bandLinks.put(bandLink[37:len(bandLink)])
                    linkCounter += 1

        self.logger.debug("Finished {} and added {} links.".format(self.name,str(linkCounter)))

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

def crawlCountry(linkCountry):
    logger = logging.getLogger('Crawler')
    logger.debug(">>> Crawling Country: " + linkCountry)
    jsonDataString = ""
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    while True:
        countryJson = http.request('GET', linkCountry)
        jsonDataString = countryJson.data.decode("utf-8")

        if "Forbidden." not in jsonDataString:
            break
        else:
            logger.debug("  trying again...")
            time.sleep(.5)

    jsonDataString = jsonDataString.replace("\"sEcho\": ,", '')
    jsonData = json.loads(jsonDataString)

    # The total amount of entries for this country is the only data we need for now.
    amountEntries = jsonData["iTotalRecords"]
    logger.debug("  Country has [{}] entries.".format(amountEntries))
    # Limit imposed by MA.
    displayConstant = 500
    # Amount of runs needed.
    neededRunCount = (amountEntries // displayConstant)

    # We need at least one and always one more (because of the division rounding down).
    if amountEntries % displayConstant > 0:
        neededRunCount += 1

    threadCount = 8

    # Override number of threads in case we don't need all.
    if neededRunCount < threadCount:
        threadCount = neededRunCount

    logger.debug("  Setting up to do [{}] runs with [{}] threads.".format(str(neededRunCount), str(threadCount)))
    linkSuffix = "json/1?sEcho=1&iDisplayStart="

    # Prepare the AJAX links for the actual run.
    for i in range(0, amountEntries, displayConstant):
        ajaxLinks.put_nowait(linkCountry + linkSuffix + str(i))
        logger.debug("    Prepping link: " + str(i))

    threads = []

    # Create threads and let them run.
    for i in range(0, threadCount):
        thread = visitBandListThread(str(i), ajaxLinks, bandsQueue)
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    logger.debug("<<< Crawling Country")

def crawlCountries():
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    countriesPage = http.request('GET', "https://www.metal-archives.com/browse/country")
    soup = BeautifulSoup(countriesPage.data, "html.parser")
    s = soup.find_all(attrs={"class": "countryCol"})
    countryLinks = []

    for i in range(0, len(s)):
        for j in range(1, len(s[i].contents), 3):
            tempLink = s[i].contents[j].attrs["href"]
            countryShort = tempLink[len(tempLink) - 2:len(tempLink)]
            countryLinks.append("https://www.metal-archives.com/browse/ajax-country/c/" + countryShort)

    return countryLinks

def crawlBand(bandName):
    # TODO: The % escaped glyphs only work if the client.py in http
    # is changed in putrequest() before self._output() is called.
    # The line looks like this:
    # url = rfc3986.uri_reference(url).unsplit()
    # Needs to import rfc3986
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

    if len(s) == 0:
        return -1

    bandData = {}
    bandData["id"] = bandName[bandName.rfind('/') + 1:]
    bandData["name"] = s[0].next_element.next_element

    s = soup.find_all(attrs={"class": "float_left"})
    bandData["country"] = s[1].contents[3].contents[0]
    bandData["location"] = s[1].contents[7].contents[0]
    bandData["status"] = s[1].contents[11].contents[0]
    bandData["formed"] = s[1].contents[15].contents[0]
    bandData["active"] = []

    s = soup.find_all(attrs={"class": "clear"})
    active = ""

    # This also contains earlier incarnations.  We take all of them.
    for element in s[3].contents[3].contents:
        active = element
        if type(active) is NavigableString:
            active = active.replace('\t', '')
            active = active.replace('),', '')
            active = active.replace('\n', '')
            active = active.replace(' ', '')
            yearTokens = active.split(',')
            for yearToken in yearTokens:
                bandData["active"].append(yearToken)
        elif type(active) is Tag:
            previousName = " " + active.contents[0]
            lastPosition = len(bandData["active"]) - 1
            bandData["active"][lastPosition] += previousName + ")"
        else:
            print(type(active))
    active = active.replace('\t', '')
    active = active.replace('),', '')
    active = active.replace('\n', '')
    active = active.replace(' ', '')

    s = soup.find_all(attrs={"class": "float_right"})
    genres = s[3].contents[3].contents[0]
    genres = genres.split(',')
    bandData["genre"] = []

    for genre in genres:
        bandData["genre"].append(genre)

    logger.debug(bandData)
    logger.debug('<<< Crawling [' + bandName + ']')

def crawlBands(fileWithBandLinks):
    logger = logging.getLogger('Crawler')
    logger.debug('>>> Crawling all bands in [{}]'.format(fileWithBandLinks))
    isFileAvailable = os.path.isfile(fileWithBandLinks)

    if isFileAvailable:
        logger.info("  {} is available. Starting to crawl all available bands. This may take a very long time.".format(fileWithBandLinks))
    else:
        logger.error("  {} is not available. Run with -c first.".format(fileWithBandLinks))
        return -1

    localBandsQueue = queue.Queue()

    with open(fileWithBandLinks, "r") as bandsFile:
        for line in bandsFile:
            localBandsQueue.put_nowait(line.rstrip('\r\n'))

    threads = []

    # Create threads and let them run.
    for i in range(0, threadCount):
        thread = visitBandThread(str(i), localBandsQueue)
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    logger.debug('<<< Crawling all bands in [{}]'.format(fileWithBandLinks))

def crawlBandsOld():
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
