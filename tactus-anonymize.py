#!/usr/bin/env python
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
DATADIR = "/home/erikt/projects/e-mental-health/usb/tmp"
ANONYMIZEPRG = "anonymize-dut.sh"
COUNSELORFILE = "counselors.txt"
ANONYMIZETAGS = ["Body","Subject", "Notes"]
COUNSELORTAG = "AssignedCounselor"
FIRSTNAMETAG = "FirstName"
LASTNAMETAG = "LastName"
KEEPTAGS = ["Dossier","AssignedCounselor","Messages","Message","DateSent","Subject","Body"]
KEEPTAGSTEXTTRACE = ["Sender","Recipients"]
CLEARTOKEN = "REMOVED"
CLEAREDSTRINGIDS = {"client":"CLIENT"}
OUTFILESUFFIX = "-an"
TMPFILENAME = "tactus-anonymize.py."+str(os.getpid())
BOUNDARY = "tactus-anonymize-py-mail-text-boundary"

clearedStringIds = CLEAREDSTRINGIDS
counselorIds = {}

def getRootOfFile(inFileName):
    return(ET.parse(inFileName))

def normalizeWhiteSpace(string):
    string = re.sub("^\s+","",string)
    string = re.sub("\s+$","",string)
    string = re.sub("\s+"," ",string)
    return(string)

def readCounselors():
    global counselorIds

    try:
        inFile = open(DATADIR+"/"+COUNSELORFILE,"r")
        for line in inFile:
            fields = normalizeWhiteSpace(line).strip().split()
            thisId = fields.pop(0)
            counselor = normalizeWhiteSpace(" ".join(fields))
            counselorIds[counselor] = thisId
        inFile.close()
    except: 
        sys.exit("error reading counselor file: "+DATADIR+"/"+COUNSELORFILE)

def removeTagText(tag,tagNamesKeepTextTrace):
    global clearedStringIds

    if not tag.text is None:
        if not tag.tag in tagNamesKeepTextTrace:
            tag.text = ""
        else:
            tag.text = normalizeWhiteSpace(tag.text)
            if tag.text != "":
                text = tag.text.lower()
                if not text in clearedStringIds:
                    clearedStringIds[text] = CLEARTOKEN+"-"+str(len(clearedStringIds.keys()))
                tag.text = clearedStringIds[text]

def removeTagChildren(tag):
    for child in [c for c in tag]:   
        tag.remove(child)

def clearTexts(tree,tagNamesKeep,tagNamesKeepTextTrace):
    root = tree.getroot()
    for tag in root.iter():
        if not tag.tag in tagNamesKeep:
            removeTagText(tag,tagNamesKeepTextTrace)
            removeTagChildren(tag)

def getChildText(tag,childName):
    childText = ""
    for child in tag.findall("./"+childName):
        try:
            if childText == "": childText = normalizeWhiteSpace(child.text)
            else: childText += " "+normalizeWhiteSpace(child.text)
        except: pass
    return(childText)

def getCounselorId(firstName,lastName):
    global counselorIds

    if firstName == "" and lastName == "": return("")
    name = normalizeWhiteSpace(firstName+" "+lastName)
    if not name in counselorIds: 
        counselorIds[name] = 1+len(counselorIds)
        try: outFile = open(DATADIR+"/"+COUNSELORFILE,"a")
        except: sys.exit("error writing counselor file: "+DATADIR+"/"+COUNSELORFILE)
        print(counselorIds[name],name,file=outFile)
        outFile.close()
    return(counselorIds[name])

def anonymizeCounselor(tree,tagNamesKeepTextTrace):
    root = tree.getroot()
    for tag in root.findall(".//"+COUNSELORTAG):
        firstName = getChildText(tag,FIRSTNAMETAG)
        lastName = getChildText(tag,LASTNAMETAG)
        removeTagText(tag,tagNamesKeepTextTrace)
        removeTagChildren(tag)
        tag.text = str(getCounselorId(firstName,lastName))

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

def getMailTexts(tree,tagNames):
    root = tree.getroot()
    textList = []
    for tag in root.iter():
        if not tag.text is None:
            if tag.tag in tagNames:
                textList.append(getTextFromXmlText(html.escape(tag.text)))
    return(textList)

def processedTextToList(processedText):
    processedList = []
    currentText = ""
    for line in processedText.split("\n"):
        if not re.search("^"+BOUNDARY,line): currentText += line+"\n"
        else:
            processedList.append(str(currentText))
            currentText = ""
    processedList.append(str(currentText))
    return(processedList)

def updateMailTexts(tree,tagNames,processedList):
    root = tree.getroot()
    i = 0
    for tag in root.iter():
        if not tag.text is None:
            if tag.tag in tagNames:
                tag.text = processedList[i]
                i += 1
                tag.text = html.unescape(tag.text)
                tag.text = re.sub(r"\n+\s*$","",tag.text)

def anonymizeTexts(tree,tagNames):
    textList = getMailTexts(tree,tagNames)
    if len(textList) > 0:
        text = (BOUNDARY+"\n").join(textList)
        processedText = runAnonymizeProcess(text)
        processedList = processedTextToList(processedText)
        updateMailTexts(tree,tagNames,processedList)

def writeFile(tree,outFileName):
    tree.write(outFileName,encoding="utf-8")

def makeOutFileName(fileName):
    parts = fileName.split(".")
    if len(parts) > 0: parts[-2] += OUTFILESUFFIX
    fileName = ".".join(parts)
    return(fileName)

def main(argv):
    global clearedStringIds

    readCounselors()
    for inFileName in argv:
        clearedStringIds = CLEAREDSTRINGIDS
        tree = getRootOfFile(inFileName)
        anonymizeCounselor(tree,KEEPTAGSTEXTTRACE)
        clearTexts(tree,KEEPTAGS,KEEPTAGSTEXTTRACE)
        anonymizeTexts(tree,ANONYMIZETAGS)
        writeFile(tree,makeOutFileName(inFileName))
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
