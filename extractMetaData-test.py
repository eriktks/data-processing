#!/usr/bin/env python3
"""
    extractMetaData-test.py: tests for extractMetaData.py
    usage: extractMetaData-test.py
    20190215 erikt(at)xs4all.nl
"""

import unittest
import extractMetaData as emd

CESDTOTALT0 = 13
CESDTOTALT1 = 15
MHCTOTALT0 = 42
MHCTOTALT1 = 28
GENDER = "GeslachtA"
BIRTHDATE = "geboortedatumA"
FINISHED = "Cursusafgerond"
AGEGROUP = "agegroup2_t0"
AGE = "Leeftijd_t0"

class myTest(unittest.TestCase):
    def testExtractMetaData(self):
        data = emd.readData()
        cesdTotalT0 = emd.getFieldTotal(data[0],emd.FIELDCESDIN,emd.FIELDT0IN,emd.CESDVALUES,emd.MAXCESD,False)
        mhcTotalT0 = emd.getFieldTotal(data[0],emd.FIELDMHC,emd.FIELDT0IN,emd.MHCVALUES,emd.MAXMHC,True)
        cesdTotalT1 = emd.getFieldTotal(data[0],emd.FIELDCESDIN,emd.FIELDT1IN,emd.CESDVALUES,emd.MAXCESD,False)
        mhcTotalT1 = emd.getFieldTotal(data[0],emd.FIELDMHC,emd.FIELDT1IN,emd.MHCVALUES,emd.MAXMHC,True)
        self.assertEqual(cesdTotalT0,CESDTOTALT0)
        self.assertEqual(cesdTotalT1,CESDTOTALT1)
        self.assertEqual(mhcTotalT0,MHCTOTALT0)
        self.assertEqual(mhcTotalT1,MHCTOTALT1)

if __name__ == '__main__':
    unittest.main()
