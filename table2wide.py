#!/usr/bin/python3 -W all
"""
   table2wide.py: convert table to wide format
   usage: table2wide.py < file
   note: table-specific because of in-code definition of column roles
   20180618 erikt(at)xs4all.nl
"""

import csv
import sys

COMBINE = ["cesd","mhc","avgSentLenCli","avgWordLenCli"]
ID = "id"
KEEP = ["id","treatment","counselor","avgSentLenCouns","avgWordLenCouns"]
SEPARATOR = ","
TIME = "time"
TIMES = ["T0","T1"]

def makeNewFieldNames():
    fieldNames = list(KEEP)
    for field in COMBINE:
        for time in TIMES:
            fieldNames.append(field+time)
    return(fieldNames)

def main(argv):
    csvReader = csv.DictReader(sys.stdin,delimiter=SEPARATOR)
    fieldNames = makeNewFieldNames()
    # do not use csvWriter: it generates invisible line-end characters
    for i in range(0,len(fieldNames)): 
        if i > 0: print(SEPARATOR,end="")
        print(fieldNames[i],end="")
    print()
    lastRow = {"id":"" }
    for row in csvReader:
        if lastRow["id"] == "":
            lastRow = row
            row = csvReader.__next__()
        outRow = {}
        for field in KEEP: outRow[field] = lastRow[field].replace("\r","")
        for field in COMBINE:
            outRow[field+lastRow[TIME]] = lastRow[field].replace("\r","")
            if row[ID] == lastRow[ID]: outRow[field+row[TIME]] = row[field].replace("\r","")
        for i in range(0,len(fieldNames)):
            if i > 0: print(SEPARATOR,end="")
            print(outRow[fieldNames[i]],end="")
        print()
        if row[ID] != lastRow[ID]: lastRow = row
        else: lastRow = { "id":"" }

if __name__ == "__main__":
    sys.exit(main(sys.argv))
