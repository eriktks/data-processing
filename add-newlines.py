#!/usr/bin/env python3
# add-newlines.py: add newlines to xml files (basic pretty print)
# usage: add-newlines.py < file.xml
# 20181016 erikt(at)xs4all.nl

import re
import sys

for line in sys.stdin:
    line = re.sub(r">",r">\n",line)
    line = re.sub(r"<",r"\n<",line)
    line = re.sub(r"\n\s*",r"\n",line)
    print(line,end="")
