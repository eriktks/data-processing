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
COUNSELOR = "COUNSELOR"
DATE = "DATE"
INDEX = "INDEX"
NBROFSENTS = "NBROFSENTS"
NBROFTOKENS = "NBROFTOKENS"
SENDER = "Sender"
MAILID = "mailId"
DAAP = "daap"
DIARY = "DIARY"
LINEWIDTH = 0.2
LINEMAX = 0.05

clientDatesList = []

def removeMetaData(row):
    if DATE in row: del(row[DATE])
    if NBROFSENTS in row: del(row[NBROFSENTS])
    if SENDER in row: del(row[SENDER])
    return(row)

def readData(inFileName,diaries=True):
    inFile = open(inFileName,"r")
    data = []
    csvReader = csv.DictReader(inFile,delimiter=",")
    for row in csvReader:
        if diaries or (SENDER in row and row[SENDER] != DIARY):
            data.append(row)
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
from datetime import datetime

PLOTWIDTH = 15
PLOTHEIGHT = 4
BARWIDTH = 1.0
IMAGEFILE = "tactus.png"
DATEFORMAT = "%Y-%m-%dT%H:%M:%S"

def makeBottomValues(fieldDataList,index,format):
    bottomValues = []
    for i in range(0,len(fieldDataList)):
        for j in range(0,len(fieldDataList[i])):
            while len(bottomValues) < j+1: bottomValues.append(0)
            if i < index: 
                if format != "": bottomValues[j] += max(fieldDataList[i])
                else: bottomValues[j] += fieldDataList[i][j]
    return(bottomValues)

def eraseOtherSenders(fieldDataList,senders,target):
    outList = []
    nbrOfMails = 0
    for i in range(0,len(fieldDataList)):
        outSubList = []
        for j in range(0,len(fieldDataList[i])):
            try:
                if senders[j] != target:
                    outSubList.append(0.0)
                else:
                    outSubList.append(fieldDataList[i][j])
                    if i == 0: nbrOfMails += 1
            except Exception as e:
                sys.exit("Error processing filedDataList: "+str(e))
        outList.append(outSubList)
    return(outList,nbrOfMails)

def addZeroListForHeight(fieldDataList):
    if len(fieldDataList) > 0:
        zeroList = []
        for i in range(0,len(fieldDataList[0])): zeroList.append(0.0)
        fieldDataList.append(zeroList)
    return(fieldDataList)

def pluralTest(number):
    if number != 1: return("s")
    else: return("")

def unique(thisList):
    return(list(set(thisList)))

def makePlotIndexPart(fieldDataList,fieldNames,format,senders,target):
    plt.figure(figsize=(PLOTWIDTH,PLOTHEIGHT))
    xvalues = range(0,len(fieldDataList[0]))
    barplots = []
    targetFieldDataList,nbrOfMails = eraseOtherSenders(fieldDataList,senders,target)
    targetFieldDataList = addZeroListForHeight(targetFieldDataList)
    for i in range(0,len(fieldDataList)):
        bottomValues = makeBottomValues(targetFieldDataList,i,format)
        barplot = plt.bar(xvalues,targetFieldDataList[i],width=BARWIDTH,bottom=bottomValues)
        barplots.append(barplot)
    plt.legend(tuple([b[0] for b in barplots]),tuple(fieldNames))
    plt.xticks(xvalues,[x+1 for x in xvalues])
    plt.title(target+" ("+str(nbrOfMails)+" message"+pluralTest(nbrOfMails)+")",fontdict={"fontweight":"bold"})
    plt.savefig(IMAGEFILE)
    plt.show()

def makePlotIndex(fieldDataList,fieldNames,format,senders):
    for sender in sorted(unique(senders)):
        makePlotIndexPart(fieldDataList,fieldNames,format,senders,sender)
    
def visualizeIndex(file,features,format=""):
    data = readData(file)
    if len(data) == 0: sys.exit("no data found!")
    featureDataList = selectData(data,features)
    senders = [d[SENDER] for d in data]
    makePlotIndex(featureDataList,features,format,senders)

