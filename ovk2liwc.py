#!/usr/bin/env python3
"""
    ovk2liwc.py: convert ovk text (in csv format) to liwc feature counts
    usage: ovk2liwc.py < file.csv
    20190211 erikt(at)xs4all.nl
"""

import csv
import sys
import importlib
t2l = importlib.import_module("tactus2liwc-en")

LIWCFILE = "Dutch_LIWC2015_Dictionary.dic"
CLIENT = "CLIENT"
COUNSELOR = "COUNSELOR"
CLIENTIDIN = "client-id"
CLIENTIDOUT = "CLIENTID"
SENDERIN = "sender"
SENDEROUT = "Sender"
NBROFTOKENS = "NBROFTOKENS"
NBROFMATCHES = "NBROFMATCHES"
NBROFSENTS = "NBROFSENTS"
RECIPIENT = "recipient"
DATEIN = "date"
DATEOUT = "DATE"
SUBJECT = "subject"
BODY = "text"
TIMEFRAME = "TIMEFRAME"
CLIENTIDID = 0
SENDERID = 1
SUBJECTID = 4
BODYID = 5
SETSIZE = 3
METADATA = [CLIENTIDOUT,TIMEFRAME,DATEOUT,NBROFSENTS,SENDEROUT,NBROFTOKENS,NBROFMATCHES]
KEYPREFIX = "COUNS_"

def readEmailData():
    emails = []
    csvreader = csv.DictReader(sys.stdin)
    for row in csvreader:
        row = dict(row)
        emails.append([row[CLIENTIDIN],row[SENDERIN],row[RECIPIENT],row[DATEIN],row[SUBJECT],row[BODY]])
    return(emails)

def countMails(emails,sender):
    return(len([email for email in emails if email[SENDERID] == sender]))

def addToSet(sender,set,element,nbrOfUsed):
    if element[SENDERID] == sender:
        if len(set) == 0:
            set = element
            nbrOfUsed = 1
        else:
            set[SUBJECTID] += " "+ element[SUBJECTID]
            set[BODYID] += " " + element[BODYID]
            nbrOfUsed += 1
    return(set,nbrOfUsed)

def combineData(emails,sender,start,end,setSize,getLast=False):
    set = []
    nbrOfUsed = 0
    if not getLast:
        i = start
        while nbrOfUsed < setSize and i <= end:
            set,nbrOfUsed = addToSet(sender,set,emails[i],nbrOfUsed)
            i += 1
    else:
        i = end
        while nbrOfUsed < setSize and i >= start:
            set,nbrOfUsed = addToSet(sender,set,emails[i],nbrOfUsed)
            i -= 1
    return(set)

def combineMails(emailsIn):
    currentId = ""
    currentStart = -1
    emailsOut = []
    for e in range(0,len(emailsIn)):
        if currentId == "":
            currentId = emailsIn[e][CLIENTIDID]
            currentStart = e
        if currentId != emailsIn[e][CLIENTIDID] or e == len(emailsIn)-1:
            firstMails = combineData(emailsIn,CLIENT,currentStart,e-1,SETSIZE)
            if countMails(emailsIn[currentStart:e-1],CLIENT) >= 2*SETSIZE:
                lastMails = combineData(emailsIn,CLIENT,currentStart,e-1,SETSIZE,getLast=True)
                emailsOut.extend([firstMails, lastMails])
            elif countMails(emailsIn[currentStart:e-1],CLIENT) > 0:
                emailsOut.extend([firstMails])
            firstMails = combineData(emailsIn,COUNSELOR,currentStart,e-1,SETSIZE)
            if countMails(emailsIn[currentStart:e-1],COUNSELOR) >= 2*SETSIZE:
                lastMails = combineData(emailsIn,COUNSELOR,currentStart,e-1,SETSIZE,getLast=True)
                emailsOut.extend([firstMails, lastMails])
            elif countMails(emailsIn[currentStart:e-1],COUNSELOR) > 0:
                emailsOut.extend([firstMails])
            currentStart = e
            currentId = emailsIn[e][CLIENTIDID]
    return(emailsOut)

def changeKeys(dictDataIn):
    dictDataOut = {}
    for key in dictDataIn:
        newKey = KEYPREFIX+key
        dictDataOut[newKey] = dictDataIn[key]
    return(dictDataOut)

def printResults(features,results,clientids):
    printData = {}
    allFeatures = METADATA+list(features.values())
    extraFeatures = [ KEYPREFIX+x for x in allFeatures ]
    allFeatures.extend(extraFeatures)
    csvwriter = csv.DictWriter(sys.stdout,fieldnames=allFeatures,restval=0)
    csvwriter.writeheader()
    lastClientId = ""
    for r in range(0,len(results)):
        results[r][CLIENTIDOUT] = clientids[r]
        if clientids[r]+" "+results[r][SENDEROUT] != lastClientId: results[r][TIMEFRAME] = "T0"
        else: results[r][TIMEFRAME] = "T1"
        lastClientId = clientids[r]+" "+results[r][SENDEROUT]
        printDataId = results[r][CLIENTIDOUT]+" "+results[r][TIMEFRAME]
        if not printDataId in printData: printData[printDataId] = results[r]
        else:
            printDataItem = changeKeys(results[r])
            for key in printDataItem: printData[printDataId][key] = printDataItem[key]
    for key in sorted(printData.keys()):
        csvwriter.writerow(printData[key])

def main(argv):
    features,words,prefixes = t2l.readLiwcDict(t2l.LIWCDIR+LIWCFILE)
    emails = readEmailData()
    emailsCombined = combineMails(emails)
    if len(emailsCombined) > 0:
        results = t2l.emails2liwc(emailsCombined,features,words,prefixes)
        clientids = [e[CLIENTIDID] for e in emailsCombined]
        printResults(features,results,clientids)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
