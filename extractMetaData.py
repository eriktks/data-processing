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

def main(argv):
    csvReader = csv.DictReader(sys.stdin,delimiter=SEPARATOR)
    for row in csvReader:
        cesdTotalT0 = 0
        cesdTotalT1 = 0
        mhcTotalT0 = 0
        mhcTotalT1 = 0
        for i in range(1,MAXCESD+1):
            strI = str(i)
            fieldName0 = FIELDCESD+strI+"_"+FIELDT0
            if not row[fieldName0] == "NA":
                cesdTotalT0 += CESDVALUES[row[fieldName0]]
            fieldName1 = FIELDCESD+strI+"_"+FIELDT1
            if not row[fieldName1] == "NA":
                cesdTotalT1 += CESDVALUES[row[fieldName1]]
        for i in range(1,MAXMHC+1):
            if i < 10: strI = "0"+str(i)
            else: strI = str(i)
            fieldName0 = FIELDMHC+strI+"_"+FIELDT0
            if not row[fieldName0] == "NA":
                mhcTotalT0 += MHCVALUES[row[fieldName0]]
            fieldName1 = FIELDMHC+strI+"_"+FIELDT1
            if not row[fieldName1] == "NA":
                mhcTotalT1 += MHCVALUES[row[fieldName1]]
        print(row[FIELDID]+","+str(cesdTotalT0)+","+str(cesdTotalT1)+","+str(mhcTotalT0)+","+str(mhcTotalT1))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
