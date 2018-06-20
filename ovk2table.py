#!/usr/bin/python3
"""
    ovk2table.py: convert ovk files to csv format
    usage: ovk2table.py file1.text [file2.text ...] > outfile.csv
    note: first convert doc files to text with abiword --to=text file.doc
    20180426 erikt(at)xs4all.nl
"""

import csv
import nltk
import re
import sys

CLIENT = "CLIENT"
COMMAND = sys.argv.pop(0)
COUNSELOR = "COUNSELOR"
COUNSELORID = 1
DATEPATTERN1 = r"^Date :"
DATEPATTERN2 = r"^Verzonden :"
DATEPATTERN3 = r"^EDate :"
DATEPATTERN4 = r"^Sent :"
MAILHEADING = ["client-id","counselor","sender","receipient","nbrOfWords","nbrOfCharsInWords","nbrOfSents","nbrOfTokensInSents","date","subject","text"]
RECEIVERPATTERN1 = r"^Aan :"
RECEIVERPATTERN2 = r"^To :"
RECEIVERPATTERN3 = r"^ETo :"
REVERSEDFILE = "reversed.txt"
SENDERPATTERN1 = r"^Van :"
SENDERPATTERN2 = r"^From :"
SENDERPATTERN3 = r"^EFrom :"
SENDER = "SENDER"
SUBJECTPATTERN1 = r"^Subject :"
SUBJECTPATTERN2 = r"^Onderwerp :"
SUBJECTPATTERN3 = r"^ESubject :"
SENTSTART = "<s>"
SENTEND = "</s>"

reversedList = []

def findDate(line,inFileName):
    match = re.search(r"([0-9]+)-([0-9]+)-([0-9]+)(\s+([0-9]+):([0-9]+)(:([0-9]+))?)?",line)
    if not match: 
        sys.exit(COMMAND+": error: no date in file "+inFileName+" on line: "+line)
    else:
        day = match.group(1)
        if len(day) < 2: day = "0"+day
        month = match.group(2)
        if len(month) < 2: month = "0"+month
        year = match.group(3)
        hour = match.group(5)
        mins = match.group(6)
        secs = match.group(8)
        if hour is None: hour = "12"
        if mins is None: mins = "00"
        if secs is None: secs = "00"
        if len(hour) < 2: hour = "0"+hour
        if len(mins) < 2: mins = "0"+mins
        if len(secs) < 2: mins = "0"+secs
        return(year+"-"+month+"-"+day+"T"+hour+":"+mins+":"+secs)

def findReceiver(line,inFileName):
    match = re.search(RECEIVERPATTERN1+r" *(.*)",line)
    if match: receiver = match.group(1)
    else:
        match = re.search(RECEIVERPATTERN2+r" *(.*)",line)
        if match: receiver = match.group(1)
        else:
            match = re.search(RECEIVERPATTERN3+r" *(.*)",line)
            if match: receiver = match.group(1)
            else: sys.exit(COMMAND+": error: no receiver on line: "+line)
    matchNbr = re.match(r"^[0-9]+\b",receiver)
    matchChr = re.match(r"^[A-Za-z]+\b",receiver)
    if matchNbr: return(matchNbr.group(0),COUNSELOR,CLIENT)
    elif matchChr: return(matchChr.group(0),CLIENT,COUNSELOR)
    else: sys.exit(COMMAND+": error: no receiver in file "+inFileName+" on line: "+line)

def findSender(line,inFileName):
    match = re.search(SENDERPATTERN1+r" *(.*)",line)
    if match: sender = match.group(1)
    else:
        match = re.search(SENDERPATTERN2+r" *(.*)",line)
        if match: sender = match.group(1)
        else:
            match = re.search(SENDERPATTERN3+r" *(.*)",line)
            if match: sender = match.group(1)
            else: sys.exit(COMMAND+": error: no sender on line: "+line)
    matchNbr = re.match(r"^[0-9]+\b",sender)
    matchChr = re.match(r"^[A-Za-z]+\b",sender)
    if matchNbr: return(matchNbr.group(0),CLIENT,COUNSELOR)
    elif matchChr: return(matchChr.group(0),COUNSELOR,CLIENT)
    else: sys.exit(COMMAND+": error: no sender in file "+inFileName+" on line: "+line)

def findSubject(line,inFileName):
    match = re.search(SUBJECTPATTERN1+r" *(.*)",line)
    if match: subject = match.group(1)
    else:
        match = re.search(SUBJECTPATTERN2+r" *(.*)",line)
        if match: subject = match.group(1)
        else:
            match = re.search(SUBJECTPATTERN3+r" *(.*)",line)
            if match: subject = match.group(1)
            else: sys.exit(COMMAND+": error: no subject in file "+inFileName+"on line: "+line)
    return(subject)

def tokenizeText(text):
    sentences = nltk.sent_tokenize(text)
    tokens = []
    for s in sentences: 
        t = nltk.word_tokenize(s)
        tokens.append(SENTSTART)
        tokens.extend(t)
        tokens.append(SENTEND)
    tokenizedText = " ".join(tokens)
    return(tokenizedText)

