#!/usr/bin/env python3
"""
    egofy.py: change Dutch biographic text to autobiographic text
    usage: egofy.py [-t file.txt ] [-p file.txt.pos] [-s]
    notes: 
    * requires frog running and listening on localhost port 8080 (for -t)
    * frog requires tokenization, multiword units, pos and ner; skip lac
    * option -s saves linguistic analysis
    20190111 erikt(at)xs4all.nl
"""

from pynlpl.clients.frogclient import FrogClient
import getopt
import re
import sys

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" [-t file.txt] [-p file.txt.pos] [-s]"
HOST = "localhost"
FEMALE = "fem"
MALE = "masc"
PORT = 8080
NE = 4
POS = 3
TOKEN = 0
ITOKEN = { False:"ik", True:"Ik" }
METOKEN = { False:"mij", True:"Mij" }
WETOKEN = { False:"we", True:"We" }
OURTOKEN = { False:"onze", True:"Onze" }
POSSESSIVE = { False:"mijn", True:"Mijn" }
REFLEXIVE = { False:"mijzelf", True:"Mijzelf" }
POSSESSIVETOKENS = { MALE:["zijn"], FEMALE:["haar"] }
ICAPSTOKEN = "Ik"
NOFROGCONTACTMSG = "no Frog found on port "+str(PORT)+"! is it running?"
NOFROGOUTPUTMSG = "no data received from Frog! is it running?"
UNKNOWN = "UNKNOWN"
INFILENAME = "input.txt"

def error(string):
    sys.exit(COMMAND+": error: "+string)

def connectToFrog():
    try:
        frogClient = FrogClient(HOST,PORT,returnall=True)
        return(frogClient)
    except Exception as e: error(NOFROGCONTACTMSG+" "+str(e))

def processLineWithFrog(frogClient,text):
    try:
        frogOutput = frogClient.process(text)
        return(frogOutput)
    except Exception as e: error(NOFROGOUTPUTMSG+" "+str(e))

def processTextWithFrog(text):
    frogClient = connectToFrog()
    processedText = []
    for line in text.split("\n"):
        frogOutput = processLineWithFrog(frogClient,line)
        processedText.append(frogOutput)
    return(processedText)

def processStdinWithFrog():
    frogClient = connectToFrog()
    processedText = []
    for line in sys.stdin:
        frogOutput = processLineWithFrog(frogClient,line)
        processedText.append(frogOutput)
    return(processedText)

def processTextWithFrog(inFileName):
    frogClient = connectToFrog()
    processedText = []
    try: inFile = open(inFileName,"r")
    except Exception as e: sys.exit(COMMAND+": cannot read file "+inFileName)
    for line in inFile:
        frogOutput = processLineWithFrog(frogClient,line)
        processedText.append(frogOutput)
    inFile.close()
    return(processedText)

def getGenderDataFromVNW(processedText):
    genderData = {}
    for paragraph in processedText:
        for tokenData in paragraph:
            if re.match(r"^VNW\(",str(tokenData[POS])):
                argument = re.sub("^.*,","",str(tokenData[POS]))
                argument = re.sub("\)$","",argument)
                if not argument in genderData: genderData[argument] = 1
                else: genderData[argument] += 1
    return(genderData)

def guessGender(processedText):
    gender = MALE
    genderData = getGenderDataFromVNW(processedText)
    for key in sorted(genderData,key=genderData.__getitem__,reverse=True):
        if key == MALE or key == FEMALE:
            gender = key
            break
    return(gender)

def guessName(processedText):
    if len(processedText) <= 0 or len(processedText[0]) <= 0: return("")
    else: 
        name = processedText[0][0][0]
        name = re.sub(r"_"," ",name)
        return(name)

def nameCheckForSingleWord(targetName,sourceName,suffix):
    targetNameTokens = targetName.split()
    for nameToken in targetNameTokens:
        if nameToken+suffix == sourceName or \
           nameToken == sourceName+suffix: return(True)
    return(False)

def nameCheckForMinusOneToken(targetName,sourceName,suffix):
    targetNameTokens = targetName.split()
    for i in range(0,len(targetNameTokens)):
        name = ""
        for j in range(0,len(targetNameTokens)):
            if j != i:
                if name == "": name = targetNameTokens[j]
                else: name += " "+targetNameTokens[j]
        if name+suffix == sourceName or \
           name == sourceName+suffix: return(True)
    return(False)

def nameMatch(targetNames,sourceNames,suffix=""):
    for targetName in targetNames:
        for sourceName in sourceNames:
            targetName = targetName.lower()
            sourceName = sourceName.lower()
            if targetName+suffix == sourceName or \
               targetName == sourceName+suffix: return(True)
            if nameCheckForSingleWord(targetName,sourceName,suffix):
                return(True)
            if nameCheckForSingleWord(sourceName,targetName,suffix): 
                return(True)
            if nameCheckForMinusOneToken(targetName,sourceName,suffix): 
                return(True)
            if nameCheckForMinusOneToken(sourceName,targetName,suffix): 
                return(True)
    return(False)

