#!/usr/bin/python3
"""
    tactus2table.py: convert xml files from tactus to csv tables
    usage: tactus2table.py file1 [file2 ...]
    20180412 erikt(at)xs4all.nl
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
DATE = "DateSent"
BODY = "Body"
SUBJECT = "Subject"
MAILDATEID = 3
MAILBODYID = 5
OUTPUTDIR = "/home/erikt/projects/e-mental-health/usb/output"
EMAILFILE = OUTPUTDIR+"/emails.csv"
EMAILHEADING = ["id","sender","receipient","date","subject","text"]

def cleanupText(text):
    text = re.sub(r"\s+"," ",text)
    text = re.sub(r"^ ","",text)
    text = re.sub(r" $","",text)
    return(text)

def makeId(fileName):
    thisId = re.sub(r".*/","",fileName)
    thisId = re.sub(r"\.xml$","",thisId)
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

def getTitles(questionnaires):
    titles = {}
    for q in questionnaires: titles[q["title"]] = True
    return(titles)

def getColumns(questionnaires,title):
    columns = {}
    for questionnaire in questionnaires:
        if questionnaire["title"] == title:
            for field in questionnaire.keys():
                columns[field] = True
    return(columns)

def storeDictTitles(questionnaires):
    titles = getTitles(questionnaires)
    for title in titles.keys():
        columns = getColumns(questionnaires,title)
        outFileName = OUTPUTDIR+"/"+title+".csv"
        with open(outFileName,"w",encoding="utf8") as csvfile:
            csvwriter = csv.writer(csvfile,delimiter=',',quotechar='"')
            heading = []
            for columnName in sorted(columns.keys()): 
                heading.append(columnName)
            csvwriter.writerow(heading)
            for questionnaire in questionnaires:
                if questionnaire["title"] == title:
                    row = []
                    for columnName in sorted(columns.keys()): 
                        try: row.append(questionnaire[columnName])
                        except: row.append("")
                    csvwriter.writerow(row)
            csvfile.close()
    return()

def main(argv):
    emails = []
    questionnaires = []
    for inFile in sys.argv:
        tree = ET.parse(inFile)
        root = tree.getroot()
        thisId = makeId(inFile)
        emails.extend(getEmailData(root,thisId))
        questionnaires.extend(getQuestionnaires(root,thisId))
    if len(emails) > 0: store(emails,EMAILFILE)
    storeDictTitles(questionnaires)
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
