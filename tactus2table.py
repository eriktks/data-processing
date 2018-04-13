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
INTAKE = "./Intake/Questionnaire/Content/question/answer"
HALFTIME = "./Treatment/TreatmentSteps/TreatmentStep/Questionnaire/Content/question/answer"
ENDTIME = HALFTIME
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
OUTPUTDIR = "../usb/output"
PATIENTFILE = OUTPUTDIR+"/patients.csv"
EMAILFILE = OUTPUTDIR+"/emails.csv"

def cleanupText(text):
    text = re.sub(r"\s+"," ",text)
    text = re.sub(r"^ ","",text)
    text = re.sub(r" $","",text)
    return(text)

def getAnswer(root,questionnaire,field):
    answers = []
    for answer in root.findall(questionnaire):
        if answer.attrib["ID"] == field:
            for answerText in answer:
                if answerText.tag == "answerText":
                    answer = cleanupText(answerText.text)
                    if answer == AMBIVALENT: answer = re.sub(",","",answer)
                    answer = re.sub(r"\s*,.*","",answer)
                    answers.append(answer)
    return(answers)

def count(root,elements):
    count = 0
    for element in root.findall(elements): count += 1
    return(count)

def countChildText(root,elements,tag,text):
    count = 0
    for element in root.findall(elements): 
        for child in element:
            if child.tag == tag and cleanupText(child.text) == text: count += 1
    return(count)

def countAll(root,elementName):
    count = 0
    for element in root.iter(elementName): count += 1
    return(count)

def makeId(fileName):
    thisId = re.sub(r".*/","",fileName)
    thisId = re.sub(r"\.xml$","",thisId)
    return(thisId)

def getPatientData(root,thisId):
    try: gender = getAnswer(root,INTAKE,GENDER)[0]
    except: gender = ""
    try: age = getAnswer(root,INTAKE,AGE)[0]
    except: age = ""
    age = re.sub(AGEEXTRA,"",age)
    try: marital = getAnswer(root,INTAKE,MARITAL)[0]
    except: marital = ""
    try: education = getAnswer(root,INTAKE,EDUCATION)[0]
    except: education = ""
    try: employment = getAnswer(root,INTAKE,EMPLOYMENT)[0]
    except: employment = ""
    try: medication = getAnswer(root,INTAKE,MEDICATION)[0]
    except: medication = ""
    try: smoking = getAnswer(root,INTAKE,SMOKING)[0]
    except: smoking = ""
    try: drugs = getAnswer(root,INTAKE,DRUGS)[0]
    except: drugs = ""
    try: gambling = getAnswer(root,INTAKE,GAMBLING)[0]
    except: gambling = ""
    try: pastTherapyDrink = getAnswer(root,INTAKE,PASTTHERAPYDRINK)[0]
    except: pastTherapyDrink = ""
    try: pastTherapyPsych = getAnswer(root,INTAKE,PASTTHERAPYPSYCH)[0]
    except: pastTherapyPsych = ""
    try: drinkLessH = getAnswer(root,HALFTIME,DRINKLESSH)[0]
    except: drinkLessH = ""
    try: markCounselorH = getAnswer(root,HALFTIME,MARKCOUNSELOR)[0]
    except: markCounselorH = ""
    try: effectiveH = getAnswer(root,HALFTIME,EFFECTIVEH)[0]
    except: effectiveH = ""
    try: recommendH = getAnswer(root,HALFTIME,RECOMMENDH)[0]
    except: recommendH = ""
    nbrOfDiaryEntries = count(root,DIARYENTRIES)
    nbrOfMessages = count(root,MESSAGES)
    nbrOfClientMessages = countChildText(root,MESSAGES,SENDER,CLIENT)
    nbrOfCounselorMessages = countChildText(root,MESSAGES,RECIPIENT,CLIENT)
    nbrOfQuestions = countAll(root,QUESTION)
    try: drinkLessE = getAnswer(root,ENDTIME,DRINKLESSE)[0]
    except: drinkLessE = ""
    try: markCounselorE = getAnswer(root,ENDTIME,MARKCOUNSELOR)[1]
    except: markCounselorE = ""
    try: effectiveE = getAnswer(root,ENDTIME,EFFECTIVEE)[0]
    except: effectiveE = ""
    try: recommendE = getAnswer(root,ENDTIME,RECOMMENDE)[0]
    except: recommendE = ""
    return([thisId,gender,age,marital,education,employment,medication,smoking,drugs,gambling,pastTherapyDrink,pastTherapyPsych,drinkLessH,markCounselorH,effectiveH,recommendH,drinkLessE,markCounselorE,effectiveE,recommendE,nbrOfDiaryEntries,nbrOfMessages,nbrOfClientMessages,nbrOfCounselorMessages])

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

patients = []
emails = []
for inFile in sys.argv:
    tree = ET.parse(inFile)
    root = tree.getroot()
    thisId = makeId(inFile)
    patients.append(getPatientData(root,thisId))
    emails.extend(getEmailData(root,thisId))
store(patients,PATIENTFILE)
store(emails,EMAILFILE)

