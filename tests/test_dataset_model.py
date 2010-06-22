# codeing=utf-8

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


import unittest

class TestDatasetModel(unittest.TestCase):

    def setUp(self):
        self.testSet = DataSet()


    def testSimpleImport(self):
        path = findApplicationBasePath() + '/testdata/test.txt'
        self.testSet.importDataset(path, True)
        self.assertEqual('test', self.testSet._displayName)
        self.assertEqual(11, self.testSet.nRows)
        self.assertEqual(5, self.testSet.nCols)



    def testVarnameObjectnameImport(self):
        path = findApplicationBasePath() + '/testdata/A_lables.txt'
        self.testSet.importDataset(path, True, True)
        self.assertEqual('a_lables', self.testSet._displayName)
        self.assertEqual(21, self.testSet.nRows)
        self.assertEqual(5, self.testSet.nCols)



if __name__ == '__main__':
    import os
    import sys

    # path for local imports
    setConsumerCheckIncludePath()
    from ds import DataSet

    unittest.main()
