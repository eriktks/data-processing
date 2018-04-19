#!/usr/bin/python3 -W all
"""
    tactus2table.py: convert xml files from tactus to csv tables
    usage: tactus2table.py file1 [file2 ...]
    20180412 erikt(at)xs4all.nl
"""

import csv
import nltk
import re
import sys
import xml.etree.ElementTree as ET

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" file1 [file2 ...]"
INTAKEQUESTIONNAIRE = "./Intake/Questionnaire"
QUESTIONNAIRE = "./Treatment/TreatmentSteps/TreatmentStep/Questionnaire"
QUESTIONNAIRETITLES = { "Intake":True,"Lijst tussenmeting":True,"Lijst nameting":True,"Lijst 3 maanden":True,"Lijst half jaar":True }
ANSWERS = "./Content/question/answer"
DIARYENTRIES = "./Diary/DiaryEntries/DiaryEntry"
MESSAGES = "./Messages/Message"
AGE = "leeftijd"
AGEEXTRA = " Leeftijd in jaren"
GENDER = "geslacht"
MARITAL = "woonsit"
EDUCATION = "opleidng"
EMPLOYMENT = "dagb"
MEDICATION = "medicijn"
SMOKING = "roken"
DRUGS = "drugs"
GAMBLING = "gokken"
PASTTHERAPYDRINK = "behdrink"
PASTTHERAPYPSYCH = "psych"
DRINKLESSH = "rcq1t"
MARKCOUNSELOR = "cijferhvn"
EFFECTIVEH = "intefft"
RECOMMENDH = "aanbevt"
CLIENT = "CLIENT"
SENDER = "Sender"
RECIPIENT = "Recipients"
QUESTION = "question"
DRINKLESSE = "rcq1n"
EFFECTIVEE = "inteffn"
RECOMMENDE = "aanbevn"
AMBIVALENT = "Niet mee eens, niet mee oneens"
DATE = "DateSent"
BODY = "Body"
SUBJECT = "Subject"
DATEID = 1
BODYID = 3
OUTPUTDIR = "/home/erikt/projects/e-mental-health/usb/output"
EMAILFILE = OUTPUTDIR+"/emails.csv"

def cleanupText(text):
    text = re.sub(r"\s+"," ",text)
    text = re.sub(r"^ ","",text)
    text = re.sub(r" $","",text)
    return(text)

def makeId(fileName):
    thisId = re.sub(r".*/","",fileName)
    thisId = re.sub(r"\.xml$","",thisId)
    return(thisId)

def getEmailData(root,thisId):
    clientMails = []
    counselorMails = []
    for message in root.findall(MESSAGES):
        body = ""
        date = ""
        sender = ""
        subject = ""
        for child in message:
            if child.tag == SENDER: sender = cleanupText(child.text)
            elif child.tag == DATE: date = cleanupText(child.text)
            elif child.tag == SUBJECT: subject = cleanupText(child.text)
            elif child.tag == BODY: body = cleanupText(child.text)
        if sender == CLIENT: clientMails.append([thisId,date,subject,body])
        else: counselorMails.append([thisId,date,subject,body])
    clientMails = cleanupMails(clientMails,counselorMails)
    return(clientMails)

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
        date = clientMails[i][DATEID]
        body = clientMails[i][BODYID]
        sentences = sentenceSplit(body)
        for s in sentences:
            if (s in clientSentenceDates and date < clientSentenceDates[s]) or \
                not s in clientSentenceDates:
                clientSentenceDates[s] = date
    for i in range(0,len(counselorMails)):
        date = counselorMails[i][DATEID]
        body = counselorMails[i][BODYID]
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
        date = clientMails[i][DATEID]
        body = clientMails[i][BODYID]
        sentences = sentenceSplit(body)
        body = ""
        for s in sentences:
            if s in clientSentenceDates and clientSentenceDates[s] == date:
                if body != "": body += " "
                body += s
        clientMails[i][BODYID] = body
    return(clientMails)

def store(array,outFileName):
    with open(outFileName,"w",encoding="utf8") as csvfile:
        csvwriter = csv.writer(csvfile,delimiter=',',quotechar='"')
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
    patients = []
    emails = []
    questionnaires = []
    for inFile in sys.argv:
        tree = ET.parse(inFile)
        root = tree.getroot()
        thisId = makeId(inFile)
        emails.extend(getEmailData(root,thisId))
        questionnaires.extend(getQuestionnaires(root,thisId))
    store(emails,EMAILFILE)
    storeDictTitles(questionnaires)
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
