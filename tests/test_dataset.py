
import unittest
import test_tools

# ConsumerCheck imports
from dataset import DataSet


class TestDatasetModel(unittest.TestCase):

    def setUp(self):
        self.testSet = DataSet()

    def testSimpleImport(self):
        path = test_tools.findApplicationBasePath() + '/datasets/test.txt'
        self.testSet.importDataset(path, True)
        self.assertEqual('test', self.testSet._displayName)
        self.assertEqual(11, self.testSet.nRows)
        self.assertEqual(5, self.testSet.nCols)

    def testVarnameObjectnameImport(self):
        path = test_tools.findApplicationBasePath() + '/datasets/A_lables.txt'
        self.testSet.importDataset(path, True, True)
        self.assertEqual('a_lables', self.testSet._displayName)
        self.assertEqual(21, self.testSet.nRows)
        self.assertEqual(5, self.testSet.nCols)


if __name__ == '__main__':
    unittest.main()