def makePlotDatesPart(fieldDataList,fieldNames,format,barwidth,dates,senders,target):
    plt.figure(figsize=(PLOTWIDTH,PLOTHEIGHT))
    ax = plt.subplot(111)
    ax.xaxis_date()
    xvalues = dates
    barplots = []
    targetFieldDataList,nbrOfMails = eraseOtherSenders(fieldDataList,senders,target)
    targetFieldDataList = addZeroListForHeight(targetFieldDataList)
    for i in range(0,len(targetFieldDataList)):
        bottomValues = makeBottomValues(fieldDataList,i,format)
        barplot = \
            plt.bar(xvalues,targetFieldDataList[i],width=barwidth,bottom=bottomValues)
        barplots.append(barplot)
    plt.legend(tuple([b[0] for b in barplots]),tuple(fieldNames))
    plt.title(target+" ("+str(nbrOfMails)+" message"+pluralTest(nbrOfMails)+")",fontdict={"fontweight":"bold"})
    plt.xticks(rotation=0)
    plt.savefig(IMAGEFILE)
    plt.show()
    
def makePlotDates(fieldDataList,fieldNames,format,barwidth,dates,senders):
    for sender in sorted(unique(senders)):
        makePlotDatesPart(fieldDataList,fieldNames,format,barwidth,dates,senders,sender)

def visualize(file,features,format="",barwidth=BARWIDTH,target=CLIENT,diaries=True):
    data = readData(file,diaries)
    if len(data) == 0: sys.exit("no data found!")
    dates = [datetime.strptime(d["DATE"],DATEFORMAT) for d in data]
    senders = [d[SENDER] for d in data]
    featureDataList = selectData(data,features)
    makePlotDates(featureDataList,features,format,barwidth,dates,senders)

def convertToAverages(valuesIn,equalwidth=False):
    startI = 0
    startId = int(valuesIn[0][MAILID])
    totalDAAP = 0.0
    valuesOut = []
    for i in range(0,len(valuesIn)):
        if int(valuesIn[i][MAILID]) == startId: 
            totalDAAP += float(valuesIn[i][DAAP])
        else:
            if equalwidth:
                valuesOut.append(valuesIn[i])
                valuesOut[-1][DAAP] = totalDAAP/(i-startI)
            else:
                for j in range(startI,i):
                    valuesOut.append(valuesIn[j])
                    valuesOut[-1][DAAP] = totalDAAP/(i-startI)
            startI = i
            startId = int(valuesIn[i][MAILID])
            totalDAAP = float(valuesIn[i][DAAP])
    if equalwidth:
        valuesOut.append(valuesIn[i])
        valuesOut[-1][DAAP] = totalDAAP/(i-startI)
    else:
        for j in range(startI,len(valuesIn)): 
            valuesOut.append(valuesIn[j])
            valuesOut[-1][DAAP] = totalDAAP/(len(valuesIn)-startI)
    return(valuesOut)

def makePlotDAAP(fileName,data,index=-1,user="",average=False,linemax=LINEMAX,equalwidth=False):
    plt.figure(figsize=(PLOTWIDTH,PLOTHEIGHT))
    if user == "CLIENT" or user == "COUNSELOR": 
        values = [ x for x in data if x[SENDER] == user ]
    else: 
        values = [ x for x in data if x[MAILID] == index ]
    if equalwidth: token = "mail"
    else: token = "token"
    if len(values) > 0:
        if average: 
            values = convertToAverages(values,equalwidth=equalwidth)
        nbrOfTokens = len(values)
        target = values[0][SENDER]
        if int(index) >= 0: 
            mailId = values[0][MAILID]
            date = values[0][DATE]
            print("Date mail "+str(int(mailId)+1)+" is "+date)
            plt.title("File: "+fileName+"; Mail "+str(int(mailId)+1)+" ("+date+"); Sender: "+target+"; "+str(nbrOfTokens)+" "+token+pluralTest(nbrOfTokens),fontdict={"fontweight":"bold"})
        else:
            plt.title("File: "+fileName+"; Sender: "+target+"; "+str(nbrOfTokens)+" "+token+pluralTest(nbrOfTokens),fontdict={"fontweight":"bold"})
        plt.plot(range(0,len(values)),[float(x[DAAP]) for x in values])
        lastMailId = values[0][MAILID]
        counter = 0
        if equalwidth: plt.plot([0.5,0.5],[-linemax,linemax],color="black",linewidth=LINEWIDTH)
        for i in range(1,len(values)):
            if values[i][MAILID] != lastMailId:
                counter += 1
                if not equalwidth:
                    plt.plot([i,i],[-linemax,linemax],color="black",linewidth=LINEWIDTH)
                else:
                    x = float(counter)+0.5
                    plt.plot([x,x],[-linemax,linemax],color="black",linewidth=LINEWIDTH)
                lastMailId = values[i][MAILID]
    else:
        plt.title("Empty data set")
    plt.savefig(IMAGEFILE)
    plt.show()
 
