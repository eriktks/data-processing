#!/usr/bin/python3 -W all
# computeAveragesPerPerson.py: compute average scores per person
# usage: computeAveragePerPerson.py < file
# 20180530 erikt(at)xs4all.nl

import csv
import sys

CLIENT = "CLIENT"
COMMAND = sys.argv.pop(0)
FIELDCLIENTID = "client-id"
FIELDCOUNSELORID = "counselor"
FIELDNBROFCHARSINWORDS = "nbrOfCharsInWords"
FIELDNBROFSENTS = "nbrOfSents"
FIELDNBROFTOKENSINSENTS = "nbrOfTokensInSents"
FIELDNBROFWORDS = "nbrOfWords"
FIELDSENDER = "sender"
HEADING = "client-id,avgSentLen,avgWordLen"
SEPARATOR = ","

def initializeDataField():
    return({FIELDNBROFWORDS:0, FIELDNBROFCHARSINWORDS:0,
        FIELDNBROFSENTS:0, FIELDNBROFTOKENSINSENTS:0 })

def printData(data):
    for person in sorted(data.keys()):
        outLine = person
        outLine += ","+str(round(data[person][FIELDNBROFTOKENSINSENTS]/data[person][FIELDNBROFSENTS],1))
        outLine += ","+str(round(data[person][FIELDNBROFCHARSINWORDS]/data[person][FIELDNBROFWORDS],1))
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
            data[person][field] += int(row[field])
    printData(data)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

