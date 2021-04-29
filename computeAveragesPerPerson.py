#!/usr/bin/python3 -W all
# computeAveragesPerPerson.py: compute average scores per person
# usage: computeAveragePerPerson.py < file
# note: example input file: AS-mails.csv
# 20180530 erikt(at)xs4all.nl

import csv
import sys

CLIENT = "CLIENT"
COMMAND = sys.argv.pop(0)
END = "END"
FIELDCLIENTID = "client-id"
FIELDCOUNSELORID = "counselor"
FIELDNBROFCHARSINWORDS = "nbrOfCharsInWords"
FIELDNBROFSENTS = "nbrOfSents"
FIELDNBROFTOKENSINSENTS = "nbrOfTokensInSents"
FIELDNBROFWORDS = "nbrOfWords"
FIELDSENDER = "sender"
FIELDID = "id"
FIELDTIMEFRAME = "timeframe"
FIELDAVGSENTLENCLI = "avgSentLenCli"
FIELDAVGWORDLENCLI = "avgWordLenCli"
FIELDAVGSENTLENCOUNS = "avgSentLenCouns"
FIELDAVGWORDLENCOUNS = "avgWordLenCouns"
FIELDNAMES = [FIELDID,FIELDCOUNSELORID,FIELDTIMEFRAME,FIELDAVGSENTLENCLI,FIELDAVGWORDLENCLI,FIELDAVGSENTLENCOUNS,FIELDAVGWORDLENCOUNS]
NA = "NA"
T0 = "T0"
T1 = "T1"
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
    if nbrOfGroups <= 0: return(NA)
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
    if nbrOfGroups <= 0: return(NA)
    else: return(round(nbrOfElements/nbrOfGroups,1))

def makeData(dataIn):
    dataOut = []
    people = sorted(dataIn.keys())
    if len(people) == 2:
        client,counselor = people
        data = { FIELDID:client,FIELDCOUNSELORID:counselor,FIELDTIMEFRAME:T0 }
        data[FIELDAVGSENTLENCLI] = str(summarizeDataStart(dataIn[client][FIELDNBROFTOKENSINSENTS],dataIn[client][FIELDNBROFSENTS]))
        data[FIELDAVGWORDLENCLI] = str(summarizeDataStart(dataIn[client][FIELDNBROFCHARSINWORDS],dataIn[client][FIELDNBROFWORDS]))
        data[FIELDAVGSENTLENCOUNS] = str(summarizeDataStart(dataIn[counselor][FIELDNBROFTOKENSINSENTS],dataIn[counselor][FIELDNBROFSENTS]))
        data[FIELDAVGWORDLENCOUNS] = str(summarizeDataStart(dataIn[counselor][FIELDNBROFCHARSINWORDS],dataIn[counselor][FIELDNBROFWORDS]))
        dataOut.append(dict(data))
        data = {FIELDID: client, FIELDCOUNSELORID: counselor, FIELDTIMEFRAME: T1}
        data[FIELDAVGSENTLENCLI] = str(summarizeDataEnd(dataIn[client][FIELDNBROFTOKENSINSENTS], dataIn[client][FIELDNBROFSENTS]))
        data[FIELDAVGWORDLENCLI] = str(summarizeDataEnd(dataIn[client][FIELDNBROFCHARSINWORDS], dataIn[client][FIELDNBROFWORDS]))
        data[FIELDAVGSENTLENCOUNS] = str(summarizeDataEnd(dataIn[counselor][FIELDNBROFTOKENSINSENTS], dataIn[counselor][FIELDNBROFSENTS]))
        data[FIELDAVGWORDLENCOUNS] = str(summarizeDataEnd(dataIn[counselor][FIELDNBROFCHARSINWORDS], dataIn[counselor][FIELDNBROFWORDS]))
        dataOut.append(dict(data))
    return(dataOut)

def main(argv):
    csvreader = csv.DictReader(sys.stdin,delimiter=SEPARATOR)
    csvwriter = csv.DictWriter(sys.stdout, delimiter=SEPARATOR,fieldnames=FIELDNAMES,restval="NA",lineterminator="\n")
    csvwriter.writeheader()
    data = {}
    clientid = ""
    printData = []
    for row in csvreader:
        if clientid != row[FIELDCLIENTID]:
            if clientid != "":
                printData.extend(makeData(data))
                data = {}
            clientid = row[FIELDCLIENTID]
        if row[FIELDSENDER] == CLIENT: person = row[FIELDCLIENTID]
        else: person = row[FIELDCOUNSELORID]
        if person not in data: data[person] = initializeDataField()
        for field in [FIELDNBROFWORDS,FIELDNBROFCHARSINWORDS,FIELDNBROFSENTS,FIELDNBROFTOKENSINSENTS]:
            data[person][field].append(int(row[field]))
    if clientid != "": printData.extend(makeData(data))
    for pd in printData: csvwriter.writerow(pd)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

