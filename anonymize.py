#!/usr/bin/python -W all
# anonymize.py: remove personal information from any text file
# usage: anonymize.py < file
# note: might miss words with punctuation attached to them
# 20180604 erikt(at)xs4all.nl

import mydict
import re
import sys

def anonymize(line):
    tokens = re.split("(\s+)",line)
    for i in range(0,len(tokens)):
        if tokens[i] in mydict.mydict:
            tokens[i] = mydict.mydict[tokens[i]]
        elif re.search(r"@",tokens[i]):
            tokens[i] = "MAIL"
        tokens[i] = re.sub(r"^0\d\d\b","PHONE",tokens[i])
        tokens[i] = re.sub(r"\d\d\d\d\d\d*","PHONE",tokens[i])
    line = "".join(tokens)
    return(line)

def main(argv):
    for line in sys.stdin:
        print(anonymize(line.rstrip()))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
