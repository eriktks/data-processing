#!/usr/bin/python3 -W all
# anonymize.py: remove personal information from any text file
# usage: anonymize.py < nerfile
# note: expects line input in ner format: word SPACE pos SPACE ner-tag
# 20180604 erikt(at)xs4all.nl

import random
import re
import sys

COMMAND = sys.argv.pop(0)
NAMESDIR = "/home/erikt/projects/e-mental-health/usb/tmp"
NAMEFILE = NAMESDIR+"/names-ovk.txt"
NEOTHER = "O"
PER = "PER"
LOC = "LOC"
ORG = "ORG"
NUM = "NUM"
DAY = "DAY"
DATE = "DATE"
MONTH = "MONTH"
MAIL = "MAIL"
MISC = "MISC"
NETAGS = {PER,LOC,ORG,NUM,DAY,DATE,MONTH,MAIL,MISC}
DATETAGS = {NUM,DAY,DATE,MONTH}
TAGNUM = "TW"
DOMAINS = "(com|net|nl|org)"
SKIP = { "EFrom","EDate","ETo","Verzonden","Van","Aan","From","To","Date","Sent" }
NAMEWORDS = [ "van","de","der","des","vande","vander","Van","De","Vande","Vander" ]
MONTHS = [ "januari","februari","maart","april","mei","juni","juli", \
           "augustus","september","oktober","november","december", \
           "Januari","Februari","Maart","April","Mei","Juni","Juli", \
           "Augustus","September","Oktober","November","December" ]
WEEKDAYS = [ "zondag","maandag","dinsdag","woensdag","donderdag", \
             "vrijdag","zaterdag", \
             "Zondag","Maandag","Dinsdag","Woensdag","Donderdag", \
             "Vrijdag","Zaterdag", \
             "zondags","maandags","dinsdags","woensdags","donderdags", \
             "vrijdags","zaterdags" ]

def addName(name,myClass):
    global names
    global newNames

    names[name] = myClass
    newNames[name] = myClass
    return()

def storeNewNames():
    global newNames

    if len(newNames) > 0:
        outFile = open(NAMEFILE,"a")
        keys = list(newNames.keys())
        random.shuffle(keys)
        for key in keys:
            print(key,newNames[key],file=outFile)
        outFile.close()
    return()

def compressNE(tokens):
    i = 0
    while i < len(tokens):
        if tokens[i] in NETAGS:
            while i < len(tokens)-1 and tokens[i+1] == tokens[i]: 
                tokens = tokens[:i]+tokens[i+1:]
            if tokens[i] in DATETAGS:
                while i < len(tokens)-1 and tokens[i+1] in DATETAGS:
                    tokens = tokens[:i]+[DATE]+tokens[i+2:]
            if tokens[i] == PER and i < len(tokens)-2 and \
               tokens[i+1] in NAMEWORDS and tokens[i+2] == PER:
                tokens = tokens[:i]+tokens[i+2:]
            if tokens[i] == PER and i < len(tokens)-3 and \
               tokens[i+1] in NAMEWORDS and tokens[i+2] in NAMEWORDS and \
               tokens[i+3] == PER:
                tokens = tokens[:i]+tokens[i+3:]
        i += 1
    return(tokens)

def isEmailHead(tokens):
    return(len(tokens) > 1 and tokens[0] in SKIP and tokens[1] == ":")

def anonymize(tokens,pos,ner):
    global names

    if not isEmailHead(tokens):
        for i in range(0,len(tokens)):
            if tokens[i] in names.keys():
                if names[tokens[i]] != NEOTHER: 
                    tokens[i] = names[tokens[i]]
            elif pos[i] == TAGNUM or re.search(r"^\d",tokens[i]): 
                tokens[i] = NUM
            elif tokens[i] in MONTHS:
                tokens[i] = MONTH
            elif tokens[i] in WEEKDAYS:
                tokens[i] = DAY
            elif re.search(r"@",tokens[i]):
                tokens[i] = MAIL
            elif re.search(r"^www\.",tokens[i],re.IGNORECASE) or \
                 re.search(r"\."+DOMAINS+"$",tokens[i],re.IGNORECASE):
                tokens[i] = ORG
            elif ner[i] != NEOTHER:
                addName(tokens[i],ner[i])
                tokens[i] = ner[i]
            tokens[i] = re.sub(r"^0\d\d\b","PHONE",tokens[i])
            tokens[i] = re.sub(r"\d\d\d\d\d\d*","PHONE",tokens[i])
    tokens = compressNE(tokens)
    line = " ".join(tokens)
    return(line)

def readKnownNames():
    names = {}
    try: 
        inFile = open(NAMEFILE,"r")
        for line in inFile:
            line = line.rstrip()
            try: token,ner = line.split()
            except: sys.exit(COMMAND+": unexpected line in name file: "+line)
            names[token] = ner
        inFile.close()
    except: pass
    return(names,{})

def posTag2base(posTag):
    return(re.sub(r"\(.*$","",posTag))

def neTag2base(neTag):
    return(re.sub(r"^.-","",neTag))

def readSentence():
    tokens,pos,ner = [[],[],[]]
    for line in sys.stdin:
        try:
            line = line.rstrip()
            token,posTag,neTag = line.split()
            posTag = posTag2base(posTag)
            neTag = neTag2base(neTag)
            tokens.append(token)
            pos.append(posTag)
            ner.append(neTag)
        except Exception as e: 
            if line != "": 
                sys.exit(COMMAND+": unexpected line: "+line+" "+str(e))
            if len(tokens) > 0: 
                return(tokens,pos,ner)
    return(tokens,pos,ner)

def main(argv):
    global names,newNames

    names,newNames = readKnownNames()
    tokens,pos,ner = readSentence()
    while len(tokens) > 0:
        print(anonymize(tokens,pos,ner))
        tokens,pos,ner = readSentence()
    storeNewNames()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
