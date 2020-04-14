#!/usr/bin/env python
# getQuestions.py: extract questions from questionaires in tactus file
# usage: getQuestions.py file
# 20191022 erikt(at)xs4all.nl

import gzip
import re
import sys
import xml.etree.ElementTree as ET

INTAKEQUESTIONNAIRE = "./Intake/Questionnaire"
QUESTIONNAIRE = "./Treatment/TreatmentSteps/TreatmentStep/Questionnaire"
QUESTIONNAIRETITLES = { "Intake":True,"Lijst tussenmeting":True,"Lijst nameting":True,"Lijst 3 maanden":True,"Lijst half jaar":True }
QUESTIONS = "./Content/question"
TITLE = "title"
ANSWER = "answer"
QUESTIONNUMBER = "questionNumber"

def cleanupText(text):
    text = re.sub(r"\s+"," ",text)
    text = re.sub(r"^ ","",text)
    text = re.sub(r" $","",text)
    return(text)

def main(argv):
    inFileName = argv.pop(1)
    inFile = gzip.open(inFileName,"rb")
    inFileContent = inFile.read()
    inFile.close()
    root = ET.fromstring(inFileContent)
    for questionnaires in INTAKEQUESTIONNAIRE,QUESTIONNAIRE:
        for questionnaire in root.findall(questionnaires):
            title = cleanupText(questionnaire.findall("./Title")[0].text)
            print("###",title)
            if title in QUESTIONNAIRETITLES:
                questionNumber = "0"
                for question in questionnaire.findall(QUESTIONS):
                    questionTitle = ""
                    numbers = question.findall("./questionNumber")
                    if numbers != None and len(numbers) > 0:
                        questionNumber = cleanupText(numbers[0].text)
                    else:
                        questionNumber = str(int(questionNumber)+1)
                    for elementQ in question:
                        if elementQ.tag == TITLE: 
                            questionTitle = cleanupText(elementQ.text)
                        if elementQ.tag == QUESTIONNUMBER: 
                            questionNumber = cleanupText(elementQ.text)
                        if elementQ.tag == ANSWER: 
                            ID = elementQ.attrib["ID"]
                            answerTitle = ""
                            for elementA in elementQ:
                                if elementA.tag == TITLE: 
                                    answerTitle = cleanupText(elementA.text)
                            if answerTitle == "":
                                print(questionNumber,ID,questionTitle)
                            else:
                                print(questionNumber,ID,answerTitle)
                                questionTitle = answerTitle
 
if __name__ == "__main__":
    sys.exit(main(sys.argv))

exit(0)
