#!/usr/bin/python3 -W all
# computeAveragesPerPerson.py: compute average scores per person
# usage: computeAveragePerPerson.py < file
# note: example input file: AS-mails.csv
# 20180530 erikt(at)xs4all.nl

import csv
import sys

CLIENT = "CLIENT"
COMMAND = sys.argv.pop(0)
REVERSEDASFILE = "/home/erikt/projects/e-mental-health/usb/OVK/data/eriktks/AS/text/reversed.txt"
REVERSEDESFILE = "/home/erikt/projects/e-mental-health/usb/OVK/data/eriktks/ES/text/reversed.txt"
END = "END"
FIELDCLIENTID = "client-id"
FIELDCOUNSELORID = "counselor"
FIELDNBROFCHARSINWORDS = "nbrOfCharsInWords"
FIELDNBROFSENTS = "nbrOfSents"
FIELDNBROFTOKENSINSENTS = "nbrOfTokensInSents"
FIELDNBROFWORDS = "nbrOfWords"
FIELDSENDER = "sender"
HEADING = "id,time,avgSentLen,avgWordLen"
NONE = "NA"
SEPARATOR = ","
START = "START"
SUMMARYCOUNT = 3

def initializeDataField():
    return({FIELDNBROFWORDS:[], FIELDNBROFCHARSINWORDS:[],
        FIELDNBROFSENTS:[], FIELDNBROFTOKENSINSENTS:[] })

def summarizeDataStart(countedElements,countedGroups):
    counter = 0
    nbrOfElements = 0
    nbrOfGroups = 0
    while counter < SUMMARYCOUNT and counter < len(countedElements):
        nbrOfElements += countedElements[counter]
        nbrOfGroups += countedGroups[counter]
        counter += 1
    if nbrOfGroups <= 0: return(NONE)
    else: return(round(nbrOfElements/nbrOfGroups,1))

def summarizeDataEnd(countedElements,countedGroups):
    counter = 0
    nbrOfElements = 0
    nbrOfGroups = 0
    if len(countedElements) >= 2*SUMMARYCOUNT:
        while counter < SUMMARYCOUNT and counter < len(countedElements):
            nbrOfElements += countedElements[-1-counter]
            nbrOfGroups += countedGroups[-1-counter]
            counter += 1
    if nbrOfGroups <= 0: return(NONE)
    else: return(round(nbrOfElements/nbrOfGroups,1))

def readReversedOrder():
    reversedOrder = []
    for reversedFile in (REVERSEDASFILE,REVERSEDESFILE):
        inFile = open(reversedFile,"r")
        for line in inFile:
            line = line.rstrip()
            reversedOrder.append(line)
        inFile.close()
    return(reversedOrder)

def printData(data):
    reversedOrder = readReversedOrder()
    for person in sorted(data.keys()):
        outLine = person
        if person in reversedOrder: outLine += ",T1"
        else: outLine += ",T0"
        outLine += ","+str(summarizeDataStart(data[person][FIELDNBROFTOKENSINSENTS],data[person][FIELDNBROFSENTS]))
        outLine += ","+str(summarizeDataStart(data[person][FIELDNBROFCHARSINWORDS],data[person][FIELDNBROFWORDS]))
        print(outLine)
        outLine = person
        if person in reversedOrder: outLine += ",T0"
        else: outLine += ",T1"
        outLine += ","+str(summarizeDataEnd(data[person][FIELDNBROFTOKENSINSENTS],data[person][FIELDNBROFSENTS]))
        outLine += ","+str(summarizeDataEnd(data[person][FIELDNBROFCHARSINWORDS],data[person][FIELDNBROFWORDS]))
        print(outLine)
    return()

def main(argv):
    csvReader = csv.DictReader(sys.stdin,delimiter=SEPARATOR)
    print(HEADING)
    data = {}
    for row in csvReader:
        if row[FIELDSENDER] == CLIENT: person = row[FIELDCLIENTID]
        else: person = row[FIELDCOUNSELORID]
        if person not in data: data[person] = initializeDataField()
        for field in [FIELDNBROFWORDS,FIELDNBROFCHARSINWORDS,FIELDNBROFSENTS,FIELDNBROFTOKENSINSENTS]:
            data[person][field].append(int(row[field]))
    printData(data)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

