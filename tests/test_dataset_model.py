# codeing=utf-8

def setConsumerCheckIncludePath():
    consumerBase = findApplicationBasePath('ConsumerCheck');
    addLoadPath(consumerBase)


def findApplicationBasePath(baseFolderName):
    basePath = os.getcwd()
    while os.path.basename(basePath) != baseFolderName:
        basePath = os.path.dirname(basePath)

    return basePath


def addLoadPath(baseFolderPath):
    sys.path.append(baseFolderPath)


import unittest

class TestDatasetModel(unittest.TestCase):

    def setUp(self):
        self.testSet = DataSet()


    def testImport(self):
        path = findApplicationBasePath('ConsumerCheck') + '/testdata/Ost.txt'
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
