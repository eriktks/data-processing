#!/usr/bin/python3 -W all
# anonymize.py: remove personal information from any text file
# usage: anonymize.py [nerFile1 [nerFile2 ...]]
# note: might miss words with punctuation attached to them
# 20180604 erikt(at)xs4all.nl

import re
import sys

COMMAND = sys.argv.pop(0)
NAMESDIR = "/home/erikt/projects/e-mental-health/usb/OVK/data/eriktks/names"
POSITIVENAMEFILE = NAMESDIR+"/positiveNames.txt"
NEGATIVENAMEFILE = NAMESDIR+"/negativeNames.txt"
TAGNUM = "TW"
NEOTHER = "O"
SKIP = [ "EFrom","EDate","Verzonden","Van","Aan","From","To","Date" ]
MONTHS = [ "januari","februari","maart","april","mei","juni","juli", \
           "augustus","september","oktober","november","december" ]
WEEKDAYS = [ "zondag","maandag","dinsdag","woensdag","donderdag", \
             "vrijdag","zaterdag" ]

def check(name,ner,nerFile):
    print(nerFile+"? ("+ner+") "+name+" ",end="")
    sys.stdout.flush()
    response = sys.stdin.readline().rstrip()
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

def anonymize(tokens,pos,ner,nerFile):
    global positiveNames,negativeNames

    if len(tokens) > 1 and tokens[0] in SKIP and tokens[1] == ":":
        return(" ".join(tokens))
    for i in range(0,len(tokens)):
        if tokens[i] in positiveNames.keys():
            tokens[i] = positiveNames[tokens[i]]
        elif pos[i] == TAGNUM: 
            tokens[i] = "NUM"
        elif re.search(r"@",tokens[i]):
            tokens[i] = "MAIL"
        elif tokens[i] in MONTHS:
            tokens[i] = "MONTH"
        elif tokens[i] in WEEKDAYS:
            tokens[i] = "DAY"
        elif (ner[i] != NEOTHER or pos[i] == "SPEC") and \
            not tokens[i] in negativeNames.keys():
            checkOutput = check(tokens[i],ner[i],nerFile)
            if not checkOutput: addNegative(tokens[i])
            else:
                addPositive(tokens[i],checkOutput)
                tokens[i] = checkOutput
        tokens[i] = re.sub(r"^0\d\d\b","PHONE",tokens[i])
        tokens[i] = re.sub(r"\d\d\d\d\d\d*","PHONE",tokens[i])
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
    for nerFile in argv:
        tokens,pos,ner = ([],[],[])
        try: inFile = open(nerFile,"r")
        except: sys.exit(COMMAND+": cannot read file "+nerFile)
        outFile = open(nerFile+".out","w")
        for line in inFile:
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
                    print(anonymize(tokens,pos,ner,nerFile),file=outFile)
                    tokens,pos,ner = ([],[],[])
        outFile.close()
        inFile.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
