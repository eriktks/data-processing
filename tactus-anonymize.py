#!/usr/bin/env python3
"""
    tactus-anonymize.py: anonymize tactus file
    usage: python3 tactus-anonymyze.py [-l lang] file1.xml [file2.xml ...]
    20181015 erikt(at)xs4all.nl
"""

import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import parse

COMMAND = sys.argv.pop(0)
BINDIR = "/home/erikt/projects/e-mental-health/data-processing"
ANONYMIZETAGS = ["Body","Notes"]
CLEARTAGS = ["Username","FirstName","LastName","Email","Sender","Recipients"]
CLEARTOKEN = "PERSON"

clearedStringIds = {}

def makeId(fileName):
    return(re.sub(r"^(.*/)?(.*)\.xml$","\g<2>",fileName))

def getRootOfFile(inFileName):
    tree = ET.parse(inFileName)
    return(tree.getroot())

def getTextId(text):
    global clearedStringIds

    text = text.lower()
    if not text in clearedStringIds:
        clearedStringIds[text] = len(clearedStringIds.keys())
    return(clearedStringIds[text])

def clearTexts(root,tagNames):
    for tagname in tagNames:
        for tag in root.findall(".//"+tagName):
            tag.text = CLEARTOKEN+"-"+getTextId(tag.text)

def getTextFromXmltext(text):
    textTree = ET.fromstring("<container>"+text+"</container>")
    if textTree.text != None: text = textTree.text
    else: text = ""
    for node in textTree.findall(".//"):
        if node.text != None: text += " "+node.text
    return(text)

def anonymizeTexts(root,tagNames):
    for tagName in tagNames:
        for tag in root.findall(".//"+tagName):
            if tag.text != None:
                text = getTextFromXmlText(tag.text)

                tmpFile = open("tmpFile","w")
                print(text,file=tmpFile)
                tmpFile.close()
                anonymizeProcess = subprocess.run([BINDIR+"/anonymize-eng.sh","tmpFile"],stdout=subprocess.PIPE)
                anonymizedText = dict(anonymizeProcess.__dict__)["stdout"]
                tag.text = anonymizedText.decode("utf8")

def writeFile(tree,outFileName):
    tree.write(outFileName)


def main(argv):
    clearedStrings = {}
    for inFileName in sys.argv:
        thisId = makeId(inFileName)
        root = getRootFromFile(inFileName)
        clearTexts(root,CLEARTAGS)
        anonymizeTexts(root,ANONYMIZETAGS)
        writeFile(tree,inFileName+".an")
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
