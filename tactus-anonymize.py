#!/usr/bin/env python3
"""
    tactus-anonymize.py: anonymize tactus file
    usage: python3 tactus-anonymyze.py [-l lang] file1.xml [file2.xml ...]
    20181015 erikt(at)xs4all.nl
"""

import html
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

COMMAND = sys.argv.pop(0)
BINDIR = "/home/erikt/projects/e-mental-health/data-processing"
ANONYMIZETAGS = ["Body","Notes"]
CLEARTAGS = ["Username","FirstName","LastName","Email","Sender","Recipients"]
CLEARTOKEN = "PERSON"

clearedStringIds = {}

def makeId(fileName):
    return(re.sub(r"^(.*/)?(.*)\.xml$","\g<2>",fileName))

def getRootOfFile(inFileName):
    return(ET.parse(inFileName))

def getTextId(text):
    global clearedStringIds

    text = text.lower()
    if not text in clearedStringIds:
        clearedStringIds[text] = str(len(clearedStringIds.keys()))
    return(clearedStringIds[text])

def clearTexts(tree,tagNames):
    root = tree.getroot()
    for tagName in tagNames:
        for tag in root.findall(".//"+tagName):
            tag.text = CLEARTOKEN+"-"+getTextId(tag.text)

def getTextFromXmlText(text):
    try: textTree = ET.fromstring("<container>"+text+"</container>")
    except Exception as e: sys.exit("Error processing text "+text+": "+str(e))
    if not textTree.text is None: text = textTree.text
    else: text = ""
    for node in textTree.findall(".//"):
        if not node.text is None: text += " "+node.text
    return(text)

def anonymizeTexts(tree,tagNames):
    root = tree.getroot()
    for tag in root.iter():
        if not tag.text is None:
            if tag.tag in tagNames:
                text = getTextFromXmlText(html.escape(tag.text))
                tmpFile = open("tmpFile","w")
                print(text,file=tmpFile)
                tmpFile.close()
                anonymizeProcess = subprocess.run([BINDIR+"/anonymize-eng.sh","tmpFile"],stdout=subprocess.PIPE)
                anonymizedText = dict(anonymizeProcess.__dict__)["stdout"]
                tag.text = anonymizedText.decode("utf8")
            tag.text = html.unescape(tag.text)

def writeFile(tree,outFileName):
    tree.write(outFileName,encoding="utf8")

def main(argv):
    for inFileName in argv:
        tree = getRootOfFile(inFileName)
        clearTexts(tree,CLEARTAGS)
        anonymizeTexts(tree,ANONYMIZETAGS)
        writeFile(tree,inFileName+".an")
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
