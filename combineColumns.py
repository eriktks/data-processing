#!/usr/bin/env python
"""
    combineColumns.py: combine columns in csv file with variant names
    usage: combineColumns.pf < file.csv
    20191112 erikt(at)xs4all.nl
"""

import csv
import re
import sys

EMPTY = "EMPTY"
REQUESTED = {"8-opleidng0":"4-opleidng","12-aanleid0":"7-aanleid","25-behdrinkt0":"19-behdrink"}
EXCEPTIONS = [ "14-drugs0","14-drugs1","14-drugs2","14-drugs3","14-drugs4","14-drugs5","25-rcq10","25-rcq11","25-rcq12","22-medi00","31-dass100","31-dass200","1-medi0n","1-medi1n","34-medi02","34-medi12","34-medi22","34-medi32","34-medi42","34-medi52","38-mateicn100","37-dass122","38-dass122","41-mateicn122","42-mateicn122" ]

def findDuplicateColumns(columnNames):
    duplicateColumns = REQUESTED
    for columnName in columnNames:
        shortName = re.sub(r"..$",r"",columnName)
        if shortName in columnNames and not columnName in EXCEPTIONS:
            duplicateColumns[columnName] = shortName
        else:
            shortName = re.sub(r".$",r"",columnName)
            if shortName in columnNames and not columnName in EXCEPTIONS:
                duplicateColumns[columnName] = shortName
    return(duplicateColumns)

def main(argv):
    duplicateColumns = None
    csvreader = csv.DictReader(sys.stdin,delimiter=',',quotechar='"')
    fieldNames = None
    csvwriter = None
    for row in csvreader:
        row = dict(row)
        if duplicateColumns == None: 
            duplicateColumns = findDuplicateColumns(row.keys())
            fieldNames = [x for x in row if not x in duplicateColumns]
            csvwriter = csv.DictWriter(sys.stdout,delimiter=',',quotechar='"',fieldnames=fieldNames)
            csvwriter.writeheader()
        for key in duplicateColumns:
            if key in row and row[key] != EMPTY:
                if duplicateColumns[key] not in row or row[duplicateColumns[key]] == EMPTY:
                    row[duplicateColumns[key]] = row[key]
                else:
                    print("clash",key,row[key],duplicateColumns[key],row[duplicateColumns[key]],file=sys.stderr)
                    row[duplicateColumns[key]] += "#"+row[key]
        outRow = {key:row[key] for key in row if not key in duplicateColumns}
        csvwriter.writerow(outRow)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
