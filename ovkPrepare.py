#!/usr/bin/python3 -W all
"""
    ovkPrepare.py: prepare ovk text files for conversion to csv
    usage: ovkPrepare.py [-g] file1 [file2 ...]
    note: option -g: use greetings as mail boundaries instead of dates
    20180509 erikt(at)xs4all.nl
"""

import getopt
import re
import sys

COMMAND = sys.argv.pop(0)
CHARPATTERN = r"[a-zA-Z]"
DATEHEADING = "EDate: "
DATESEP = "-"
DATEPATTERNALPHA = r"^\s*(\d\d?)\s+([a-z]+)\.?(\s+(\d+))?\s*$"
DATEPATTERNALPHADAY = 1
DATEPATTERNALPHAMONTH = 2
DATEPATTERNALPHAYEAR = 3
DATEPATTERNNUM = r"^\s*(([A-Za-z]+)\s+)?(\d+)\s*"+DATESEP+r"\s*(\d+)\s*"+DATESEP+r"\s*(\d+)\b$"
DATEPATTERNNUMWEEKDAY = 2
DATEPATTERNNUMDAY = 3
DATEPATTERNNUMMONTH = 4
DATEPATTERNNUMYEAR = 5
DEFAULTYEAR = "2011"
FROMHEADING = "EFrom: "
GREETPATTERN = r"^([A-Za-z]+)\s+([A-Za-z0-9]+)\b"
GREETPATTERNGREET = 1
GREETPATTERNTARGET = 2
GREETINGS = ["Beste","Dag","Goedeavond","Goedemorgen","Hallo","Hi","Hoi"]
MONTHS = { "jan":"1","feb":"2","mrt":"3","apr":"4","mei":"5","jun":"6", \
           "jul":"7","aug":"8","sep":"9","okt":"10","nov":"11","dec":"12",
           "maart":"3","april":"4" }
NAMEPATTERN = r"([A-Za-z0-9]+)\s*$"
NAMEPATTERNTARGET = 1
SUSPECTEDPATTERN = r"^\s*[A-Z][a-z]+:"
UNKNOWN = "???"
USAGE = "usage: "+COMMAND+" [-g] file1 [file2 ...]"

def warn(message):
    print(COMMAND+": "+message,file=sys.stderr)
    return()

def error(message):
    warn(message)
    sys.exit(0)

def getClientName(fileName):
    matchId = re.search(r"^(\d+)\.",fileName)
    if matchId: return(matchId.group(1))
    else: error("cannot extract client name from file name: "+fileName)

def containsChars(string):
    return(re.search(CHARPATTERN,string))

def getCounselorName(lines):
    candidates = {}
    for line in lines:
        candidate = ""
        matchName = re.search(NAMEPATTERN,line)
        matchGreet = re.search(GREETPATTERN,line)
        if matchName and containsChars(matchName.group(NAMEPATTERNTARGET)): 
            candidate = matchName.group(NAMEPATTERNTARGET)
        elif matchGreet and containsChars(matchGreet.group(GREETPATTERNGREET)) \
             and matchGreet.group(GREETPATTERNGREET) in GREETINGS: 
            candidate = matchGreet.group(GREETPATTERNTARGET)
        if candidate != "":
            if candidate in candidates: candidates[candidate] += 1
            else: candidates[candidate] = 1
    if not candidates: return("")
    else: 
        return(sorted(candidates,key=candidates.get,reverse=True)[0])

def readTextFile(fileName):
    lines = []
    try:
        inFile = open(fileName,"r")
        for line in inFile: lines.append(line)
        inFile.close()
    except: error("cannot read file "+fileName)
    return(lines)

def printMailText(client,counselor,date,mailText,receiver):
    if receiver == client: sender = counselor
    elif receiver == counselor: sender = client
    else: sender = UNKNOWN
    print(FROMHEADING+sender)
    if date != "": print(DATEHEADING+date)
    print("")
    print(mailText)
    return()

def getDateNum(line):
    matchDateNum = re.search(DATEPATTERNNUM,line)
    if not matchDateNum: date = ""
    else:
        weekday = matchDateNum.group(DATEPATTERNNUMWEEKDAY)
        day = matchDateNum.group(DATEPATTERNNUMDAY)
        month = matchDateNum.group(DATEPATTERNNUMMONTH)
        year = matchDateNum.group(DATEPATTERNNUMYEAR)
        date = day+DATESEP+month+DATESEP+year
        if weekday: date = weekday+" "+date
    return(date)

def getDateAlpha(line):
    matchDateAlpha = re.search(DATEPATTERNALPHA,line)
    if not matchDateAlpha: date = ""
    else:
        day = matchDateAlpha.group(DATEPATTERNALPHADAY)
        month = MONTHS[matchDateAlpha.group(DATEPATTERNALPHAMONTH)]
        year = matchDateAlpha.group(DATEPATTERNALPHAYEAR)
        date = day+DATESEP+month
        if not year: date += DATESEP+DEFAULTYEAR
        else: date += DATESEP+"20"+year
    return(date)

def processFile(client,counselor,lines,options):
    date = ""
    mailText = ""
    nbrOfProcessed = 0
    receiver = ""
    for i in range(0,len(lines)):
        line = lines[i]
        matchGreet = re.search(GREETPATTERN,line)
        matchDateNum = re.search(DATEPATTERNNUM,line)
        matchDateAlpha = re.search(DATEPATTERNALPHA,line)
        if matchGreet and matchGreet.group(GREETPATTERNGREET) in GREETINGS:
            if "g" in options and (receiver !="" or nbrOfProcessed > 0):
                printMailText(client,counselor,date,mailText,receiver)
                mailText = ""
                receiver = ""
                nbrOfProcessed += 1
            if receiver == "": 
                receiver = matchGreet.group(GREETPATTERNTARGET)
            else: 
                warn("dupicate greeting (missing date?) on line "+str(i+1)+": "+line)
        if matchDateNum or matchDateAlpha:
            if receiver != "" or nbrOfProcessed > 0:
                printMailText(client,counselor,date,mailText,receiver)
                mailText = ""
                receiver = ""
                nbrOfProcessed += 1
            if matchDateNum: date = getDateNum(line)
            else: date = getDateAlpha(line)
        else: mailText += line
    if mailText != "":
        printMailText(client,counselor,date,mailText,receiver)
    return()

def sanityCheck(lines):
    for line in lines:
        if re.search(SUSPECTEDPATTERN,line): warn(line)
    return()

def makeOptionDict(optionList):
    optionDict = {}
    for keyValuePair in optionList:
        optionName = re.sub("^-","",keyValuePair[0])
        optionDict[optionName] = True
    return(optionDict)

def main(argv):
    try: optionList, files = getopt.getopt(argv,"g",[])
    except: error(USAGE)
    optionDict = makeOptionDict(optionList)
    for inFileName in files:
        lines = readTextFile(inFileName)
        client = getClientName(inFileName)
        counselor = getCounselorName(lines)
        processFile(client,counselor,lines,optionDict)
        sanityCheck(lines)
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
