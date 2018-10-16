#!/usr/bin/env python3
# ner-eng.py: perform named entity recognition with frog
# usage: ner-eng.py < file
# note adapted from: https://www.tutorialspoint.com/python/python_networking.htm
# 20181016 erikt(at)xs4all.nl

import nltk
import sys

COMMAND = sys.argv.pop(0)

def printTree(tree,label):
    for node in tree:
        if type(node) == nltk.Tree: printTree(node,node.label())
        else: print(list(node)[0],list(node)[1],label)
    return(0)

text = ""
for line in sys.stdin: text += " "+line
sents = nltk.sent_tokenize(text)
for sent in sents:
    data = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent)))
    printTree(data,"O")

