#!/usr/bin/env python
"""
    mark-duplicate-phrases.py: mark duplicate sequences of n words
    usage: mark-duplicate-phrases.py file1.xml [file2.xml ...]
    notes: 
    * divides body texts in texts (original) and dups (duplicates)
    * ref attributes contain message ids and word ids (n.m)
    20190723 erikt(at)xs4all.nl
"""

import sys
import xml.etree.ElementTree as ET

BODY = "Body"
MESSAGE = "Message"
N = 16

phraseFrequencies = {}
phraseInitialPos = {}

def makeRefId(fileName,message,i):
    return(fileName+"."+message.attrib["id"]+"."+str(i+1))

def countPhrases(fileName,message):
    global phraseFrequencies,phraseInitialPos

    words = message.text.split()
    inDuplicate = False
    duplicateStarts,duplicateEnds,duplicateRefs = [],[],[]
    for i in range(0,len(words)-N):
        phrase = " ".join(words[i:i+N])
        if phrase in phraseFrequencies: 
            phraseFrequencies[phrase] += 1
            if not inDuplicate:
                inDuplicate = True
                duplicateStarts.append(i)
                duplicateRefs.append(phraseInitialPos[phrase])
        else: 
            phraseFrequencies[phrase] = 1
            phraseInitialPos[phrase] = makeRefId(fileName,message,i)
            if inDuplicate:
                inDuplicate = False
                duplicateEnds.append(i+N-2)
    if inDuplicate: duplicateEnds.append(len(words)-1)
    return(duplicateStarts,duplicateEnds,duplicateRefs)

def markDuplicates(message,duplicateStarts,duplicateEnds,duplicateRefs):
    words = message.text.split()
    message.text = ""
    wordIndex = 0
    while len(duplicateStarts) > 0:
        indexDuplicateStarts = duplicateStarts.pop(0)
        indexDuplicateEnds = duplicateEnds.pop(0)
        duplicateRef = duplicateRefs.pop(0)
        if indexDuplicateStarts > wordIndex:
            text = ET.SubElement(message,"text")
            text.text = " ".join(words[wordIndex:indexDuplicateStarts])
        if indexDuplicateStarts < indexDuplicateEnds:
            dup = ET.SubElement(message,"dup")
            dup.text = " ".join(words[indexDuplicateStarts:indexDuplicateEnds+1])
            dup.attrib["ref"] = duplicateRef
        wordIndex = indexDuplicateEnds+1
    if wordIndex < len(words):
        text = ET.SubElement(message,"text")
        text.text = " ".join(words[wordIndex:])

def convertMessages(fileName,messages):
    for key in sorted(messages.keys()):
        if messages[key].text != None:
            duplicateStarts,duplicateEnds,duplicateRefs = countPhrases(fileName,messages[key])
            markDuplicates(messages[key],duplicateStarts,duplicateEnds,duplicateRefs)

def getMessages(root):
    messages = {}
    idCounter = 0
    for message in root.findall(".//"+MESSAGE):
        try:
            dateSent = message.findall("./"+"DateSent")[0].text
            messages[dateSent] = message.findall("./"+BODY)[0]
            idCounter += 1
            messages[dateSent].attrib["id"] = str(idCounter)
        except Exception as e:
            sys.exit("error processing message "+message+" "+str(e))
    return(messages)

def makeOutputFileName(fileName):
    fileNameParts = fileName.split(".")
    fileNameParts[-2] += "-dup"
    return(".".join(fileNameParts))

def main(argv):
    for fileName in sys.argv[1:]:
        parser = ET.XMLParser(encoding="utf-8")
        tree = ET.parse(fileName,parser=parser)
        root = tree.getroot()
        messages = getMessages(root)
        convertMessages(makeOutputFileName(fileName),messages)
        tree.write(makeOutputFileName(fileName))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
