#!/usr/bin/python3 -W all
# anonymize-eng.py: remove personal information from English text file
# usage: anonymize-eng.py [-i] < file.ner
# note: might miss words with punctuation attached to them
# 20181016 erikt(at)xs4all.nl

import getopt
import re
import sys

COMMAND = sys.argv.pop(0)
# NAMESDIR = "/home/erikt/projects/e-mental-health/usb/OVK/data/eriktks/names"
NAMESDIR = "/home/erikt/projects/e-mental-health/usb"
POSITIVENAMEFILE = NAMESDIR+"/positiveNamesEng.txt"
NEGATIVENAMEFILE = NAMESDIR+"/negativeNamesEng.txt"
NEOTHER = "O"
PER = "PERSON"
LOC = "LOCATION"
ORG = "ORGANIZATION"
STOP = "x"
TAGNUM = "TW"
NAMEWORDS = [ ]
SKIP = [ ]
MONTHS = [ "january","february","march","april","may","june","july", \
           "august","september","october","november","december", \
           "January","February","March","April","May","June","July", \
           "August","September","October","November","December" ]
WEEKDAYS = [ "sunday","monday","tuesday","wednesday","thursday", \
             "friday","saturday", \
             "Sunday","Monday","Tuesday","Wednesday","Thursday", \
             "Friday","Saturday", \
             "Sundays","Mondays","Tuesdays","Wednesdays","Thursdays", \
             "Fridays","Saturdays",
             "Sun","Mon","Tue","Wed","Thu","Fri","Sat","Sun" ]

def check(name,ner):
    print("? ("+ner+") "+name+" ",end="")
    sys.stdout.flush()
    response = sys.stdin.readline().rstrip()
    if response == STOP: sys.exit(COMMAND+": stopped")
    if response == "1": response = ner
    return(response)

def addNegative(name):
    global negativeNames

    negativeNames[name] = False
    outFile = open(NEGATIVENAMEFILE,"a")
    print(name,file=outFile)
    outFile.close()
    return()

def addPositive(name,myClass):
    global positiveNames

    positiveNames[name] = myClass
    outFile = open(POSITIVENAMEFILE,"a")
    print(name+" "+myClass,file=outFile)
    outFile.close()
    return()

def compressPER(tokens):
    counter = 0
    while counter < len(tokens):
        if tokens[counter] != PER: counter += 1
        else:
            nextCounter = counter
            allChecked = False
            while not allChecked:
                if nextCounter < len(tokens)-1 and \
                   tokens[nextCounter+1] == PER:
                    nextCounter += 1
                elif nextCounter < len(tokens)-2 and \
                   tokens[nextCounter+1] in NAMEWORDS and \
                   tokens[nextCounter+2] == PER:
                    nextCounter += 2
                elif nextCounter < len(tokens)-2 and \
                   tokens[nextCounter+1] in NAMEWORDS and \
                   tokens[nextCounter+2] in NAMEWORDS and \
                   tokens[nextCounter+3] == PER:
                    nextCounter += 2
                else: allChecked = True
            tokens = tokens[:counter]+[PER]+tokens[nextCounter+1:]
            counter += 1
    return(tokens)

def anonymize(tokens,pos,ner,interactive):
    global positiveNames,negativeNames

    if len(tokens) > 1 and tokens[0] in SKIP and tokens[1] == ":":
        return(" ".join(tokens))
    for i in range(0,len(tokens)):
        if tokens[i] in positiveNames.keys():
            if positiveNames[tokens[i]] != NEOTHER:
                tokens[i] = positiveNames[tokens[i]]
        elif pos[i] == TAGNUM or re.search(r"^\d",tokens[i]): 
            tokens[i] = "NUM"
        elif tokens[i] in MONTHS:
            tokens[i] = "MONTH"
        elif tokens[i] in WEEKDAYS:
            tokens[i] = "DAY"
        elif re.search(r"@",tokens[i]):
            tokens[i] = "MAIL"
        elif re.search(r"^www\.",tokens[i],re.IGNORECASE) or \
             re.search(r"\.nl$",tokens[i],re.IGNORECASE):
            tokens[i] = ORG
        elif (ner[i] != NEOTHER or pos[i] == "SPEC") and \
            not tokens[i] in negativeNames.keys():
            if interactive:
                checkOutput = check(tokens[i],ner[i])
                if not checkOutput: addNegative(tokens[i])
                else:
                    addPositive(tokens[i],checkOutput)
                    tokens[i] = checkOutput
            else:
                addPositive(tokens[i],ner[i])
                if ner[i] != NEOTHER: tokens[i] = ner[i]

        tokens[i] = re.sub(r"^0\d\d\b","PHONE",tokens[i])
        tokens[i] = re.sub(r"\d\d\d\d\d\d*","PHONE",tokens[i])
    tokens = compressPER(tokens)
    line = " ".join(tokens)
    return(line)

def readPositiveNames():
    data = {}
    inFile = open(POSITIVENAMEFILE,"r")
    for line in inFile:
        line = line.rstrip()
        try: token,ner = line.split()
        except: sys.exit(COMMAND+": unexpected line in positive file: "+line)
        data[token] = ner
    inFile.close()
    return(data)

def readNegativeNames():
    data = {}
    inFile = open(NEGATIVENAMEFILE,"r")
    for line in inFile:
        line = line.rstrip()
        try: [token] = line.split()
        except: sys.exit(COMMAND+": unexpected line in negative file: "+line)
        data[token] = False
    inFile.close()
    return(data)

positiveNames = readPositiveNames()
negativeNames = readNegativeNames()

def main(argv):
    try: optionList, files = getopt.getopt(argv,"i",[])
    except: sys.exit("usage: "+COMMAND+" [-i] < nerfile ")
    interactive = "-i" in dict(optionList).keys()
    ner,pos,tokens = [[],[],[]]
    for line in sys.stdin:
        try:
            line = line.rstrip()
            token,tag,ne = line.split()
            tag = re.sub(r"\(.*$","",tag)
            ne = re.sub(r"\(.*$","",ne)
            ne = re.sub(r"^.-","",ne)
            tokens.append(token)
            pos.append(tag)
            ner.append(ne)
        except: 
            if line != "": sys.exit(COMMAND+": unexpected line: "+line)
            elif len(tokens) > 0: 
                 print(anonymize(tokens,pos,ner,interactive))
                 tokens,pos,ner = ([],[],[])
    if len(tokens) > 0: 
         print(anonymize(tokens,pos,ner,interactive))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
