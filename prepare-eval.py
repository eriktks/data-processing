#!/usr/bin/env python
"""
   prepare-eval.py: prepare anonymization output for evaluation
   usage: paste goldfile anofile | python prepare-eval
   note: expected input line format: goldtag ... predictedtag$
   20190430 erikt(at)xs4all.nl
"""

import getopt
import sys

COMMAND = sys.argv.pop(0)
DUMMY = "dummy"
ENTITYLABELS = [ "DATE","LOC","MISC","NUM","ORG","PER" ]
UNLABELED = "B-UNL"
UNLOPTION = "-u"

def processOptions(argv):
    optlist,args = getopt.getopt(argv,"u")
    opthash = {}
    for opt,val in optlist: opthash[opt] = val
    return(opthash,args)

def printFields(fields,options):
    if not fields[0] in ENTITYLABELS: fields[0] = "O"
    elif UNLOPTION in options: fields[0] = UNLABELED
    else: fields[0] = "B-"+fields[0]
    if not fields[-1] in ENTITYLABELS: fields[-1] = "O"
    elif UNLOPTION in options: fields[-1] = UNLABELED
    else: fields[-1] = "B-"+fields[-1]
    print(DUMMY,fields[0],fields[-1])

def main(argv):
    options,args = processOptions(argv)
    expectedFields = -1
    for line in sys.stdin:
        fields = line.split()
        if len(fields) == 0: print()
        else:
            if expectedFields < 0: expectedFields = len(fields)
            if len(fields) != expectedFields:
                sys.exit(COMMAND+": unexpected line: "+line)
            printFields(fields,options)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
