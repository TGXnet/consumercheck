
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
        self.assertEqual('test', self.testSet._ds_name)
        self.assertEqual(11, self.testSet.n_rows)
        self.assertEqual(5, self.testSet.n_cols)

    def testVarnameObjectnameImport(self):
        path = test_tools.findApplicationBasePath() + '/datasets/A_labels.txt'
        self.testSet.importDataset(path, True, True)
        self.assertEqual('a_labels', self.testSet._ds_name)
        self.assertEqual(21, self.testSet.n_rows)
        self.assertEqual(5, self.testSet.n_cols)


if __name__ == '__main__':
    unittest.main()
