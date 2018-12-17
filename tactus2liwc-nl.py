#!/usr/bin/python3
"""
    tactus2liwc-nl.py: convert xml files from tactus to percentages of liwc categories
    usage: tactus2liwc-nl.py file1 [file2 ...]
    note: based on tactus2text.py, tactus2liwc-en.py and text2liwc.py
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
SENDERID = 1
MAILDATEID = 3
MAILTITLEID = 4
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
    thisId = re.sub(r"\.xml.*$","",thisId)
    return(thisId)

def anonymizeCounselor(name):
    if name != CLIENT: return(COUNSELOR)
    else: return(name)

# def tokenize(text):
#     return(" ".join(nltk.word_tokenize(text)))

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
    #   sentences = sentenceSplit(body)
    #   body = ""
    #   for s in sentences:
    #       if s in clientSentenceDates and clientSentenceDates[s] == date:
    #           if body != "": body += " "
    #           body += s
    #   clientMails[i][MAILBODYID] = body
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

LIWCDIR = "/home/erikt/projects/e-mental-health/liwc/"
LIWCFILE = "LIWC2015_English_Flat.dic"
TEXTBOUNDARY = "%"
NBROFTOKENS = "NBROFTOKENS"
NBROFSENTS = "NBROFSENTS"
NBROFMATCHES = "NBROFMATCHES"
MAXPREFIXLEN = 10
FROGPORT = 8080
FROGHOST = "localhost"
TOKENID = 0
LEMMAID = 1
NUMBER = "number"
numberId = -1
NEWFEATURENAMES = { NBROFTOKENS:NBROFTOKENS, NBROFSENTS:NBROFSENTS, SENDER:SENDER }

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

def readFeatureNames(inFile):
    global numberId

    featureNames = {}
    for line in inFile:
        line = line.strip()
        if line == TEXTBOUNDARY: break
        fields = line.split()
        featureId = fields.pop(0)
        featureName = " ".join(fields)
        featureName = re.sub(r"\s*\(.*$","",featureName)
        featureNames[featureId] = featureName
        if featureName == NUMBER: numberId = featureId
    return(featureNames)

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
    featureNames = readFeatureNames(inFile)
    words,prefixes = readWords(inFile)
    inFile.close()
    return(featureNames,words,prefixes)

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
    for token in tokens:
        if token in words:
            addFeatureToCounts(counts,NBROFMATCHES)
            for feature in words[token]: 
                addFeatureToCounts(counts,feature)
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

def printHeader(featureNames):
    first = True
    for featureName in featureNames.values():
        if not first: print(",",end="")
        else: first = False
        print(featureName,end="")
    print()

def printResults(featureNames,results):
    first = True
    for featureName in featureNames:
        if not first: print(",",end="")
        else: first = False
        if featureName in results: print(results[featureName],end="")
        else: print(0,end="")
    print()

def getMailText(row):
    mailTitle = row[MAILTITLEID]
    mailText = row[MAILBODYID]
    return(mailTitle+" "+mailText)

def addFeatures(feature,newFeatures):
    return({**feature,**newFeatures})

def emails2liwc(emails,featureNames,words,prefixes):
    for row in emails:
        if row[SENDERID] == CLIENT: 
            text = getMailText(row)
            tokens,nbrOfSents = tokenize(text)
            results = text2liwc(words,prefixes,tokens)
            results = addFeatures(results,{NBROFTOKENS:len(tokens),NBROFSENTS:nbrOfSents,SENDER:row[SENDERID]})
            printResults(featureNames,results)

def main(argv):
    emails,questionnaires = [],[]
    featureNames,words,prefixes = readLiwcDict(LIWCDIR+LIWCFILE)
    featureNames = addFeatures(featureNames,NEWFEATURENAMES)
    printHeader(featureNames)
    for inFile in sys.argv:
        root = ET.parse(inFile).getroot()
        thisId = makeId(inFile)
        emails.extend(getEmailData(root,thisId))
        questionnaires.extend(getQuestionnaires(root,thisId))
    if len(emails) > 0: emails2liwc(emails,featureNames,words,prefixes)
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
