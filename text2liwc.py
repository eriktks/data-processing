#!/usr/bin/env python3
"""
    text2liwc.py: convert lines of untokenized text to vector of liwc features
    usage: text2liwc.py < file
    20181120 erikt(at)xs4all.nl
"""

from pynlpl.clients.frogclient import FrogClient
import re
import sys

COMMAND = sys.argv.pop(0)
LIWCDIR = "/home/erikt/projects/e-mental-health/liwc/"
LIWCFILE = "Dutch_LIWC2015_Dictionary.dic"
TEXTBOUNDARY = "%"
NBROFTOKENS = "NBROFTOKENS"
NBROFSENTS = "NBROFSENTS"
NBROFMATCHES = "NBROFMATCHES"
MAXPREFIXLEN = 10
FROGPORT = 8080
FROGHOST = "localhost"
TOKENID = 0
LEMMAID = 1
NUMBER = "number"
numberId = -1

def processFrogData(tokenInfo):
    tokens = []
    nbrOfSents = 0
    for token in tokenInfo:
        if token[TOKENID] == None: nbrOfSents += 1
        else: tokens.append(token[LEMMAID])
    if len(tokens) > 0: nbrOfSents += 1
    return(tokens,nbrOfSents)

def tokenize(text):
    try: frogclient = FrogClient('localhost',FROGPORT,returnall=True)
    except Exception as e: sys.exit(COMMAND+": cannot run frog: "+str(e))
    tokens,nbrOfSents = processFrogData(frogclient.process(text))
    return(tokens,nbrOfSents)

def isNumber(string):
    return(string.lstrip("-").replace(".","1").isnumeric())

def readEmpty(inFile):
    text = ""
    for line in inFile:
        line = line.strip()
        if line == TEXTBOUNDARY: break
        text += line+"\n"
    if text != "": 
        sys.exit(COMMAND+": liwc dictionary starts with unexpected text: "+text)

def readFeatures(inFile):
    global numberId

    features = {}
    for line in inFile:
        line = line.strip()
        if line == TEXTBOUNDARY: break
        fields = line.split()
        featureId = fields.pop(0)
        featureName = " ".join(fields)
        features[featureId] = featureName
        if featureName == NUMBER: numberId = featureId
    return(features)

def makeUniqueElements(inList):
    outList = []
    seen = {}
    for element in inList:
        if not element in seen:
            outList.append(element)
            seen[element] = True
    return(outList)

def readWords(inFile):
    words = {}
    prefixes = {}
    for line in inFile:
        line = line.strip()
        if line == TEXTBOUNDARY: break
        fields = line.split()
        word = fields.pop(0).lower()
        word = re.sub(r"\*$","",word)
        if re.search(r"-$",word):
            word = re.sub(r"-$","",word)
            if not word in prefixes: prefixes[word] = fields
            else: words[word] = makeUniqueElements(words[word]+fields)
        else:
            if not word in words: words[word] = fields
            else: words[word] = makeUniqueElements(words[word]+fields)
    return(words,prefixes)

def readLiwc(inFileName):
    try: inFile = open(inFileName,"r")
    except Exception as e: 
        sys.exit(COMMAND+": cannot read LIWC dictionary "+inFileName)
    readEmpty(inFile)
    features = readFeatures(inFile)
    words,prefixes = readWords(inFile)
    inFile.close()
    return(features,words,prefixes)

def findLongestPrefix(prefixes,word):
    while not word in prefixes and len(word) > 0:
        chars = list(word)
        chars.pop(-1)
        word = "".join(chars)
    return(word)

def addFeatureToCounts(counts,feature):
    if feature in counts: counts[feature] += 1
    else: counts[feature] = 1

def text2liwc(words,prefixes,tokens):
    global numberId

    counts = {}
    for word in tokens:
        if word in words:
            addFeatureToCounts(counts,NBROFMATCHES)
            for feature in words[word]: 
                addFeatureToCounts(counts,feature)
        longestPrefix = findLongestPrefix(prefixes,word)
        if longestPrefix != "":
            addFeatureToCounts(counts,NBROFMATCHES)
            for feature in prefixes[longestPrefix]:
                addFeatureToCounts(counts,feature)
        if isNumber(word): 
            addFeatureToCounts(counts,NBROFMATCHES)
            addFeatureToCounts(counts,numberId)
    return(counts)

def stdin2liwc(features,words,prefixes):
    text = ""
    for line in sys.stdin: text += line
    tokens,nbrOfSents = tokenize(text)
    liwcResults = text2liwc(words,prefixes,tokens)
    liwcResults[NBROFTOKENS] = len(tokens)
    liwcResults[NBROFSENTS] = nbrOfSents
    return(liwcResults)

def printHeader(features):
    print(NBROFTOKENS,NBROFMATCHES,NBROFSENTS,sep=",",end="")
    for value in features.values():
        print(","+value,end="")
    print()

def printResults(features,results):
    printHeader(features)
    print(results[NBROFTOKENS],results[NBROFMATCHES],results[NBROFSENTS],sep=",",end="")
    for feature in features:
        print(",",end="")
        if feature in results: print(results[feature],end="")
        else: print(0,end="")
    print()
    return()

def main(argv):
    features,words,prefixes = readLiwc(LIWCDIR+LIWCFILE)
    results = stdin2liwc(features,words,prefixes)
    printResults(features,results)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
