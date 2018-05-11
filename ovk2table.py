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
DATEPATTERN1 = r"^Date:"
DATEPATTERN2 = r"^Verzonden:"
DATEPATTERN3 = r"^EDate:"
DATEPATTERN4 = r"^Sent:"
MAILHEADING = ["id","sender","receipient","date","subject","text"]
RECEIVERPATTERN1 = r"^Aan:"
RECEIVERPATTERN2 = r"^To:"
RECEIVERPATTERN3 = r"^ETo:"
SENDERPATTERN1 = r"^Van:"
SENDERPATTERN2 = r"^From:"
SENDERPATTERN3 = r"^EFrom:"
SENDER = "SENDER"
SUBJECTPATTERN1 = r"^Subject:"
SUBJECTPATTERN2 = r"^Onderwerp:"
SUBJECTPATTERN3 = r"^ESubject:"

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
    if re.match(r"^[0-9]+\b",receiver): return(COUNSELOR,CLIENT)
    elif re.match(r"^[A-Za-z]+\b",receiver): return(CLIENT,COUNSELOR)
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
    if re.match(r"^[0-9]+\b",sender): return(CLIENT,COUNSELOR)
    elif re.match(r"^[A-Za-z]+\b",sender): return(COUNSELOR,CLIENT)
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
    tokens = nltk.word_tokenize(text)
    tokenizedText = " ".join(tokens)
    return(tokenizedText)

def processMailHeader(mailText,inFileName):
    date, receiver, sender, subject = ("","","","")
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
            sender,receiver = findSender(line,inFileName)
        elif re.search(RECEIVERPATTERN1,line) or \
             re.search(RECEIVERPATTERN2,line) or \
             re.search(RECEIVERPATTERN3,line):
            sender,receiver = findReceiver(line,inFileName)
        elif re.search(SUBJECTPATTERN1,line) or \
             re.search(SUBJECTPATTERN2,line) or \
             re.search(SUBJECTPATTERN3,line): 
            subject = findSubject(line,inFileName)
        else: 
            break
        skipLines += 1
    mailText = "\n".join(mailLines[skipLines:])
    return(date, mailText, receiver, sender, subject)

def processMailText(thisId,mailText,inFileName):
    date, mailText, receiver, sender, subject = processMailHeader(mailText,inFileName)
    return([thisId,sender,receiver,date,tokenizeText(subject),tokenizeText(mailText)])

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
    return(mails)

def show(array):
    csvwriter = csv.writer(sys.stdout,delimiter=',')
    csvwriter.writerow(MAILHEADING)
    for row in array: csvwriter.writerow(row)
    return()

def main(argv):
    emails = []
    for inFileName in sys.argv:
        emails.extend(getMailData(inFileName))
    if len(emails) > 0: show(emails)
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
