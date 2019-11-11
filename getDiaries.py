#!/usr/bin/env python
# getDiaries.py: extract diaries from questionaires in tactus file
# usage: getDiaries.py file
# 20191111 erikt(at)xs4all.nl

import csv
import gzip
import re
import sys
import xml.etree.ElementTree as ET

DIARYENTRIES = "./Diary/DiaryEntries/DiaryEntry"
QUESTIONNAIRETITLES = { "Intake":True,"Lijst tussenmeting":True,"Lijst nameting":True,"Lijst 3 maanden":True,"Lijst half jaar":True }
ID = "PatientId"
QUESTIONS = "./Content/question"
DATE = "Date"
TIME = "Time"
URGE = "Urge"
STANDARDUNITS = "StandardUnits" 
MEASUREMENTUNITNAME = "MeasurementUnitName"
QUANTITY = "Quantity"
SNAPSHOT = "Snapshot"
FIELDNAMES = [ID,DATE,TIME,URGE,STANDARDUNITS,MEASUREMENTUNITNAME,QUANTITY,SNAPSHOT]
PRESENT =  "present"

def cleanupText(text):
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
            for entry in root.findall(DIARYENTRIES):
                data = initData(thisId)
                for element in entry:
                    if element.tag == DATE: data[DATE] = cleanupText(element.text)
                    elif element.tag == TIME: data[TIME] = cleanupText(element.text)
                    elif element.tag == URGE: data[URGE] = cleanupText(element.text)
                    elif element.tag == STANDARDUNITS: data[STANDARDUNITS] = cleanupText(element.text)
                    elif element.tag == MEASUREMENTUNITNAME: data[MEASUREMENTUNITNAME] = cleanupText(element.text)
                    elif element.tag == QUANTITY: data[QUANTITY] = cleanupText(element.text)
                    elif element.tag == SNAPSHOT: data[SNAPSHOT] = PRESENT
                csvWriter.writerow(data)
 
if __name__ == "__main__":
    sys.exit(main(sys.argv))

exit(0)
