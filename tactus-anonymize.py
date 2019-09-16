#!/usr/bin/env python3
"""
    tactus-anonymize.py: anonymize tactus file
    usage: python3 tactus-anonymyze.py [-l lang] file1.xml [file2.xml ...]
    20181015 erikt(at)xs4all.nl
"""

import html
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

COMMAND = sys.argv.pop(0)
BINDIR = "/home/erikt/projects/e-mental-health/data-processing"
ANONYMIZEPRG = "anonymize-dut.sh"
ANONYMIZETAGS = ["Body","Subject", "Notes"]
CLEARTAGS = ["AssignedCounselor","Intake","Treatment","Diary","Sender","Recipients"]
CLEARTOKEN = "REMOVED"
CLEAREDSTRINGIDS = {"client":"CLIENT"}
OUTFILESUFFIX = "-an"
TMPFILENAME = "tactus-anonymize.py."+str(os.getpid())

clearedStringIds = CLEAREDSTRINGIDS

def getRootOfFile(inFileName):
    return(ET.parse(inFileName))

def normalizeWhiteSpace(string):
    string = re.sub("^\s+","",string)
    string = re.sub("\s+$","",string)
    string = re.sub("\s+"," ",string)
    return(string)

def removeTagText(tag):
    global clearedStringIds

    if not tag.text is None:
        tag.text = normalizeWhiteSpace(tag.text)
        if tag.text != "":
            text = tag.text.lower()
            if not text in clearedStringIds:
                clearedStringIds[text] = CLEARTOKEN+"-"+str(len(clearedStringIds.keys()))
            tag.text = clearedStringIds[text]

def removeTagChildren(tag):
    for child in [c for c in tag]:   
        tag.remove(child)

def clearTexts(tree,tagNames):
    root = tree.getroot()
    for tagName in tagNames:
       for tag in root.findall(".//"+tagName):
           removeTagText(tag)
           removeTagChildren(tag)

def getTextFromXmlText(text):
    try: textTree = ET.fromstring("<container>"+text+"</container>")
    except Exception as e: sys.exit("Error processing text "+text+": "+str(e))
    if not textTree.text is None: text = textTree.text
    else: text = ""
    for node in textTree.findall(".//"):
        if not node.text is None: text += " "+node.text
    return(text)

def runAnonymizeProcess(inText):
    text = getTextFromXmlText(html.escape(inText))
    tmpFile = open(TMPFILENAME,"w")
    print(text,file=tmpFile)
    tmpFile.close()
    anonymizeProcess = subprocess.run([BINDIR+"/"+ANONYMIZEPRG,TMPFILENAME],stdout=subprocess.PIPE)
    anonymizedText = dict(anonymizeProcess.__dict__)["stdout"]
    outText = anonymizedText.decode("utf8")
    os.remove(TMPFILENAME)
    return(outText)

def anonymizeTexts(tree,tagNames):
    root = tree.getroot()
    for tag in root.iter():
        if not tag.text is None:
            if tag.tag in tagNames:
                text = getTextFromXmlText(html.escape(tag.text))
                tag.text = runAnonymizeProcess(text)
            tag.text = html.unescape(tag.text)
            tag.text = re.sub(r"\n+\s*$","",tag.text)

def writeFile(tree,outFileName):
    tree.write(outFileName,encoding="utf-8")

def makeOutFileName(fileName):
    parts = fileName.split(".")
    if len(parts) > 0: parts[-2] += OUTFILESUFFIX
    fileName = ".".join(parts)
    return(fileName)

def main(argv):
    global clearedStringIds

    for inFileName in argv:
        clearedStringIds = CLEAREDSTRINGIDS
        tree = getRootOfFile(inFileName)
        clearTexts(tree,CLEARTAGS)
        anonymizeTexts(tree,ANONYMIZETAGS)
        writeFile(tree,makeOutFileName(inFileName))
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
