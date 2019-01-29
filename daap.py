#!/usr/bin/env python3
"""
    daap.py: convert tokenized text to sequence of daap average scores
    usage: daap.py [-d dictionary-file] < file.txt
    20190129 erikt(at)xs4all.nl
"""

from math import exp,pow
import sys

COMMAND = sys.argv.pop(0)
DAAPDICTFILE = "/home/erikt/projects/e-mental-health/DAAP09.6/WRAD/WRAD.Wt"
WINDOWSIZE = 100
MOVINGWEIGHTS = {}

def readDict(inFileName):
    try: 
        dictionary = {}
        inFile = open(inFileName,"r")
        for line in inFile:
            line = line.strip()
            token,weight = line.split()
            dictionary[token] = float(weight)
        inFile.close()
        return(dictionary)
    except Exception as e: 
        sys.exit(COMMAND+": error processing file "+inFileName+": "+str(e))

def readText():
    text = ""
    for line in sys.stdin: text += line
    return(text)

def getWeightList(text,dictionary):
    weightList = []
    for token in text.split():
        if token in dictionary: weightList.append(dictionary[token])
        else: weightList.append(0.0)
    return(weightList)

def getRealContextIndex(contextIndex,weightListLen):
    switchCounter = 0
    while contextIndex < 0:
        contextIndex += weightListLen
        switchCounter += 1
    if switchCounter % 2 != 0:
        contextIndex = weightListLen-1-contextIndex
    while contextIndex >= weightListLen:
        contextIndex -= weightListLen
        switchCounter += 1
    if switchCounter % 2 != 0:
        contextIndex = weightListLen-1-contextIndex
    return(contextIndex)

def movingWeight(index):
    global MOVINGWEIGHTS

    if str(index) in MOVINGWEIGHTS: return(MOVINGWEIGHTS[str(index)])
    elif index <= -WINDOWSIZE or index >= WINDOWSIZE: 
        MOVINGWEIGHTS[str(index)] = 0.0
        return(MOVINGWEIGHTS[str(index)])
    else:
        nominator = exp(-2.0*pow(WINDOWSIZE,2.0)*(pow(WINDOWSIZE,2.0)+pow(index,2.0))/pow((pow(WINDOWSIZE,2.0)-pow(index,2.0)),2.0))
        denominator = 0.0
        for j in range(1-WINDOWSIZE,WINDOWSIZE):
            denominator += exp(-2.0*pow(WINDOWSIZE,2.0)*(pow(WINDOWSIZE,2.0)+pow(j,2.0))/pow((pow(WINDOWSIZE,2.0)-pow(j,2.0)),2.0))
        MOVINGWEIGHTS[str(index)] = nominator/denominator
        return(MOVINGWEIGHTS[str(index)])

def computeAverage(weightList,index):
    total = 0
    for contextIndex in range(index-WINDOWSIZE+1,index+WINDOWSIZE):
        realContextIndex = getRealContextIndex(contextIndex,len(weightList))
        total += weightList[realContextIndex]*movingWeight(contextIndex-index)
    return(total/(-1.0*2.0*WINDOWSIZE))

def computeAverageWeights(weightList):
    averageWeights = []
    for i in range(0,len(weightList)):
        averageWeights.append(computeAverage(weightList,i))
    return(averageWeights)

def printResults(averageWeights):
    for average in averageWeights: print(average)

def main(argv):
    dictionary = readDict(DAAPDICTFILE)
    text = readText()
    weightList = getWeightList(text,dictionary)
    averageWeights = computeAverageWeights(weightList)
    printResults(averageWeights)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
