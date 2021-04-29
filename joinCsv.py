#!/usr/bin/env python3
"""
    joinCsv.py: join two csv files based on a single key column
    usage: joinCsv.py file1.csv file2.csv keyColumnName
    20191203 erikt(at)xs4all.nl
"""

import csv
import sys

COMMA = ","

def readCsv(inFileName,delimiter=COMMA):
    try:
        if inFileName != "-": inFile = open(inFileName,"r")
        else: inFile = sys.stdin
        csvreader = csv.DictReader(inFile,delimiter=delimiter)
        table = []
        for row in csvreader: table.append(row)
        inFile.close()
        return(table)
    except Exception as e:
        sys.exit(COMMAND+": error processing file "+inFileName+": "+str(e))

def makeDict(table,keyColumnName):
    outDict = {}
    for row in table:
        if not keyColumnName in row:
            print("skipping row from table2:",row,file=sys.stderr)
        elif row[keyColumnName] in outDict:
            print("duplicate key entry in row:",row,":",row[keyColumnName],file=sys.stderr)
        else:
            outDict[row[keyColumnName]] = row
    return(outDict)

def join(table1,table2,keyColumnName):
    table2dict = makeDict(table2,keyColumnName)
    table1out = []
    for row in table1:
        if not keyColumnName in row:
            print("skipping row from table1:",row,file=sys.stderr)
        elif not row[keyColumnName] in table2dict:
            print("unknown key:",row[keyColumnName],"(skipping row)",file=sys.stderr)
        else:
            rowOut = dict(row)
            for key in table2dict[rowOut[keyColumnName]]:
                if key in rowOut and key != keyColumnName:
                    print("warning: overwriting value for key:",key,file=sys.stderr)
                rowOut[key] = table2dict[rowOut[keyColumnName]][key]
            table1out.append(rowOut)
    return(table1out)

def printCsv(table):
    if len(table) > 0:
        fieldNames = table[0].keys()
        csvWriter = csv.DictWriter(sys.stdout,fieldnames=fieldNames)
        csvWriter.writeheader()
        for row in table: csvWriter.writerow(row)

def main(argv):
    inFileName1,inFileName2,keyColumnName = argv[1:]
    table1 = readCsv(inFileName1)
    table2 = readCsv(inFileName2)
    table3 = join(table1,table2,keyColumnName)
    printCsv(table3)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
