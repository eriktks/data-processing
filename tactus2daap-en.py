#!/usr/bin/python3
"""
    tactus2daap-en.py: convert xml files from tactus to daap scores per mail csv
    usage: tactus2daap-en.py file1.xml [file2.xml ...] > file1.csv
    note: based on tactus2liwc-en.py
    20190204 erikt(at)xs4all.nl
"""

import csv
import nltk
import operator
import re
import sys
import xml.etree.ElementTree as ET

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" file1 [file2 ...]"
INTAKEQUESTIONNAIRE = "./Intake/Questionnaire"
QUESTIONNAIRE = "./Treatment/TreatmentSteps/TreatmentStep/Questionnaire"
QUESTIONNAIRETITLES = { "Intake":True,"Lijst tussenmeting":True,"Lijst nameting":True,"Lijst 3 maanden":True,"Lijst half jaar":True }
ANSWERS = "./Content/question/answer"
MESSAGES = "./Messages/Message"
AGE = "leeftijd"
CLIENT = "CLIENT"
COUNSELOR = "COUNSELOR"
SENDER = "Sender"
RECIPIENT = "Recipients"
QUESTION = "question"
DATESENT = "DateSent"
DATE = "DATE"
BODY = "Body"
ATTACHMENT = "Attachment"
SUBJECT = "Subject"
SENDERID = 1
MAILDATEID = 3
MAILTITLEID = 4
MAILBODYID = 5
OUTPUTDIR = "/home/erikt/projects/e-mental-health/usb/output"
EMAILFILE = OUTPUTDIR+"/emails.csv"
EMAILHEADING = ["id","sender","receipient","date","subject","text"]
DAAPDIR = "/home/erikt/projects/e-mental-health/DAAP09.6/WRAD/"
DAAPFILE = "WRAD.Wt"
TEXTBOUNDARY = "%"
NBROFTOKENS = "NBROFTOKENS"
NBROFSENTS = "NBROFSENTS"
NBROFMATCHES = "NBROFMATCHES"
NUMBER = "number"
METADATAFEATURES = [DATE,NBROFTOKENS,NBROFSENTS,NBROFMATCHES,SENDER]
DAAP = "daap"

numberId = -1
headerPrinted = False

def cleanupText(text):
    if text == None: return("")
    text = re.sub(r"\s+"," ",text)
    text = re.sub(r"^ ","",text)
    text = re.sub(r" $","",text)
    return(text)

def removeSpaces(text):
    text = re.sub(r"\s+","",text)
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
                sender = anonymizeCounselor(cleanupText(child.text))
            elif child.tag == RECIPIENT: 
                recipient = anonymizeCounselor(cleanupText(child.text))
            elif child.tag == DATESENT: date = cleanupText(child.text)
            elif child.tag == SUBJECT: subject = cleanupText(child.text)
            elif child.tag == BODY: body = cleanupText(child.text)
        if sender == CLIENT: clientMails.append([thisId,sender,recipient,date,subject,body])
        else: counselorMails.append([thisId,sender,recipient,date,subject,body])
    clientMails = cleanupMails(clientMails,counselorMails)
    counselorMails = cleanupMails(counselorMails,clientMails)
    allMails = clientMails
    allMails.extend(counselorMails)
    return(sorted(allMails,key=lambda subList:subList[MAILDATEID]))

def sentenceSplit(text):
    tokens = text.split()
    sentence = []
    sentences = []
    for token in tokens:
        sentence.append(token)
        if not re.search(r"[a-zA-Z0-9'\"]",token): 
            sentences.append(" ".join(sentence))
            sentence = []
    if len(sentence) > 0: sentences.append(" ".join(sentence))
    return(sentences)

