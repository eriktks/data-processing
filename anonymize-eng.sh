#!/bin/bash
# anonymize-eng.sh: anonymize English text
# usage: anonymize-eng.sh file.txt
# 20181016 erikt(at)xs4all.nl

BINDIR="/home/erikt/projects/e-mental-health/data-processing"
INFILE=$1

source activate env
python3 $BINDIR/ner-eng.py < $INFILE |\
   python3 $BINDIR/anonymize-eng.py $INTERACTIVE

exit 0
