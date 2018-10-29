#!/usr/bin/env python3 -W all
"""
    ner-frog.py: perform named entity recognition for Dutch
    usage: ner-frog.py < text
    notes:
    * adapted from: https://www.tutorialspoint.com/python/python_networking.htm
    * requires frog running and listening on localhost port 8080
    * output lines with format: token SPACE postag SPACE nertag
    * outputs empty line between sentences
    20180604 erikt(at)xs4all.nl
"""

from pynlpl.clients.frogclient import FrogClient
import sys

COMMAND = sys.argv.pop(0)
HOST = "localhost"
PORT = 8080
NOFROGCONTACTMSG = "no Frog found on port "+str(PORT)+"! is it running?"
NOFROGOUTPUTMSG = "no data received from Frog! is it running?"
NERID = 4
POSID = 3
TOKENID = 0

def error(string):
    sys.exit(COMMAND+": error: "+string)

def tokenInfoIsComplete(row):
    return(row[TOKENID] != None and len(row) >= NERID+1)

def tokenInfoIsIncomplete(row):
    return(not tokenInfoIsComplete(row) and len(row) > 0 and row[TOKENID] != None)

def printTokenInfo(row):
    print(row[TOKENID],row[POSID],row[NERID])

def printEndOfSentence():
    print("")

def prettyPrint(data):
    for row in data:
        if tokenInfoIsComplete(row): printTokenInfo(row)
        elif tokenInfoIsIncomplete(row): error("incomplete token: "+str(row))
        else: printEndOfSentence()

def connectToFrog():
    try: frogClient = FrogClient(HOST,PORT,returnall=True)
    except Exception as e: error(NOFROGCONTACTMSG+" "+str(e))
    return(frogClient)

def processWithFrog(frogClient,text):
    try: frogOutput = frogClient.process(text)
    except Exception as e: error(NOFROGOUTPUTMSG+" "+str(e))
    return(frogOutput)

def readTextFromStdin():
    text = ""
    for line in sys.stdin: text += " "+line.strip()
    return(text)

def main(argv):
    frogClient = connectToFrog()
    text = readTextFromStdin()
    frogOutput = processWithFrog(frogClient,text)
    prettyPrint(frogOutput)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
