#!/usr/bin/env python3
"""
    anonymize-prepare-eval.py: prepare anonymization result for evaluation
    usage: anonymize-prepare-eval.py < file.txt
    note: expects single column with words and entities
    20190118 erikt(at)xs4all.nl
"""

import sys

ENTITIES = ["DATE","LOC","MISC","NUM","ORG","PER"]

def main(argv):
    for line in sys.stdin:
        line = line.strip()
        if line == "": print(line)
        elif line in ENTITIES: print("I-"+line) 
        else: print("O")

if __name__ == "__main__":
    sys.exit(main(sys.argv))
