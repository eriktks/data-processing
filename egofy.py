#!/usr/bin/env python3
"""
    egofy.py: change Dutch biographic text to autobiographic text
    usage: egofy.py [-t file.txt ] [-p file.txt.pos] [-n name] [-s]
    notes: 
    * requires frog running and listening on localhost port 8080 (for -t)
    * frog requires tokenization, multiword units, pos and ner; skip lac
    * option -s saves linguistic analysis
    * option -n can be repeated several times
    20190111 erikt(at)xs4all.nl
"""

from pynlpl.clients.frogclient import FrogClient
import getopt
import re
import sys

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" [-t file.txt] [-p file.txt.pos] [-n name] [-s]"
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
COMPLETE = "COMPLETE"
PARTIAL = "PARTIAL"

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

def matchTokenToNames(paragraph,start,names):
    if not paragraph[start][TOKEN] in names: return(paragraph[start][TOKEN],start,start)
    end = start
    token = paragraph[start][TOKEN]
    while end+1 < len(paragraph) and token+" "+paragraph[end+1][TOKEN] in names:
        end += 1
        token += " "+paragraph[end][TOKEN]
    while token !="" and names[token] != COMPLETE:
        token = re.sub("\s*\S*","",token)
        end -= 1
    if token == "": return(paragraph[start][TOKEN],start,start)
    else: return(token,start,end)

def egofy(processedText,names,gender):
    text = ""
    textInitial = True
    for paragraph in processedText:
        sentenceInitial = True
        lastPOS = ""
        i = 0
        if textInitial: 
            for token in paragraph: 
                print(token[TOKEN],end=" ")
            print()
        else:
            while i < len(paragraph):
                if paragraph[i][TOKEN] == None:
                    if not sentenceInitial:
                        text += "\n"
                        sentenceInitial = True
                        lastPOS = ""
                else:
                    token,start,end = matchTokenToNames(paragraph,i,names)
                    token = re.sub(r"_"," ",paragraph[i][TOKEN])
                    if token in names and names[token] == COMPLETE:
                        if re.search(r"VZ",lastPOS): 
                            text += METOKEN[sentenceInitial]+" "
                        else: 
                            text += ITOKEN[sentenceInitial]+" "
                        for j in range(start+1,end+1): paragraph.pop(start+1)
                    elif not paragraph[i][NE] == "O" and \
                         (nameMatch([token],names,"s") or \
                          nameMatch([token],names,"'s")):
                        text += POSSESSIVE[sentenceInitial]+" "
                    elif re.search(r"^VNW",paragraph[i][POS]) and \
                         re.search(r"pers",paragraph[i][POS]) and \
                         (re.search(r"nomin",paragraph[i][POS]) or \
                          re.search(r"stan",paragraph[i][POS])) and \
                         re.search(gender,paragraph[i][POS]):
                        text += ITOKEN[sentenceInitial]+" "
                    elif re.search(r"^VNW",paragraph[i][POS]) and \
                         re.search(r"pers",paragraph[i][POS]) and \
                         re.search(r"mv",paragraph[i][POS]):
                        text += WETOKEN[sentenceInitial]+" "
                    elif re.search(r"^VNW",paragraph[i][POS]) and \
                         re.search(r"pers",paragraph[i][POS]) and \
                         re.search(r"obl",paragraph[i][POS]) and \
                         re.search(gender,paragraph[i][POS]):
                        text += METOKEN[sentenceInitial]+" "
                    elif re.search(r"^VNW",paragraph[i][POS]) and \
                         re.search(r"refl",paragraph[i][POS]) and \
                         re.search(r"ndr",paragraph[i][POS]):
                        text += REFLEXIVE[sentenceInitial]+" "
                    elif re.search(r"^VNW",paragraph[i][POS]) and \
                         re.search(r"bez",paragraph[i][POS]) and \
                         token.lower() in POSSESSIVETOKENS[gender]:
                        text += POSSESSIVE[sentenceInitial]+" "
                    elif re.search(r"^VNW",paragraph[i][POS]) and \
                         re.search(r"bez",paragraph[i][POS]) and \
                         re.search(r"mv",paragraph[i][POS]) and \
                         re.search(r"3",paragraph[i][POS]):
                        text += OURTOKEN[sentenceInitial]+" "
                    else:
                        text += token+" "
                    lastPOS = paragraph[i][POS]
                    sentenceInitial = False
                i += 1
            text += "\n"
        textInitial = False
    return(text)

def readFile(inFileName):
    text = ""
    try:
        inFile = open(inFileName,"r")
        for line in inFile: text += line
        inFile.close()
    except Exception as e: sys.exit(COMMAND+": "+str(e))
    return(text)

def extendNameDict(names,name):
    names[name] = COMPLETE
    while True:
        name = re.sub(r"\s*\S*$",r"",name)
        if name == "": break
        if not name in names: names[name] = PARTIAL
    return(names)

def processOptions(argv):
    try:
        names = {}
        optionList, files = getopt.getopt(argv,"n:p:t:s",[])
        options = {}
        for option, arg in optionList:
            if option == "-n": names = extendNameDict(names,arg)
            elif option == "-t" or option == "-p": options[option] = arg
            elif option == "-s": options[option] = True
            else: sys.exit(USAGE)
        return(options,files,names)
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
    options,files,names = processOptions(argv)
    if "-p" in options: processedText = readPosFile(options["-p"])
    elif "-t" in options: processedText = processTextWithFrog(options["-t"])
    else: sys.exit(USAGE)
    if "-s" in options and "-t" in options: savePosFile(processedText,options["-t"])
    if len(processedText) > 0:
        gender = guessGender(processedText)
        if len(names) == 0: names = [guessName(processedText)]
        text = egofy(processedText,names,gender)
        print(text)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
