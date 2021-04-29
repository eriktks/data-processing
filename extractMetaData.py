#!/usr/bin/python3 -W all
"""
    extractMetadata.py: extract relevant meta data fields from csv file
    usage: extractMetadata.py < file
    note: first convert spss sav file to csv with R
    20180517 erikt(at)xs4all.nl
"""

import csv
import sys

DATAFILE = "/home/erikt/projects/e-mental-health/usb/ovk/data/eriktks/spss/opve.csv"
FIELDCESDIN = "CESD"
FIELDCESDOUT = "cesd"
FIELDMHC = "mhc"
FIELDT0IN = "t0"
FIELDT0OUT = "T0"
FIELDT1IN = "t1"
FIELDT1OUT = "T1"
FIELDIDIN = "onderzoeksnummer1"
FIELDIDOUT = "id"
FIELDTIME = "timeframe"
MAXCESD = 20
MAXMHC = 14
NA = "NA"
GENDER = "GeslachtA"
FINISHED = "Cursusafgerond"
AGEGROUP = "agegroup2_t0"
AGE = "Leeftijd_t0"
SEPARATOR = ","
MHCVALUES = { "nooit":0,
              "een of twee keer":1,
              "ongeveer een keer per week":2,
              "twee of drie keer per week":3,
              "bijna elke dag":4,
              "elke dag":5 }
CESDVALUES = { "0":0, "1":1, "2":2, "3":3,
               "zelden of nooit (minder dan 1 dag)":0,
               "soms of weinig (1-2 dagen)":1,
               "regelmatig (3-4 dagen)":2,
               "meestal of altijd (5-7 dagen)":3 }
INVERTED = [ [FIELDCESDIN,4],[FIELDCESDIN,8],[FIELDCESDIN,12],[FIELDCESDIN,16] ]
OUTFIELDNAMES= [FIELDIDOUT,FIELDTIME,FIELDCESDOUT,FIELDMHC,GENDER,AGE,AGEGROUP,FINISHED ]

def makeFieldName(prefix,suffix,i,addZero):
    if addZero and i < 10: strI = "0" + str(i)
    else: strI = str(i)
    return(prefix + strI + "_" + suffix)

def computeScore(convertor,dataValue,prefix):
    if not prefix in INVERTED: return(convertor[dataValue])
    else:
        maxValue = max(convertor.values())
        minValue = min(convertor.values())
        return(maxValue+minValue-convertor[dataValue])

def getFieldTotal(row,prefix,suffix,convertor,maxIndex,addZero):
    total = 0
    NAcount = 0
    for i in range(1,maxIndex+1):
        fieldName = makeFieldName(prefix,suffix,i,addZero)
        if row[fieldName] == NA: NAcount += 1
        else: total += computeScore(convertor,row[fieldName],[prefix,i])
    if NAcount > 0: return(NA)
    else: return(total)

def readData(inFileName=DATAFILE):
    try: inFile = open(inFileName,"r")
    except Exception as e: sys.exit(COMMAND+": cannot read from file "+inFileName+" "+str(e))
    csvreader = csv.DictReader(inFile,delimiter=SEPARATOR)
    data = []
    for row in csvreader: data.append(row)
    inFile.close()
    return(data)

def main(argv):
    data = readData(DATAFILE)
    csvwriter = csv.DictWriter(sys.stdout,delimiter=SEPARATOR,fieldnames=OUTFIELDNAMES)
    csvwriter.writeheader()
    for rowIn in data:
        cesdTotalT0 = getFieldTotal(rowIn,FIELDCESDIN,FIELDT0IN,CESDVALUES,MAXCESD,False)
        mhcTotalT0 = getFieldTotal(rowIn, FIELDMHC, FIELDT0IN, MHCVALUES, MAXMHC, True)
        rowOut = { FIELDIDOUT: rowIn[FIELDIDIN],FIELDTIME:FIELDT0OUT,FIELDCESDOUT:cesdTotalT0,FIELDMHC:mhcTotalT0 }
        rowOut = { **rowOut, **{GENDER:rowIn[GENDER],AGEGROUP:rowIn[AGEGROUP],AGE:rowIn[AGE],FINISHED:rowIn[FINISHED]}}
        csvwriter.writerow(rowOut)
        cesdTotalT1 = getFieldTotal(rowIn,FIELDCESDIN,FIELDT1IN,CESDVALUES,MAXCESD,False)
        mhcTotalT1 = getFieldTotal(rowIn, FIELDMHC, FIELDT1IN, MHCVALUES, MAXMHC, True)
        rowOut = { FIELDIDOUT: rowIn[FIELDIDIN],FIELDTIME:FIELDT1OUT,FIELDCESDOUT:cesdTotalT1,FIELDMHC:mhcTotalT1 }
        rowOut = { **rowOut, **{GENDER:rowIn[GENDER],AGEGROUP:rowIn[AGEGROUP],AGE:rowIn[AGE],FINISHED:rowIn[FINISHED]}}
        csvwriter.writerow(rowOut)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
