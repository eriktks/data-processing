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

exceptions = {"medi0":True,"medi00":True,"drugs0":True}
valueCounts = {}

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

def tokenize(text):
    return(" ".join(nltk.word_tokenize(text)))

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
            elif child.tag == DATE: date = cleanupText(child.text)
            elif child.tag == SUBJECT: subject = tokenize(cleanupText(child.text))
            elif child.tag == BODY: body = cleanupText(child.text)
        if sender == CLIENT: clientMails.append([thisId,sender,recipient,date,subject,body])
        else: counselorMails.append([thisId,sender,recipient,date,subject,body])
    clientMails = cleanupMails(clientMails,counselorMails)
    counselorMails = cleanupMails(counselorMails,clientMails)
    allMails = clientMails
    allMails.extend(counselorMails)
    return(sorted(allMails,key=lambda subList:subList[MAILDATEID]))

# the sentence chunks produced by nltk are quite coarse and
# leave too much of the quoted text in the emails
def sentenceSplitNltk(text): return(nltk.sent_tokenize(text))

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
        sentences = sentenceSplit(body)
        body = ""
        for s in sentences:
            if s in clientSentenceDates and clientSentenceDates[s] == date:
                if body != "": body += " "
                body += s
        clientMails[i][MAILBODYID] = body
    return(clientMails)

def store(array,outFileName):
    with open(outFileName,"w",encoding="utf8") as csvfile:
        csvwriter = csv.writer(csvfile,delimiter=',',quotechar='"')
        csvwriter.writerow(EMAILHEADING)
        for row in array: csvwriter.writerow(row)
    csvfile.close()

def removeInitialKeywords(value):
    return(re.sub("^.*:\s*","",value))

def removeDoubleQuotes(value):
    return(cleanupText(re.sub(r"\"","",value)))

def removeCommas(value):
    return(cleanupText(re.sub(r","," ",value)))

def isEmptyString(value):
    return(re.search(r"^\s*$",value))

def getFirstWordIfNumber(value):
    return(re.search(r"(\d+)\s",value))

def isMultiword(value):
    return(re.search(r"\s",value))

def isMailAddress(value):
    return(re.search(r"@",value))

def isPhoneNumber(value):
    return(re.search(r"\d\d\d\d\d",value))

def count(value,questionaireTitle):
    global valueCounts
    if not questionaireTitle in valueCounts: 
        valueCounts[questionaireTitle] = {}
    if value in valueCounts[questionaireTitle]: 
        valueCounts[questionaireTitle][value] += 1
    else: 
        valueCounts[questionaireTitle][value] = 1
    return()

def summarizeCellValueFirst(value,questionaireTitle):
    value = removeCommas(removeDoubleQuotes(removeInitialKeywords(value))).lower()
    if isEmptyString(value): return(EMPTYTOKEN)
    count(value,questionaireTitle)
    return(value)

def summarizeCellValueLast(value):
    firstWordIfNumber = getFirstWordIfNumber(value)
    if firstWordIfNumber != None: return(firstWordIfNumber[1])
    elif isMultiword(value): return(MULTIWORDTOKEN)
    elif isMailAddress(value) or isPhoneNumber(value): return(REMOVEDTOKEN)
    else: return(value)

def getQuestionnaires(root,thisId):
    global exceptions
    qs = []
    for questionnaires in INTAKEQUESTIONNAIRE,QUESTIONNAIRE:
        for questionnaire in root.findall(questionnaires):
            title = cleanupText(questionnaire.findall("./Title")[0].text)
            if title in QUESTIONNAIRETITLES:
                q = {"0-title":title,"0-id":thisId}
                for question in questionnaire.findall(QUESTIONS):
                    numbers = question.findall("./questionNumber")
                    if numbers != None and len(numbers) > 0:
                        number = cleanupText(numbers[0].text)
                        for answer in question.findall(ANSWERS):
                            try:
                                key = answer.attrib["ID"]
                                shortKey = key
                                if not key in exceptions:
                                    shortKey = re.sub(r"t0$",r"",shortKey)
                                    #shortKey = re.sub(r"([a-z])0*$",r"\1",shortKey)
                                    #shortKey = re.sub(r"([a-rs-z0-9])t*$",r"\1",shortKey)
                                value = cleanupText(answer.findall("./answerText")[0].text)
                                summary = summarizeCellValueFirst(value,title)
                                if summary != "" and summary != EMPTYTOKEN:
                                    qKey = number+SEPARATOR+shortKey
                                    if qKey in q:
                                        print("clash for",thisId,title,shortKey,qKey,":",q[qKey],"<>",summary)
                                    q[qKey] = summary
                            except: continue 
                qs.append(q)
    return(qs)

def getTitles(questionnaires):
    titles = {}
    for q in questionnaires: titles[q["0-title"]] = True
    return(titles)

def getColumns(questionnaires,title):
    columns = {}
    for questionnaire in questionnaires:
        if questionnaire["0-title"] == title:
            for field in questionnaire.keys():
                columns[field] = True
    return(columns)

def countsFilter(value,questionaireTitle):
    global valueCounts
    if questionaireTitle in valueCounts and \
       value in valueCounts[questionaireTitle] and \
       valueCounts[questionaireTitle][value] >= MINVALUE: return(value)
    else: return(summarizeCellValueLast(value))

def keyCombine(number,string):
    return(str(number)+SEPARATOR+string)

def keySplit(key):
    keyParts = key.split(SEPARATOR)
    return(int(keyParts[0]),keyParts[1])

def sortKeys(keys):
    splitKeys = [keySplit(k) for k in keys]
    sortedKeys = sorted(splitKeys,key=itemgetter(0,1))
    return([keyCombine(k[0],k[1]) for k in sortedKeys])

def storeDictTitles(questionnaires):
    titles = getTitles(questionnaires)
    for title in titles.keys():
        columns = getColumns(questionnaires,title)
        outFileName = OUTPUTDIR+"/"+title+".csv"
        with open(outFileName,"w",encoding="utf8") as csvfile:
            csvwriter = csv.writer(csvfile,delimiter=',',quotechar='"')
            heading = []
            for columnName in sortKeys(columns.keys()): 
                heading.append(columnName)
            csvwriter.writerow(heading)
            for questionnaire in questionnaires:
                if questionnaire["0-title"] == title:
                    row = []
                    for columnName in sortKeys(columns.keys()):
                        try: row.append(countsFilter(questionnaire[columnName],title))
                        except: row.append(EMPTYTOKEN)
                    csvwriter.writerow(row)
            csvfile.close()
    return()

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

def main(argv):
    emails = []
    questionnaires = []
    for inFileName in sys.argv:
        root = readRootFromFile(inFileName)
        thisId = makeId(inFileName)
        emails.extend(getEmailData(root,thisId))
        questionnaires.extend(getQuestionnaires(root,thisId))
    # if len(emails) > 0: store(emails,EMAILFILE)
    storeDictTitles(questionnaires)
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
