#!/usr/bin/python3 -W all
"""
    extractMetadata.py: extract relevant meta data fields from csv file
    usage: extractMetadata.py < file
    note: first convert spss sav file to csv with R
    20180517 erikt(at)xs4all.nl
"""

import csv
import sys

FIELDCESD = "CESD"
FIELDMHC = "mhc"
FIELDT0 = "t0"
FIELDT1 = "t1"
FIELDID = "onderzoeksnummer1"
MAXCESD = 20
MAXMHC = 14
NONE = "NA"
SEPARATOR = ","
MHCVALUES = { "nooit":0,
              "een of twee keer":1,
              "ongeveer een keer per week":2,
              "twee of drie keer per week":3,
              "bijna elke dag":4,
              "elke dag":5,
              "NA":"NA" }
CESDVALUES = { "0":0, "1":1, "2":2, "3":3,
               "zelden of nooit (minder dan 1 dag)":0,
               "soms of weinig (1-2 dagen)":1,
               "regelmatig (3-4 dagen)":2,
               "meestal of altijd (5-7 dagen)":3 }
HEADING = "id,time,cesd,mhc"

def getFieldTotal(row,prefix,suffix,convertor,maxIndex,addZero):
    total = NONE
    for i in range(1,maxIndex+1):
        if addZero and i < 10: strI = "0"+str(i)
        else: strI = str(i)
        fieldName = prefix+strI+"_"+suffix
        if not row[fieldName] == "NA":
            if total != NONE: total += convertor[row[fieldName]]
            else: total = convertor[row[fieldName]]
    return(total)

def doOutput(thisId,cesdTotalT0,cesdTotalT1,mhcTotalT0,mhcTotalT1):
    outString = str(thisId)
    outString += ","+str("T0")
    outString += ","+str(cesdTotalT0)
    outString += ","+str(mhcTotalT0)
    print(outString)
    outString = str(thisId)
    outString += ","+str("T1")
    outString += ","+str(cesdTotalT1)
    outString += ","+str(mhcTotalT1)
    print(outString)
    return()
    
def main(argv):
    csvReader = csv.DictReader(sys.stdin,delimiter=SEPARATOR)
    print(HEADING)
    for row in csvReader:
        cesdTotalT0 = getFieldTotal(row,FIELDCESD,FIELDT0,CESDVALUES,MAXCESD,False)
        cesdTotalT1 = getFieldTotal(row,FIELDCESD,FIELDT1,CESDVALUES,MAXCESD,False)
        mhcTotalT0 = getFieldTotal(row,FIELDMHC,FIELDT0,MHCVALUES,MAXMHC,True)
        mhcTotalT1 = getFieldTotal(row,FIELDMHC,FIELDT1,MHCVALUES,MAXMHC,True)
        doOutput(row[FIELDID],cesdTotalT0,cesdTotalT1,mhcTotalT0,mhcTotalT1)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
