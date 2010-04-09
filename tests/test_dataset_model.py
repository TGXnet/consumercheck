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


    def testImport(self):
        path = findApplicationBasePath() + '/testdata/Ost.txt'
        self.testSet.importDataset(path, True)
        self.assertEqual('ost', self.testSet._displayName)
        self.assertEqual(336, self.testSet.nRows)
        self.assertEqual(20, self.testSet.nCols)



if __name__ == '__main__':
    import os
    import sys

    # path for local imports
    setConsumerCheckIncludePath()
    from ds import DataSet

    unittest.main()
