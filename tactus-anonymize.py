#!/usr/bin/env python3
"""
    tactus-anonymize.py: anonymize tactus file
    usage: python3 tactus-anonymyze.py file.xml
    20181015 erikt(at)xs4all.nl
"""

import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import parse

COMMAND = sys.argv.pop(0)
BINDIR = "/home/erikt/projects/e-mental-health/data-processing"
TARGETTAGS = ["Body","Notes"]
CLEANTAGS = ["Username","FirstName","LastName","Email","Sender","Recipients"]

def makeId(fileName):
    thisId = re.sub(r".*/","",fileName)
    thisId = re.sub(r"\.xml.*$","",thisId)
    return(thisId)

def main(argv):
    for inFileName in sys.argv:
        tree = ET.parse(inFileName)
        root = tree.getroot()
        thisId = makeId(inFileName)
        for targetTag in CLEANTAGS:
            for tag in root.findall(".//"+targetTag):
                    tag.text = "REMOVED"
        for targetTag in TARGETTAGS:
            for tag in root.findall(".//"+targetTag):
                if tag.text != None:
                    textTree = ET.fromstring("<container>"+tag.text+"</container>")
                    if textTree.text != None: text = textTree.text
                    else: text = ""
                    for node in textTree.findall(".//"):
                        if node.text != None: text += " "+node.text
                    tmpFile = open("tmpFile","w")
                    print(text,file=tmpFile)
                    tmpFile.close()
                    anonymizeProcess = subprocess.run([BINDIR+"/anonymize-eng.sh","tmpFile"],stdout=subprocess.PIPE)
                    anonymizedText = dict(anonymizeProcess.__dict__)["stdout"]
                    tag.text = anonymizedText.decode("utf8")
        tree.write(inFileName+".an")
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
