#!/usr/bin/env python3
"""
    deduce-test.py: test the de-identification program deduce
    usage: deduce-test.py first_names initials surname given_name < file.ego
    note: deduce on github: https://github.com/vmenger/deduce
    20190121 erikt(at)xs4all.nl
"""

import deduce
import re
import sys

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+"first_names initials surname given_name < file"
ARGVLEN = 4
OUTSIDENE = "O"
CONVERT = { "DATUM":"DATE","INSTELLING":"ORG","LEEFTIJD":"NUM","LOCATIE":"LOC","MAIL":"O","PATIENT":"PER","PERSOON":"PER","TELEFOONNUMMER":"NUM","URL":"O" }

def readTextFromStdin():
    text = ""
    for line in sys.stdin: text += line
    return(text)

def annotationStart(token):
    return(re.search(r"^<[A-Z]",token))

def annotationEnd(token):
    return(re.search(r".>.*$",token))

def addMissingSpaces(line):
    line = re.sub(r"([^ ])<",r"\1 <",line)
    line = re.sub(r">([^ ])",r"> \1",line)
    return(line)

def printResults(annotatedText):
    paragraphs = annotatedText.split("\n")
    for par in paragraphs:
        par = addMissingSpaces(par)
        tokens = par.split(" ")
        t = 0
        while t < len(tokens):
            if annotationStart(tokens[t]):
                label = tokens[t]
                label = re.sub(r"<",r"",label)
                t += 1
                while t < len(tokens) and not re.search(r">",tokens[t]):
                    print(tokens[t],CONVERT[label],sep="\t")
                    t += 1
                if t >= len(tokens): 
                    sys.exit(COMMAND+": entity not closed on line: "+par)
                tokens[t] = re.sub(r">.*$",r"",tokens[t])
                if tokens[t] != "":
                    print(tokens[t],CONVERT[label],sep="\t")
            elif tokens[t] != "": 
                print(tokens[t],OUTSIDENE,sep="\t")
            t += 1
        print("")

def main(argv):
    if len(argv) != ARGVLEN: sys.exit(USAGE)
    first_names,initials,surname,given_name = argv
    text = readTextFromStdin()
    annotatedText = deduce.annotate_text(text, \
        first_names,initials,surname,given_name, \
        names=True, locations=True, institutions=True, dates=True, \
        ages=True, patient_numbers=True, phone_numbers=True, urls=True, \
        flatten=True)
    printResults(annotatedText)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

