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
movingWeights = {}

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

def eFunction(windowSize,index):
    return(exp(-2.0*pow(windowSize,2.0) * \
               (pow(windowSize,2.0)+pow(index,2.0)) / \
               pow(pow(windowSize,2.0)-pow(index,2.0),2.0)))

def movingWeight(index,windowSize):
    global movingWeights

    if str(index) in movingWeights: return(movingWeights[str(index)])
    elif index <= -windowSize or index >= windowSize: 
        movingWeights[str(index)] = 0.0
        return(movingWeights[str(index)])
    else:
        nominator = eFunction(windowSize,index)
        denominator = 0.0
        for j in range(1-windowSize,windowSize):
            denominator += eFunction(windowSize,j)
        movingWeights[str(index)] = nominator/denominator
        return(movingWeights[str(index)])

def computeAverage(weightList,index,windowSize):
    total = 0
    for contextIndex in range(index-windowSize+1,index+windowSize):
        realContextIndex = getRealContextIndex(contextIndex,len(weightList))
        total += weightList[realContextIndex]*movingWeight(contextIndex-index,windowSize)
    return(total)

def computeAverageWeights(weightList,windowSize):
    averageWeights = []
    for i in range(0,len(weightList)):
        averageWeights.append(computeAverage(weightList,i,windowSize))
    return(averageWeights)

def printResults(averageWeights):
    for average in averageWeights: print(average)

def daap(text,windowSize=WINDOWSIZE):
    global movingWeights

    movingWeights.clear()
    dictionary = readDict(DAAPDICTFILE)
    weightList = getWeightList(text.lower(),dictionary)
    averageWeights = computeAverageWeights(weightList,windowSize)
    return(averageWeights)

def main(argv):
    text = readText()
    averageWeights = daap(text)
    printResults(averageWeights)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