def makeTableDAAP(fileName,data,index=-1,user="",average=False):
    if user == "CLIENT" or user == "COUNSELOR": 
        values = [ x for x in data if x[SENDER] == user ]
    else: 
        values = [ x for x in data if x[MAILID] == index ]
    token = "token"
    if len(values) > 0:
        if average: 
            values = convertToAverages(values)
        maximum = max([float(x[DAAP]) for x in values])
        nbrOfTokens = len(values)
        target = values[0][SENDER]
        if int(index) >= 0: 
            mailId = values[0][MAILID]
            date = values[0][DATE]
            print("File: "+fileName+"; Mail "+str(int(mailId)+1)+" ("+date+"); Sender: "+target+"; "+str(nbrOfTokens)+" "+token+pluralTest(nbrOfTokens))
        else:
            print("File: "+fileName+"; Sender: "+target+"; "+str(nbrOfTokens)+" "+token+pluralTest(nbrOfTokens))
        if not average:
            print("mail token   score sender")
            for i in range(0,len(values)):
                if float(values[i][DAAP]) >= maximum: maxString = "maximum"
                else: maxString = ""
                print("{0:4d} {1:5d} {2:7.4f} {3:9s} {4:7s}".format(1+int(values[i][MAILID]),1+i,float(values[i][DAAP]),values[i][SENDER],maxString))
        else:
            print(" mail   score sender")
            for i in range(0,len(values)):
                if float(values[i][DAAP]) >= maximum: maxString = "maximum"
                else: maxString = ""
                if i == 0 or values[i][MAILID] != values[i-1][MAILID]:
                    print("{0:4d} {1:7.4f} {2:9s} {3:7s}".format(1+int(values[i][MAILID]),float(values[i][DAAP]),values[i][SENDER],maxString))
    else:
        print("Empty data set")
 
def visualizeDAAP(file,user="",mail=-1,average=False,linemax=LINEMAX,equalwidth=False,table=False):
    data = readData(file)
    if len(data) == 0: sys.exit("no data found!")
    if table:
        if user == CLIENT or user == COUNSELOR:
            makeTableDAAP(file,data,user=user,average=average)
        elif mail >= 1:
            makeTableDAAP(file,data,index=str(mail-1))
        else:
            seen = {}
            for dataItem in data:
                index = dataItem[MAILID]
                if not index in seen:
                    makeTableDAAP(file,data,index=index,average=average)
                    seen[index] = True
    else:
        if user == CLIENT:
            makePlotDAAP(file,data,user=CLIENT,average=average,linemax=linemax,equalwidth=equalwidth)
            makePlotDAAP(file,data,user=COUNSELOR,average=average,linemax=linemax,equalwidth=equalwidth)
        elif user == COUNSELOR:
            makePlotDAAP(file,data,user=CLIENT,average=average,linemax=linemax,equalwidth=equalwidth)
            makePlotDAAP(file,data,user=COUNSELOR,average=average,linemax=linemax,equalwidth=equalwidth)
        elif mail >= 1:
            makePlotDAAP(file,data,index=str(mail-1))
        else:
            seen = {}
            for dataItem in data:
                index = dataItem[MAILID]
                if not index in seen:
                    makePlotDAAP(file,data,index=index,average=average,linemax=linemax)
                    seen[index] = True