def processMailHeader(mailText,inFileName):
    date, receiver, receiverName, sender, senderName, subject = ("","","","","","")
    mailLines = mailText.split("\n")
    skipLines = 0
    for line in mailLines:
        if re.search(DATEPATTERN1,line) or \
           re.search(DATEPATTERN2,line) or \
           re.search(DATEPATTERN3,line) or \
           re.search(DATEPATTERN4,line): 
            date = findDate(line,inFileName)
        elif re.search(SENDERPATTERN1,line) or \
             re.search(SENDERPATTERN2,line) or \
             re.search(SENDERPATTERN3,line):
            senderName,sender,receiver = findSender(line,inFileName)
        elif re.search(RECEIVERPATTERN1,line) or \
             re.search(RECEIVERPATTERN2,line) or \
             re.search(RECEIVERPATTERN3,line):
            receiverName,sender,receiver = findReceiver(line,inFileName)
        elif re.search(SUBJECTPATTERN1,line) or \
             re.search(SUBJECTPATTERN2,line) or \
             re.search(SUBJECTPATTERN3,line): 
            subject = findSubject(line,inFileName)
        else: 
            break
        skipLines += 1
    if senderName != "": counselor = senderName
    mailText = "\n".join(mailLines[skipLines:])
    if sender == CLIENT: 
        return(date, mailText, receiver, sender, subject, receiverName)
    elif receiver == CLIENT:
        return(date, mailText, receiver, sender, subject, senderName)

def analyzeText(text):
    tokens = text.split()
    nbrOfWords = 0
    nbrOfCharsInWords = 0
    nbrOfSents = 0
    nbrOfTokensInSents = 0
    for token in tokens:
        if token == SENTSTART: 
            nbrOfSents += 1 
        elif token != SENTEND:
            nbrOfTokensInSents += 1
            if re.match(r"[a-zA-Z]",token):
                nbrOfWords += 1
                nbrOfCharsInWords += len(token)
    return(nbrOfWords,nbrOfCharsInWords,nbrOfSents,nbrOfTokensInSents)

def processMailText(thisId,mailText,inFileName):
    date, mailText, receiver, sender, subject, counselor = processMailHeader(mailText,inFileName)
    tokenizedMailText = tokenizeText(mailText)
    (nbrOfWords, nbrOfCharsInWords, nbrOfSents, nbrTokensInSents) = analyzeText(tokenizedMailText)
    return([thisId,counselor,sender,receiver,nbrOfWords,nbrOfCharsInWords,nbrOfSents,nbrTokensInSents,date,tokenizeText(subject),tokenizedMailText])

def nextMailStarts(line):
    return(re.search(DATEPATTERN1,line) or
           re.search(DATEPATTERN2,line) or
           re.search(DATEPATTERN3,line) or
           re.search(DATEPATTERN4,line) or
           re.search(RECEIVERPATTERN1,line) or
           re.search(RECEIVERPATTERN2,line) or
           re.search(RECEIVERPATTERN3,line) or
           re.search(SENDERPATTERN1,line) or
           re.search(SENDERPATTERN2,line) or
           re.search(SENDERPATTERN3,line) or
           re.search(SUBJECTPATTERN1,line) or
           re.search(SUBJECTPATTERN2,line) or
           re.search(SUBJECTPATTERN3,line))

def fixCounselor(mails):
    counselor = ""
    for mail in mails:
        if mail[COUNSELORID] != "": 
            counselor = mail[COUNSELORID]
            break
    for i in range(0,len(mails)):
        if mails[i][COUNSELORID] == "": mails[i][COUNSELORID] = counselor
        elif mails[i][COUNSELORID] != counselor:
            print(COMMAND+": mismatching counselors: "+counselor+" "+mails[i][COUNSELORID])
    return(mails)

def checkOrder(mails,inFileName):
    global reversedList

    thisId = re.sub(r"\..*$","",inFileName)
    if not thisId in reversedList: return(mails)
    else: return(reversed(mails))

def getMailData(inFileName):
    mails = []
    mailText = ""
    lastLine = ""
    inFile = open(inFileName,"r")
    thisId = re.sub(r"^(.*/)?(....)(.*)$",r"\2",inFileName)
    for line in inFile:
        if nextMailStarts(line) and not nextMailStarts(lastLine) and \
           mailText != "":
            mails.append(processMailText(thisId,mailText,inFileName))
            mailText = ""
        mailText += line
        lastLine = line
    if mailText != "":
        mails.append(processMailText(thisId,mailText,inFileName))
    inFile.close()
    mails = fixCounselor(mails)
    mails = checkOrder(mails,inFileName)
    return(mails)

def show(array):
    csvwriter = csv.writer(sys.stdout,delimiter=',')
    csvwriter.writerow(MAILHEADING)
    for row in array: csvwriter.writerow(row)
    return()

def readReversed():
    reversedList = []
    try:
        inFile = open(REVERSEDFILE,"r")
        for line in inFile:
            line = line.rstrip()
            reversedList.append(line)
        inFile.close()
        return(reversedList)
    except:
        sys.warn(COMMAND+": warning: cannot read file "+REVERSEDFILE)
        return([])

def main(argv):
    global reversedList

    emails = []
    reversedList = readReversed()
    for inFileName in sys.argv:
        emails.extend(getMailData(inFileName))
    if len(emails) > 0: show(emails)
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
