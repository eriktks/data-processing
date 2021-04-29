#!/usr/bin/env python
"""
    mail2phrases.py: extract sequences of n words from mail messages
    usage: mail2phrases.py file1.xml [file2.xml ...]
    20190627 erikt(at)xs4all.nl
"""

import sys
import xml.etree.ElementTree as ET

BODY = "Body"
CLIENT = "CLIENT"
MESSAGE = "Message"
N = 20
SENDER = "Sender"


def text2phrases(text):
    words = text.split()
    wordBuffer = []
    for w in words:
        wordBuffer.append(w)
        if len(wordBuffer) >= N:
            print(" ".join(wordBuffer))
            wordBuffer.pop(0)

def printPhrases(root):
    for message in root.findall(".//"+MESSAGE):
        try:
            sender = message.findall("./"+SENDER)[0].text
            if sender != None:
                bodyText = message.findall("./"+BODY)[0].text
                text2phrases(bodyText)
        except: pass

def main(argv):
    for fileName in sys.argv[1:]:
        parser = ET.XMLParser(encoding="utf-8")
        tree = ET.parse(fileName,parser=parser)
        root = tree.getroot()
        printPhrases(root)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