def makePlotDAAPboth(fileName,data,bar=False):
    plt.figure(figsize=(PLOTWIDTH,PLOTHEIGHT))
    values = convertToAverages(data,equalwidth=True)
    for i in range(0,len(values)): values[i][INDEX] = i
    nbrOfMails = len(values)
    client = [x for x in values if x[SENDER] == CLIENT ]
    counselor = [x for x in values if x[SENDER] == COUNSELOR ]
    plt.title("File: "+fileName+"; "+str(nbrOfMails)+" mail"+pluralTest(nbrOfMails)+"; Client: "+str(len(client))+"; Counselor: "+str(len(counselor)),fontdict={"fontweight":"bold"})
    if bar:
        minimum = min([float(x[DAAP]) for x in values])
        barCl = plt.bar([x[INDEX] for x in client],[float(x[DAAP])-minimum+abs(0.2*minimum) for x in client],color="red")
        barCo = plt.bar([x[INDEX] for x in counselor],[float(x[DAAP])-minimum+abs(0.2*minimum) for x in counselor],color="blue")
        plt.yticks([])
    else:
        barCl, = plt.plot([x[INDEX] for x in client],[float(x[DAAP]) for x in client],color="red")
        barCo, = plt.plot([x[INDEX] for x in counselor],[float(x[DAAP]) for x in counselor],color="blue")
    plt.legend([barCl,barCo],["Client","Counselor"])
    plt.savefig(IMAGEFILE)
    plt.show()
 
def visualizeDAAPboth(file,bar=False):
    data = readData(file)
    if len(data) == 0: sys.exit("no data found!")
    makePlotDAAPboth(file,data,bar=bar)

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

def summarizeDataFeature(data,featureName,target):
    return({i+1:float(data[i][featureName])/float(data[i][NBROFTOKENS]) \
            for i in range(0,len(data)) if featureName in data[i] and (target == None or data[i][SENDER] == target)})

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

def summarizeData(data,target):
    summary = {}
    for row in data:
        if target == None or row[SENDER] == target:
            for featureName in row:
                if row[featureName].isdigit():
                    if featureName in summary: 
                        summary[featureName] += int(row[featureName])
                    else: 
                        summary[featureName] = int(row[featureName])
                else:
                    if featureName in summary: 
                        summary[featureName] += 1
                    else: 
                        summary[featureName] = 1
    return(summary)

def printSummary(data,summary,type=DATA):
    if NBROFTOKENS in summary: print("tokens:",int(summary[NBROFTOKENS]))
    if NBROFMATCHES in summary: print("number of matches:",summary[NBROFMATCHES])
    for element in sorted(summary.items(), \
                          key=operator.itemgetter(1),reverse=True):
        featureName,frequency = element
        if frequency > 0.0:
            if featureName in (NBROFTOKENS,NBROFSENTS) or \
               (featureName in data[0] and not data[0][featureName].isdigit()): print("      "+featureName)
            elif type != DATA: print("%5.2f%% %s" % (100.0*frequency,featureName))
            else: print("%5d %s (%0.2f%%)" % \
                    (frequency,featureName,
                     100.0*float(frequency)/float(summary[NBROFTOKENS])))
    print("missing:",end="")
    for element in sorted(summary.items()):
        featureName,frequency = element
        if not featureName in (NBROFTOKENS,NBROFMATCHES) and frequency <= 0.0:
            print(" "+featureName,end="")
    print("\n",end="")

def summarizeFeature(file,feature,target=None):
    data = readData(file)
    summary = summarizeDataFeature(data,feature,target)
    printSummary(data,summary,FEATURE)        

def summarizeMail(file,mail):
    data = readData(file)
    summary = summarizeDataMail(data,mail-1,target)
    printSummary(data,summary,MAIL)

def summarize(file,target=None):
    data = readData(file)
    summary = summarizeData(data,target)
    printSummary(data,summary)

