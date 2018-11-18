#!/usr/bin/python
import os
import sys
import getopt
from enum import Enum

class MapMode(Enum):
    Error = -1
    SingleCrawl = 0

def printHelp():
    print('Supported modes:')
    print('  Crawl mode: metalMapper.py -c')

def main(argv):
    
    firstSet = ''
    lastSet = ''

    # Change to a terminal size in which everything fits.
    os.system('mode con: cols=153 lines=9999')

    try:
        opts, args = getopt.getopt(argv, "ah")
    except getopt.GetoptError:
        printHelp()
        sys.exit(2)

    mode = MapMode.Error

    if len(opts) == 0:
        printHelp()

    for opt, arg in opts:
        if opt == '-h':
            printHelp()
            sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])
