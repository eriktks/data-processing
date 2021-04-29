#!/bin/bash
# anonymize-ovk.sh: anonymize OVK mail data (text format)
# usage: anonymize-ovk.sh < file.txt
# 20181029 erikt(at)xs4all.nl

BINDIR="/home/erikt/projects/e-mental-health/data-processing"

source activate env
python3 $BINDIR/mail2paragraphs.py |\
   python3 $BINDIR/ner-frog.py |\
   python3 $BINDIR/anonymize-ovk.py

exit 0
