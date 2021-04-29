#!/usr/bin/env python3
"""
    ner-nltk.py: perform named entity recognition with nltk toolkit
    usage: ner-nltk.py < file
    notes:
    * adapted from: https://www.tutorialspoint.com/python/python_networking.htm
    * expects as input one paragraph per line
    * outputs lines with format: token SPACE postag SPACE nertag
    * outputs empty line between sentences
    * only available for English; other languages require retraining ner AND pos
    20181016 erikt(at)xs4all.nl
"""

import nltk
import sys

COMMAND = sys.argv.pop(0)
OUTSIDENELABEL = "O"

def printTree(tree,parentNELabel):
    for node in tree:
        if type(node) == nltk.Tree: printTree(node,node.label())
        else:
            token = list(node)[0]
            postag = list(node)[1]
            print(token,postag,parentNELabel)

def splitInSentences(text):
    return(nltk.sent_tokenize(text))

def processWithNltk(sentence):
    return(nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sentence))))

def main(argv):
    for line in sys.stdin:
        sentences = splitInSentences(line)
        for sentence in sentences:
            nltkOutput = processWithNltk(sentence)
            printTree(nltkOutput,OUTSIDENELABEL)
            print()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
