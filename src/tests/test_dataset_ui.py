
import unittest
import test_tools

# ConsumerCheck imports
from ds_ui import DataSet, ds_list_tab


class TestDatasetModel(unittest.TestCase):

    def setUp(self):
        self.testSet = DataSet()

    def testImport(self):
        path = test_tools.findApplicationBasePath() + '/datasets/test.txt'
        self.testSet.importDataset(path, True)
        self.assertEqual('test', self.testSet._ds_name)
        self.assertEqual(11, self.testSet.n_rows)
        self.assertEqual(5, self.testSet.n_cols)
        self.testSet.configure_traits( view=ds_list_tab )


if __name__ == '__main__':
    unittest.main()
