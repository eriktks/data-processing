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
CLIENTID = "client-id"
SENDER = "sender"
RECIPIENT = "recipient"
DATE = "date"
SUBJECT = "subject"
BODY = "text"
CLIENTIDID = 0
SENDERID = 1
SUBJECTID = 4
BODYID = 5
SETSIZE = 3
METADATA = ["CLIENTID","DATE","NBROFSENTS","Sender","NBROFTOKENS","NBROFMATCHES"]

def readEmailData():
    emails = []
    csvreader = csv.DictReader(sys.stdin)
    for row in csvreader:
        row = dict(row)
        emails.append([row[CLIENTID],row[SENDER],row[RECIPIENT],row[DATE],row[SUBJECT],row[BODY]])
    return(emails)

def addToSet(set,element,nbrOfUsed):
    if element[SENDERID] == "CLIENT":
        if len(set) == 0:
            set = element
            nbrOfUsed = 1
        else:
            set[SUBJECTID] += " "+ element[SUBJECTID]
            set[BODYID] += " " + element[BODYID]
            nbrOfUsed += 1
    return(set,nbrOfUsed)

def combineData(emails,start,end,setSize,getLast=False):
    set = []
    nbrOfUsed = 0
    if not getLast:
        i = start
        while nbrOfUsed < setSize and i <= end:
            set,nbrOfUsed = addToSet(set,emails[i],nbrOfUsed)
            i += 1
    else:
        i = end
        while nbrOfUsed < setSize and i >= start:
            set,nbrOfUsed = addToSet(set, emails[i],nbrOfUsed)
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
            firstMails = combineData(emailsIn,currentStart,e-1,SETSIZE)
            lastMails = combineData(emailsIn,currentStart,e-1,SETSIZE,getLast=True)
            emailsOut.extend([firstMails,lastMails])
            currentStart = e
            currentId = emailsIn[e][CLIENTIDID]
    return(emailsOut)

def printResults(features,results,clientids):
    allFeatures = METADATA+list(features.keys())
    csvwriter = csv.DictWriter(sys.stdout,fieldnames=allFeatures)
    for r in range(0,len(results)):
        for f in allFeatures: 
            if not f in results[r] or type(results[r][f]) == type(None): 
                results[r][f] = ""
        results[r]["CLIENTID"] = clientids[r]
        csvwriter.writerow(results[r])

def main(argv):
    features,words,prefixes = t2l.readLiwcDict(t2l.LIWCDIR+LIWCFILE)
    emails = readEmailData()
    emailsCombined = combineMails(emails)
    if len(emailsCombined) > 0: 
        results = t2l.emails2liwc(emailsCombined,features,words,prefixes)
        clientids = [e[CLIENTIDID] for e in emailsCombined]
        printResults(features,results,clientids)
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
