#!/usr/bin/python3
"""
    tactus2table.py: convert xml files from tactus to csv tables
    usage: tactus2table.py file1 [file2 ...]
    note: writes output to ../output/emails.csv
    20180412 erikt(at)xs4all.nl
"""

import csv
import gzip
import nltk
import operator
import re
import sys
import xml.etree.ElementTree as ET
from operator import itemgetter

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" file1 [file2 ...]"
INTAKEQUESTIONNAIRE = "./Intake/Questionnaire"
QUESTIONNAIRE = "./Treatment/TreatmentSteps/TreatmentStep/Questionnaire"
QUESTIONNAIRETITLES = { "Intake":True,"Lijst tussenmeting":True,"Lijst nameting":True,"Lijst 3 maanden":True,"Lijst half jaar":True }
QUESTIONS = "./Content/question"
ANSWERS = "./answer"
MESSAGES = "./Messages/Message"
AGE = "leeftijd"
CLIENT = "CLIENT"
COUNSELOR = "COUNSELOR"
SENDER = "Sender"
RECIPIENT = "Recipients"
QUESTION = "question"
DATE = "DateSent"
BODY = "Body"
SUBJECT = "Subject"
MAILFROMID = 1
MAILDATEID = 3
MAILBODYID = 5
OUTPUTDIR = "/home/erikt/projects/e-mental-health/usb/output"
EMAILFILE = OUTPUTDIR+"/emails.csv"
EMAILHEADING = ["id","sender","receipient","date","subject","text"]
EMPTYTOKEN = "EMPTY"
MULTIWORDTOKEN = "MULTIWORD"
MINVALUE = 5
REMOVEDTOKEN = "REMOVED"
SEPARATOR= "-"
SECRETARY = "ttvsecr"
UNDERSCORE = "_"
DEBUGOPT = "-d"
NEWCOUNSELORFREQ = 5

def cleanupText(text):
    text = re.sub(r"\s+"," ",text)
    text = re.sub(r"^ ","",text)
    text = re.sub(r" $","",text)
    return(text)

def makeId(fileName):
    thisId = re.sub(r".*/","",fileName)
    thisId = re.sub(r"\.xml.*$","",thisId)
    return(thisId)

def anonymizeCounselor(name):
    if name != CLIENT: return(COUNSELOR)
    else: return(name)

def getEmailData(root,thisId):
    clientMails = []
    counselorMails = []
    for message in root.findall(MESSAGES):
        body = ""
        date = ""
        recipient = ""
        sender = ""
        subject = ""
        for child in message:
            if child.tag == SENDER: 
                sender = cleanupText(child.text)
            elif child.tag == RECIPIENT: 
                recipient = cleanupText(child.text)
            elif child.tag == DATE: date = cleanupText(child.text)
            elif child.tag == SUBJECT: subject = cleanupText(child.text)
            elif child.tag == BODY: body = cleanupText(child.text)
        if sender == CLIENT: clientMails.append([thisId,sender,recipient,date,subject,body])
        else: counselorMails.append([thisId,sender,recipient,date,subject,body])
    clientMails = cleanupMails(clientMails,counselorMails)
    counselorMails = cleanupMails(counselorMails,clientMails)
    allMails = clientMails
    allMails.extend(counselorMails)
    return(sorted(allMails,key=lambda subList:subList[MAILDATEID]))

def cleanupMails(clientMails, counselorMails):
    for i in range(0,len(clientMails)):
        date = clientMails[i][MAILDATEID]
        body = clientMails[i][MAILBODYID]
    for i in range(0,len(counselorMails)):
        date = counselorMails[i][MAILDATEID]
        body = counselorMails[i][MAILBODYID]
    for i in range(0,len(clientMails)):
        date = clientMails[i][MAILDATEID]
        body = clientMails[i][MAILBODYID]
    return(clientMails)

def readRootFromFile(inFileName):
    if re.search(r"\.gz$",inFileName):
        inFile = gzip.open(inFileName,"rb")
        inFileContent = inFile.read()
        inFile.close()
        return(ET.fromstring(inFileContent))
    else: 
        tree = ET.parse(inFileName)
        root = tree.getroot()
        return(root)

def getSendersByDate(emails):
    mailSenders = {}
    for i in range(0,len(emails)):
        mailSenders[emails[i][MAILDATEID]] = emails[i][MAILFROMID]
    return(mailSenders)

def removeClients(mailSenders):
    for date in [date for date in mailSenders.keys() if mailSenders[date] == CLIENT]:
        del(mailSenders[date])
    return(mailSenders)

def removeCoordinators(mailSenders):
    for date in [date for date in mailSenders.keys() if mailSenders[date] == SECRETARY or re.search(UNDERSCORE,mailSenders[date])]:
        del(mailSenders[date])
    return(mailSenders)

def getValueCounts(mailSendersList):
    valueCounts = {}
    for i in range(0,len(mailSendersList)):
        if mailSendersList[i] in valueCounts: valueCounts[mailSendersList[i]] += 1
        else: valueCounts[mailSendersList[i]] = 1
    return(valueCounts)

def checkFirstLastN(mailSendersList,name,N):
    if N > 0:
        for i in range(0,N):
            if mailSendersList[i] == name: return(True)
        return(False)
    elif N < 0:
        for i in range(-1,N-1,-1):
            if mailSendersList[i] == name: return(True)
        return(False)
    else: return(True)

def countCounselors(emails,debug=False):
    mailSenders = getSendersByDate(emails)
    mailSenders = removeClients(mailSenders)
    mailSenders = removeCoordinators(mailSenders)
    mailSendersList = [mailSenders[date] for date in sorted(mailSenders.keys())] 
    if len(mailSendersList) == 0: return(0)
    valueCounts = getValueCounts(mailSendersList)
    maxValueCountId = [x for x in valueCounts if valueCounts[x] == max(valueCounts.values())][0]
    if debug: print(maxValueCountId,mailSendersList)
    if checkFirstLastN(mailSendersList,maxValueCountId,NEWCOUNSELORFREQ) and \
       checkFirstLastN(mailSendersList,maxValueCountId,-NEWCOUNSELORFREQ):
        return(1)
    else: return(2)

def main(argv):
    debug = False
    if len(argv) > 0 and argv[0] == DEBUGOPT:
        debug = True
        argv.pop(0)
    for inFileName in argv:
        emails = []
        root = readRootFromFile(inFileName)
        thisId = makeId(inFileName)
        emails.extend(getEmailData(root,thisId))
        print(thisId,countCounselors(emails,debug=debug))
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