def egofy(processedText,name,gender):
    text = ""
    textInitial = True
    for paragraph in processedText:
        sentenceInitial = True
        lastPOS = ""
        for tokenData in paragraph:
            if tokenData[TOKEN] == None:
                if not sentenceInitial:
                    text += "\n"
                    sentenceInitial = True
                    lastPOS = ""
            else:
                token = re.sub(r"_"," ",tokenData[TOKEN])
                if not textInitial and \
                   re.search(r"-PER",tokenData[NE]) and \
                   not re.search(r"^VZ[^_]*$",tokenData[POS]) and \
                   nameMatch([token],[name]):
                       if re.search(r"VZ",lastPOS): 
                           text += METOKEN[sentenceInitial]+" "
                       else: 
                           text += ITOKEN[sentenceInitial]+" "
                elif not tokenData[NE] == "O" and \
                     (nameMatch([token],[name],"s") or \
                      nameMatch([token],[name],"'s")):
                    text += POSSESSIVE[sentenceInitial]+" "
                elif re.search(r"^VNW",tokenData[POS]) and \
                     re.search(r"pers",tokenData[POS]) and \
                     (re.search(r"nomin",tokenData[POS]) or \
                      re.search(r"stan",tokenData[POS])) and \
                     re.search(gender,tokenData[POS]):
                    text += ITOKEN[sentenceInitial]+" "
                elif re.search(r"^VNW",tokenData[POS]) and \
                     re.search(r"pers",tokenData[POS]) and \
                     re.search(r"mv",tokenData[POS]):
                    text += WETOKEN[sentenceInitial]+" "
                elif re.search(r"^VNW",tokenData[POS]) and \
                     re.search(r"pers",tokenData[POS]) and \
                     re.search(r"obl",tokenData[POS]) and \
                     re.search(gender,tokenData[POS]):
                    text += METOKEN[sentenceInitial]+" "
                elif re.search(r"^VNW",tokenData[POS]) and \
                     re.search(r"refl",tokenData[POS]) and \
                     re.search(r"ndr",tokenData[POS]):
                    text += REFLEXIVE[sentenceInitial]+" "
                elif re.search(r"^VNW",tokenData[POS]) and \
                     re.search(r"bez",tokenData[POS]) and \
                     token.lower() in POSSESSIVETOKENS[gender]:
                    text += POSSESSIVE[sentenceInitial]+" "
                elif re.search(r"^VNW",tokenData[POS]) and \
                     re.search(r"bez",tokenData[POS]) and \
                     re.search(r"mv",tokenData[POS]) and \
                     re.search(r"3",tokenData[POS]):
                    text += OURTOKEN[sentenceInitial]+" "
                else:
                    text += token+" "
                lastPOS = tokenData[POS]
                sentenceInitial = False
            textInitial = False
        text += "\n"
    return(text)

def readFile(inFileName):
    text = ""
    try:
        inFile = open(inFileName,"r")
        for line in inFile: text += line
        inFile.close()
    except Exception as e: sys.exit(COMMAND+": "+str(e))
    return(text)

def processOptions(argv):
    try:
        optionList, files = getopt.getopt(argv,"p:t:s",[])
        options = {}
        for option, arg in optionList:
            if option == "-t" or option == "-p": options[option] = arg
            elif option == "-s": options[option] = True
            else: sys.exit(USAGE)
        return(options)
    except Exception as e: error(USAGE+" "+str(e))

def convertNones(valueList):
    for i in range(0,len(valueList)):
        if valueList[i] != "None": return(valueList)
    for i in range(0,len(valueList)):
        valueList[i] = None
    return(valueList)

def readPosFile(inFileName):
    try: inFile = open(inFileName,"r")
    except Exception as e: sys.exit(COMMAND+": cannot read from file "+inFileName)
    paragraph,processedText = [],[]
    for line in inFile:
        line = line.strip()
        if line !="": paragraph.append(convertNones(line.split("\t")))
        else:
            processedText.append(paragraph)
            paragraph = []
    if len(paragraph) > 0: processedText.append(paragraph)
    return(processedText)

def savePosFile(processedOptions,outFileName):
    outFileName += ".pos"
    try: outFile = open(outFileName,"w")
    except Exception as e: sys.exit(COMMAND+": cannot write file "+outFileName)
    for paragraph in processedOptions:
        if len(paragraph) == 0: print("\n",file=outFile,end="")
        for token in paragraph:
            for i in range(0,len(token)):
                if i > 0: print("\t",file=outFile,end="")
                print(token[i],file=outFile,end="")
            print("\n",file=outFile,end="")
    outFile.close()

def main(argv):
    options = processOptions(argv)
    if "-p" in options: processedText = readPosFile(options["-p"])
    elif "-t" in options: processedText = processTextWithFrog(options["-t"])
    else: sys.exit(USAGE)
    if "-s" in options and "-t" in options: savePosFile(processedText,options["-t"])
    if len(processedText) > 0:
        gender = guessGender(processedText)
        name = guessName(processedText)
        text = egofy(processedText,name,gender)
        print(text)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
