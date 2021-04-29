#!/bin/bash
# count-mails.bash: count number of mails from client and counselor per session
# usage: count-mails.bash
# note: writes output to files mails-per-client.csv and mails-per-client.txt
# 20191220 erikt(at)xs4all.nl

for F in AdB????-an.xml.gz
do
   SENDERCLIENTCOUNT=`gunzip -c $F |grep "<Sender>CLIENT"|wc -l`;
   SENDERCOUNSELORCOUNT=`gunzip -c $F |grep "<Sender>"|grep -v "<Sender>CLIENT"|wc -l`
   echo $SENDERCLIENTCOUNT $SENDERCOUNSELORCOUNT $F
done |\
   sed 's/REST.//' | sed 's/AdB0*//' | sed 's/-an.xml.gz//' |\
   sort -n -k 3 | tee mails-per-client.txt | tr " " "," > mails-per-client.csv

exit 0
