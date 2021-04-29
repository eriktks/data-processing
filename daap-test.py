#!/usr/bin/python3 -W all
"""
    daap-test.py: tests for daap.py
    usage: daap-test.py
    20190204 erikt(at)xs4all.nl
"""

import sys
import unittest
from daap import daap

TEXT = "This is a test ."
# WRAD scores: this:-; is:-1; a:.625; test:-; .:-
WINDOWSIZE1 = 1
WINDOWSIZE2 = 2
RESULTS1 = [0.0, -1.0, 0.625, 0.0, 0.0]
RESULTS2 = [-0.07394182491906767, -0.8059027095874471, 0.45863089393209766, 0.04621364057441729, 0.0]

class myTest(unittest.TestCase):
    def testDaap(self):
        results = daap(TEXT,WINDOWSIZE1)
        self.assertEqual(len(results),len(TEXT.split()))
        self.assertEqual(results,RESULTS1)
        results = daap(TEXT,WINDOWSIZE2)
        self.assertEqual(len(results),len(TEXT.split()))
        self.assertEqual(results,RESULTS2)

if __name__ == '__main__':
    unittest.main()
