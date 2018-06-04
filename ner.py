#!/usr/bin/python3 -W all
# ner.py: perform named antity recognition with frog
# usage: ner.py < text
# note adapted from: https://www.tutorialspoint.com/python/python_networking.htm
# 20180604 erikt(at)xs4all.nl

from pynlpl.clients.frogclient import FrogClient
import re
import socket
import sys

PORT = 8080
MAXDATA = 1024
NERID = 4
TOKENID = 0

def prettyPrint(data):
    for row in data:
        if len(row) >= NERID+1 : 
            lastLine = row[TOKENID]+" "+row[NERID]
            print(lastLine)
    print("")
    return()

frogclient = FrogClient('localhost',PORT,returnall=True)
for line in sys.stdin:
    data = frogclient.process(line)
    prettyPrint(data)

