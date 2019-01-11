#!/usr/bin/env python3
"""
    egofy.py: change Dutch biographic text to autobiographic text
    usage: egofy.py < file.txt
    notes: 
    * requires frog running and listening on localhost port 8080
    * frog requires tokenization multi word units, pos and ner; skip lac
    20190111 erikt(at)xs4all.nl
"""

from pynlpl.clients.frogclient import FrogClient
import re
import sys

COMMAND = sys.argv.pop(0)
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
    try: frogClient = FrogClient(HOST,PORT,returnall=True)
    except Exception as e: error(NOFROGCONTACTMSG+" "+str(e))
    return(frogClient)

def processLineWithFrog(frogClient,text):
    try: frogOutput = frogClient.process(text)
    except Exception as e: error(NOFROGOUTPUTMSG+" "+str(e))
    return(frogOutput)

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

def nameMatch(targetName,sourceName,suffix=""):
    targetName = targetName.lower()
    sourceName = sourceName.lower()
    if targetName+suffix == sourceName or \
       targetName == sourceName+suffix: return(True)
    if nameCheckForSingleWord(targetName,sourceName,suffix): return(True)
    if nameCheckForSingleWord(sourceName,targetName,suffix): return(True)
    if nameCheckForMinusOneToken(targetName,sourceName,suffix): return(True)
    if nameCheckForMinusOneToken(sourceName,targetName,suffix): return(True)
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
                   nameMatch(token,name):
                       if re.search(r"VZ",lastPOS): 
                           text += METOKEN[sentenceInitial]+" "
                       else: 
                           text += ITOKEN[sentenceInitial]+" "
                elif not tokenData[NE] == "O" and \
                     (nameMatch(token,name,"s") or \
                      nameMatch(token,name,"'s")):
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

def main(argv):
    processedText = processStdinWithFrog()
    gender = guessGender(processedText)
    name = guessName(processedText)
    text = egofy(processedText,name,gender)
    print(text)
    #for paragraph in processedText:
    #    for tokenData in paragraph:
    #        print(tokenData[TOKEN],tokenData[POS],tokenData[NE])

if __name__ == "__main__":
    sys.exit(main(sys.argv))
