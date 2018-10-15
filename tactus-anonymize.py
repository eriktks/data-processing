#!/usr/bin/env python3
"""
    tactus-anonymize.py: anonymize tactus file
    usage: python3 tactus-anonymyze.py file.xml
    20181015 erikt(at)xs4all.nl
"""

import re
import sys
import xml.etree.ElementTree as ET

COMMAND = sys.argv.pop(0)

def makeId(fileName):
    thisId = re.sub(r".*/","",fileName)
    thisId = re.sub(r"\.xml.*$","",thisId)
    return(thisId)

def main(argv):
    for inFileName in sys.argv:
        tree = ET.parse(inFileName)
        root = tree.getroot()
        thisId = makeId(inFileName)
        for tag in root.findall(".//FirstName"):
            tag.text = re.sub(r"\b([A-Z])\S*",r"\1",tag.text)
            print(tag.text)
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
