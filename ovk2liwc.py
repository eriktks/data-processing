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

CLIENTID = "client-id"
SENDER = "sender"
RECIPIENT = "recipient"
DATE = "date"
SUBJECT = "subject"
BODY = "text"

def readEmailData():
    emails = []
    csvreader = csv.DictReader(sys.stdin)
    for row in csvreader:
        row = dict(row)
        emails.append([row[CLIENTID],row[SENDER],row[RECIPIENT],row[DATE],row[SUBJECT],row[BODY]])
    return(emails)

def main(argv):
    features,words,prefixes = t2l.readLiwcDict(t2l.LIWCDIR+t2l.LIWCFILE)
    emails = readEmailData()
    if len(emails) > 0: t2l.emails2liwc(emails,features,words,prefixes)
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
