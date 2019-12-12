#!/usr/bin/env python3
"""
    getCapitalized.py: get words from text which are only used in capitalized form
    usage: python3 getCapitalized < file.xml
    note: assumes text does not appear on lines containing xml tags
    20191212 erikt(at)xs4all.nl
"""

import re
import sys

def main(argv):
    capitalized = {}
    lowerCased = {}
    for line in sys.stdin:
        if not re.match(r"^.*<.*>.*$",line):
            tokens = line.split()
            for token in tokens:
                if not re.match(r"^.*[A-Z].*$",token): lowerCased[token.lower()] = True
                elif not token in capitalized and not token.lower() in lowerCased:
                    print(token)
                    capitalized[token] = True

if __name__ == "__main__":
    sys.exit(main(sys.argv))
