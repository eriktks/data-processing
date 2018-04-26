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
COUNSELOR = "COUNSELOR"
MAILHEADING = ["id","sender","receipient","date","subject","text"]

def findDate(line):
    match = re.search(r"[A-Z][a-z]\s+([0-9]+)-([0-9]+)-([0-9]+)\s*",line,re.IGNORECASE)
    if match:
        day = match.group(1)
        if len(day) < 2: day = "0"+day
        month = match.group(2)
        if len(month) < 2: month = "0"+month
        year = match.group(3)
        return(year+month+day)
    else: return("")

def findSender(line):
    sender = ""
    match = re.search(r"^\s*(Beste|Dag|Hallo|Hoi)\s([A-Za-z0-9]+)",line,re.IGNORECASE)
    if match: sender = match.group(2)
    if re.match(r"^[0-9]+$",sender): return(CLIENT,COUNSELOR)
    elif re.match(r"^[A-Za-z]+$",sender): return(COUNSELOR,CLIENT)
    else: return("","")

def findSubject(line):
    subject = ""
    match = re.search(r"^(Onderwerp|Subject):\s*(RE:)*\s*(.*)",line,re.IGNORECASE)
    if match: subject = match.group(3)
    return(subject)

def tokenizeText(text):
    tokens = nltk.word_tokenize(text)
    tokenizedText = " ".join(tokens)
    return(tokenizedText)

def getMailData(inFileName):
    inFile = open(inFileName,"r")
    mailText = ""
    mails = []
    sender = ""
    receiver = ""
    date = ""
    subject = ""
    thisId = re.sub(r"^(....)(.*)$",r"\1",inFileName)
    for line in inFile:
        nextDate = findDate(line)
        if sender == "": sender,receiver = findSender(line)
        if subject == "": subject = findSubject(line)
        if nextDate != "":
            if mailText != "":
                mails.append([thisId,sender,receiver,date,subject,tokenizeText(mailText)])
                sender = ""
                receiver = ""
                mailText = ""
            date = nextDate
        elif not re.search(r"^[a-zA-Z]+:\s",line):
            mailText += line+" "
    if mailText != "":
        mails.append([thisId,sender,receiver,date,subject,tokenizeText(mailText)])
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
