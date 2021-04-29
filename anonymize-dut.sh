#!/bin/bash
# anonymize-dut.sh: anonymize Dutch text
# usage: anonymize-dut.sh file.txt
# 20181018 erikt(at)xs4all.nl

BINDIR="/home/erikt/projects/e-mental-health/data-processing"
INFILE="$1"

python $BINDIR/ner-frog.py < $INFILE |\
   python $BINDIR/anonymize-ovk.py -n

exit 0
