#!/bin/bash
# anonymize-dut.sh: anonymize Dutch text
# usage: anonymize-dut.sh < file.txt
# 20181018 erikt(at)xs4all.nl

BINDIR="/home/erikt/projects/e-mental-health/data-processing"

source activate env
python3 $BINDIR/ner-frog.py |\
   python3 $BINDIR/anonymize-dut.py

exit 0
