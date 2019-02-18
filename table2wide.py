#!/usr/bin/python3 -W all
"""
   table2wide.py: convert table to wide format
   usage: table2wide.py < file
   note: table-specific because of in-code definition of column roles
   20180618 erikt(at)xs4all.nl
"""

import csv
import sys

ID = "id"
EMPTYDICT = {}
KEEP = [ID,"treatment","counselor"]
SEPARATOR = ","
TIME = "timeframe"
TIMES = ["T0","T1"]

def makeNewFieldNames(fieldNamesIn):
    fieldNamesOut = list(KEEP)
    for field in fieldNamesIn:
        if not field in KEEP and field != TIME:
            for time in TIMES:
                fieldNamesOut.append(field+time)
    return(fieldNamesOut)

def fillWithNA(fieldNames):
    return({ f:"NA" for f in fieldNames })

def main(argv):
    csvreader = csv.DictReader(sys.stdin,delimiter=SEPARATOR)
    fieldNames = makeNewFieldNames(csvreader.fieldnames)
    csvwriter = csv.DictWriter(sys.stdout,delimiter=SEPARATOR,fieldnames=fieldNames)
    csvwriter.writeheader()
    lastRow = EMPTYDICT
    for row in csvreader:
        if lastRow == EMPTYDICT:
            lastRow = row
            row = csvreader.__next__()
        outRow = fillWithNA(fieldNames)
        for field in KEEP: outRow[field] = lastRow[field]
        for field in row.keys():
            if not field in KEEP and field != TIME:
                outRow[field+lastRow[TIME]] = lastRow[field]
                if row[ID] == lastRow[ID]: outRow[field+row[TIME]] = row[field]
        csvwriter.writerow(outRow)
        if row[ID] == lastRow[ID]: lastRow = EMPTYDICT
        else: lastRow = row

if __name__ == "__main__":
    sys.exit(main(sys.argv))
