#!/usr/bin/python3
"""
    tactus2liwc-en.py: convert xml files from tactus to liwc scores per mail csv
    usage: tactus2liwc-en.py file1.xml [file2.xml ...] > file1.csv
    note: based on tactus2table.py and text2liwc.py
    20181218 erikt(at)xs4all.nl
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
DIARIES = "./Diary/DiaryEntries/DiaryEntry"
AGE = "leeftijd"
CLIENT = "CLIENT"
COUNSELOR = "COUNSELOR"
DIARY = "DIARY"
SENDER = "Sender"
RECIPIENT = "Recipients"
QUESTION = "question"
DATESENT = "DateSent"
DIARYDATE = "Date"
DATE = "DATE"
TIME = "Time"
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
LIWCDIR = "/home/erikt/projects/e-mental-health/liwc/"
LIWCFILE = "LIWC2015_English_Flat.dic"
TEXTBOUNDARY = "%"
NBROFTOKENS = "NBROFTOKENS"
NBROFSENTS = "NBROFSENTS"
NBROFMATCHES = "NBROFMATCHES"
NUMBER = "number"
TEXT = "text"
METADATAFEATURES = [DATE,NBROFTOKENS,NBROFSENTS,NBROFMATCHES,SENDER]
SNAPSHOT = "Snapshot"

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

def getNodeText(node):
    text = ""
    for child in node: text += getNodeText(child)
    if node.text != "" and node.text != None: text += node.text+"\n\n"
    return(text)

def getDiaryData(root,thisId):
    diaries = []
    subject = ""
    for entry in root.findall(DIARIES):
        date = ""
        text = ""
        for child in entry:
            if child.tag == DIARYDATE: date = cleanupText(child.text)+date
            elif child.tag == TIME: date = date+"T"+cleanupText(child.text)
            elif child.tag == SNAPSHOT: text += getNodeText(child)
        if text != "": diaries.append([thisId,DIARY,DIARY,date,subject,text])
    return(diaries)

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
        featureName = re.sub(r"\s*\(.*$","",featureName)
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

def readLiwcDict(inFileName):
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

    counts = { NBROFMATCHES:0 }
    c = 1
    for token in tokens:
        if token in words:
            addFeatureToCounts(counts,NBROFMATCHES)
            for feature in words[token]: 
                addFeatureToCounts(counts,feature)
                if feature == "1": 
                    c += 1
        longestPrefix = findLongestPrefix(prefixes,token)
        if longestPrefix != "":
            addFeatureToCounts(counts,NBROFMATCHES)
            for feature in prefixes[longestPrefix]:
                addFeatureToCounts(counts,feature)
        if isNumber(token): 
            addFeatureToCounts(counts,NBROFMATCHES)
            addFeatureToCounts(counts,numberId)
    return(counts)

def readTextFromStdin():
    text = ""
    for line in sys.stdin: text += line
    return(text)

def printHeader(features):
    for i in range(0,len(METADATAFEATURES)):
        if i != 0: print(",",end="")
        print(METADATAFEATURES[i],end="")
    for value in features.values():
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

def emails2liwc(emails,features,words,prefixes):
    global headerPrinted

    if not headerPrinted:
        printHeader(features)
        headerPrinted = True
    for row in emails:
        text = row[MAILTITLEID]+" "+row[MAILBODYID]
        tokens,nbrOfSents = tokenize(text)
        results = text2liwc(words,prefixes,tokens)
        results[NBROFTOKENS] = len(tokens)
        results[NBROFSENTS] = nbrOfSents
        results[SENDER] = row[SENDERID]
        results[DATE] = row[MAILDATEID]
        printResults(features,results)

def main(argv):
    emails = []
    questionnaires = []
    features,words,prefixes = readLiwcDict(LIWCDIR+LIWCFILE)
    for inFile in sys.argv:
        tree = ET.parse(inFile)
        root = tree.getroot()
        thisId = makeId(inFile)
        emails.extend(getEmailData(root,thisId))
        emails.extend(getDiaryData(root,thisId))
        questionnaires.extend(getQuestionnaires(root,thisId))
    if len(emails) > 0: emails2liwc(emails,features,words,prefixes)
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
