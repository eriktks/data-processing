#!/usr/bin/env python3
"""
    tactus-visualize.py: support functions for tactus-visualize.ipynb
    usage: import tactus-visualize
    20190108 erikt(at)xs4all.nl
"""

# The first block of code contains the code of the function that 
# reads the data.

import csv

CLIENT = "CLIENT"
DATE = "DATE"
NBROFSENTS = "NBROFSENTS"
NBROFTOKENS = "NBROFTOKENS"
SENDER = "Sender"

clientDatesList = []

def removeMetaData(row):
    if DATE in row: del(row[DATE])
    if NBROFSENTS in row: del(row[NBROFSENTS])
    if SENDER in row: del(row[SENDER])
    return(row)

def readData(inFileName):
    inFile = open(inFileName,"r")
    data = []
    csvReader = csv.DictReader(inFile,delimiter=",")
    for row in csvReader:
        if (DATE in row and row[DATE] in clientDatesList) or \
           (SENDER in row and row[SENDER] == CLIENT): 
               data.append(removeMetaData(row))
    inFile.close()
    return(data)

# The second code block holds the function that selects the data
# from the fields we want to visualize. Each field data item is a 
# list with numbers: how often each type of word was seen in each 
# of the mails. Since one mail can be longer than another, we will 
# use percentages in the data visualization. Therefore, we divide
# each number by the total number of words of each mail 
# (NBROFTOKENS). 

import sys

NBROFTOKENS = "NBROFTOKENS"

def selectData(data,fieldNameList):
    fieldDataList = []
    for fieldName in fieldNameList:
        if not fieldName in data[0]: sys.exit("unknown field name: "+fieldName)
        fieldData = [float(data[i][fieldName])/float(data[i][NBROFTOKENS]) \
                     for i in range(0,len(data))]
        fieldDataList.append(fieldData)
    return(fieldDataList)

# The data will be visualized as a stacked bar plot by the three 
# functions in the third code block. The y-values shown in the 
# plot are fractions: 0.01 corresponds to 1%. The data 
# visualization is automatically saved in the file tactus.png. 
# You can use this image file for presentations.

import matplotlib.pyplot as plt

PLOTWIDTH = 15
PLOTHEIGHT = 4
BARWIDTH = 1.0
IMAGEFILE = "tactus.png"

def makeBottomValues(fieldDataList,index,format):
    bottomValues = []
    for i in range(0,len(fieldDataList)):
        for j in range(0,len(fieldDataList[i])):
            while len(bottomValues) < j+1: bottomValues.append(0)
            if i < index: 
                if format != "": bottomValues[j] += max(fieldDataList[i])
                else: bottomValues[j] += fieldDataList[i][j]
    return(bottomValues)

def makePlot(fieldDataList,fieldNames,format):
    plt.figure(figsize=(PLOTWIDTH,PLOTHEIGHT))
    xvalues = range(0,len(fieldDataList[0]))
    barplots = []
    for i in range(0,len(fieldDataList)):
        bottomValues = makeBottomValues(fieldDataList,i,format)
        barplot = \
            plt.bar(xvalues,fieldDataList[i],width=BARWIDTH,bottom=bottomValues)
        barplots.append(barplot)
    plt.legend(tuple([b[0] for b in barplots]),tuple(fieldNames))
    plt.xticks(xvalues,[x+1 for x in xvalues])
    plt.savefig(IMAGEFILE)
    plt.show()
    
def visualize(file,features,format=""):
    data = readData(file)
    featureDataList = selectData(data,features)
    makePlot(featureDataList,features,format)

# The function summarize presents a list of feature names together 
# with their frequency. Thus we can observe which feature names are 
# interesting in a certain file. With summarizeMail, we obtain the
# frequencies of the features for a single mail. And 
# summarizeFeature provides the frequencies of a single feature per 
# mail.

import operator

DATA = "DATA"
FEATURE = "FEATURE"
MAIL = "MAIL"
NBROFMATCHES ="NBROFMATCHES"

def summarizeDataFeature(data,featureName):
    return({i+1:float(data[i][featureName])/float(data[i][NBROFTOKENS]) \
            for i in range(0,len(data)) if featureName in data[i]})

def summarizeDataMail(data,mailId):
    summary = {}
    if mailId >= 0 and mailId < len(data):
        row = data[mailId]
        for featureName in row:
            if row[featureName].isdigit():
                if featureName == NBROFTOKENS:
                    summary[featureName] = float(row[featureName])
                elif featureName in summary: 
                    summary[featureName] += \
                        float(row[featureName])/float(row[NBROFTOKENS])
                else: 
                    summary[featureName] = \
                        float(row[featureName])/float(row[NBROFTOKENS])
    return(summary)

def summarizeData(data):
    summary = {}
    for row in data:
        for featureName in row:
            if row[featureName].isdigit() :
                if featureName in summary: 
                    summary[featureName] += int(row[featureName])
                else: 
                    summary[featureName] = int(row[featureName])
    return(summary)

def printSummary(summary,type=DATA):
    if NBROFTOKENS in summary: print("tokens:",int(summary[NBROFTOKENS]))
    if NBROFMATCHES in summary: print("number of matches:",summary[NBROFMATCHES])
    for element in sorted(summary.items(), \
                          key=operator.itemgetter(1),reverse=True):
        featureName,frequency = element
        if not featureName in (NBROFTOKENS,NBROFMATCHES) and frequency > 0.0: 
            if type != DATA: print("%5.2f%% %s" % (100.0*frequency,featureName))
            else: print("%5d %s (%0.2f%%)" % \
                    (frequency,featureName,
                     100.0*float(frequency)/float(summary[NBROFTOKENS])))
    print("missing:",end="")
    for element in sorted(summary.items()):
        featureName,frequency = element
        if not featureName in (NBROFTOKENS,NBROFMATCHES) and frequency <= 0.0:
            print(" "+featureName,end="")
    print("\n",end="")

def summarizeFeature(file,feature):
    data = readData(file)
    summary = summarizeDataFeature(data,feature)
    printSummary(summary,FEATURE)        

def summarizeMail(file,mail):
    data = readData(file)
    summary = summarizeDataMail(data,mail-1)
    printSummary(summary,MAIL)

def summarize(file):
    data = readData(file)
    summary = summarizeData(data)
    printSummary(summary)