def cleanupMails(clientMails, counselorMails):
    clientSentenceDates = {}
    counselorSentenceDates = {}
    for i in range(0,len(clientMails)):
        date = clientMails[i][MAILDATEID]
        body = clientMails[i][MAILBODYID]
        sentences = sentenceSplit(body)
        for s in sentences:
            if (s in clientSentenceDates and date < clientSentenceDates[s]) or \
                not s in clientSentenceDates:
                clientSentenceDates[s] = date
    for i in range(0,len(counselorMails)):
        date = counselorMails[i][MAILDATEID]
        body = counselorMails[i][MAILBODYID]
        sentences = sentenceSplit(body)
        for s in sentences:
            if s in clientSentenceDates and date < clientSentenceDates[s]:
                counselorSentenceDates[s] = date
                del(clientSentenceDates[s])
            elif s in counselorSentenceDates and date < counselorSentenceDates[s]:
                counselorSentenceDates[s] = date
            elif not s in clientSentenceDates and not s in counselorSentenceDates:
                counselorSentenceDates[s] = date
    for i in range(0,len(clientMails)):
        date = clientMails[i][MAILDATEID]
        body = clientMails[i][MAILBODYID]
    return(clientMails)

def getQuestionnaires(root,thisId):
    qs = []
    for questionnaires in INTAKEQUESTIONNAIRE,QUESTIONNAIRE:
        for questionnaire in root.findall(questionnaires):
            title = cleanupText(questionnaire.findall("./Title")[0].text)
            if title in QUESTIONNAIRETITLES:
                q = {"title":title,"id":thisId}
                for answer in questionnaire.findall(ANSWERS):
                    try:
                        key = answer.attrib["ID"]
                        value = cleanupText(answer.findall("./answerText")[0].text)
                        q[key] = value
                    except: continue 
                qs.append(q)
    return(qs)

def tokenize(text):
    sentences = nltk.sent_tokenize(text)
    tokens = []
    for s in sentences:
        t = nltk.word_tokenize(s)
        tokens.extend(t)
    return(tokens,len(sentences))

def isNumber(string):
    return(string.lstrip("-").replace(".","1").isnumeric())

def readWords(inFile):
    words = {}
    for line in inFile:
        line = line.strip()
        word,weight = line.split()
        weight = re.sub("r-","0",weight)
        words[word] = float(weight)
    return(words)

def readDaapDict(inFileName):
    try: inFile = open(inFileName,"r")
    except Exception as e: 
        sys.exit(COMMAND+": cannot read DAAP dictionary "+inFileName)
    words = readWords(inFile)
    inFile.close()
    return(words)

def addFeatureToCounts(counts,feature):
    if feature in counts: counts[feature] += 1
    else: counts[feature] = 1

def text2daap(words,tokens):
    global numberId

    counts = { NBROFMATCHES:0 , DAAP:0.0 }
    for token in tokens:
        if token in words:
            addFeatureToCounts(counts,NBROFMATCHES)
            counts[DAAP] += words[token] 
    if counts[NBROFMATCHES] > 0: counts[DAAP] /= counts[NBROFMATCHES]
    return(counts)

def readTextFromStdin():
    text = ""
    for line in sys.stdin: text += line
    return(text)

def printHeader(features):
    for i in range(0,len(METADATAFEATURES)):
        if i != 0: print(",",end="")
        print(METADATAFEATURES[i],end="")
    for value in features:
        print(","+value,end="")
    print()

def printResults(features,results):
    for i in range(0,len(METADATAFEATURES)):
        if i != 0: print(",",end="")
        if METADATAFEATURES[i] in results:
            print(removeSpaces(str(results[METADATAFEATURES[i]])),end="")
    for feature in features:
        print(",",end="")
        if feature in results: print(results[feature],end="")
        else: print(0,end="")
    print()

def emails2daap(emails,features,words):
    global headerPrinted

    if not headerPrinted:
        printHeader(features)
        headerPrinted = True
    for row in emails:
        text = row[MAILTITLEID]+" "+row[MAILBODYID]
        tokens,nbrOfSents = tokenize(text)
        results = text2daap(words,tokens)
        results[NBROFTOKENS] = len(tokens)
        results[NBROFSENTS] = nbrOfSents
        results[SENDER] = row[SENDERID]
        results[DATE] = row[MAILDATEID]
        printResults(features,results)

def main(argv):
    emails = []
    questionnaires = []
    words = readDaapDict(DAAPDIR+DAAPFILE)
    features = [DAAP]
    for inFile in sys.argv:
        tree = ET.parse(inFile)
        root = tree.getroot()
        thisId = makeId(inFile)
        emails.extend(getEmailData(root,thisId))
        questionnaires.extend(getQuestionnaires(root,thisId))
    if len(emails) > 0: emails2daap(emails,features,words)
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
