# -*- coding: utf-8 -*-

def setConsumerCheckIncludePath():
    consumerBase = findApplicationBasePath();
    addLoadPath(consumerBase)

def findApplicationBasePath():
    basePath = os.getcwd()
    while os.path.basename(basePath) != 'tests':
        basePath = os.path.dirname(basePath)
    basePath = os.path.dirname(basePath)
    return basePath

def addLoadPath(baseFolderPath):
    sys.path.append(baseFolderPath)


# path for local imports
import os
import sys

appBase = findApplicationBasePath()
addLoadPath(appBase)

from file_import import FileData


import unittest

class TestUiDatasetTree(unittest.TestCase):

    def setUp(self):
        self.tf = appBase + '/testdata/'


    def testFileRead(self):
        readTest = FileData(self.tf + 'C_lables.txt', True, True)
        headers = readTest.getColumnHeader()
        matrix = readTest.getMatrix()
        print len(headers)
        print matrix.shape


if __name__ == '__main__':
    unittest.main()
