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
                for question in questionnaire.findall(QUESTIONS):
                    questionTitle = ""
                    for elementQ in question:
                        if elementQ.tag == "title": 
                            questionTitle = cleanupText(elementQ.text)
                        if elementQ.tag == "answer": 
                            ID = elementQ.attrib["ID"]
                            answerTitle = ""
                            for elementA in elementQ:
                                if elementA.tag == "title": 
                                    answerTitle = cleanupText(elementA.text)
                            if answerTitle == "":
                                print(ID,questionTitle)
                            else:
                                print(ID,answerTitle)
 
if __name__ == "__main__":
    sys.exit(main(sys.argv))

exit(0)
