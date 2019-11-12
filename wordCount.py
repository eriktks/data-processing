#!/usr/bin/env python
# getDiaries.py: extract diaries from questionaires in tactus file
# usage: getDiaries.py file
# 20191111 erikt(at)xs4all.nl

import csv
import gzip
import re
import sys
import xml.etree.ElementTree as ET

MESSAGES = "./Messages/Message"
ID = "PatientId"
DATE = "DateSent"
SENDER = "Sender"
BODY = "Body"
SUBJECT = "Subject"
WORDCOUNT = "WordCount"
CLIENT = "CLIENT"
TOTAL = "Total"
YES = "yes"
FIELDNAMES = [ID,DATE,SENDER,WORDCOUNT,TOTAL]

def cleanupText(text):
    if text == None: return("")
    text = re.sub(r"\s+"," ",text)
    text = re.sub(r"^ ","",text)
    text = re.sub(r" $","",text)
    return(text)

def makeId(fileName):
    thisId = re.sub(r".*/","",fileName)
    thisId = re.sub(r"\.xml.*$","",thisId)
    return(thisId)

def initData(thisId):
    data = { ID:thisId}
    for fieldName in FIELDNAMES: 
        if fieldName != ID: data[fieldName] = ""
    return(data)

def wordCount(text):
    return(len(text.split()))

def main(argv):
    with sys.stdout as csvFile:
        csvWriter = csv.DictWriter(csvFile,fieldnames=FIELDNAMES)
        csvWriter.writeheader()
        for inFileName in argv[1:]:
            inFile = gzip.open(inFileName,"rb")
            inFileContent = inFile.read()
            inFile.close()
            root = ET.fromstring(inFileContent)
            thisId = makeId(inFileName)
            clientTotal = 0
            for message in root.findall(MESSAGES):
                data = initData(thisId)
                wordCountBody,wordCountSubject = 0,0
                for element in message:
                    if element.tag == DATE: data[DATE] = cleanupText(element.text)
                    elif element.tag == SENDER: data[SENDER] = cleanupText(element.text)
                    elif element.tag == SUBJECT: 
                        wordCountSubject = wordCount(cleanupText(element.text))
                    elif element.tag == BODY: 
                        wordCountBody = wordCount(cleanupText(element.text))
                data[WORDCOUNT] = wordCountSubject+wordCountBody
                if SENDER in data and data[SENDER] == CLIENT: 
                    clientTotal += data[WORDCOUNT]
                csvWriter.writerow(data)
            data = initData(thisId)
            data[SENDER] = CLIENT
            data[TOTAL] = YES
            data[WORDCOUNT] = clientTotal
            csvWriter.writerow(data)
 
if __name__ == "__main__":
    sys.exit(main(sys.argv))

exit(0)
