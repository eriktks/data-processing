#!/usr/bin/env python3
"""
    mail2paragraphs.py: convert mail text to one paragraph per line
    usage: mail2paragraphs < file
    20181029 erikt(at)xs4all.nl
"""

import re
import sys

def endOfParagraph(line):
    return(line == "")

def isEmailHead(line):
    return(re.search(r"^\S+:\s",line))

def main(argv):
    paragraph = ""
    for line in sys.stdin:
        line = line.strip()
        if endOfParagraph(line):
            if paragraph != "":
                print(paragraph)
                paragraph = ""
        if paragraph == "" and isEmailHead(line):
            print(line)
        else:
            if paragraph != "": paragraph += " "
            paragraph += line
    if paragraph != "": print(paragraph)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
