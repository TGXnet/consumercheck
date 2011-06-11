
import unittest
import test_tools

from enthought.traits.api import HasTraits, Str, Instance
from enthought.traits.ui.api import View, Item

# ConsumerCheck imports
from dataset import DataSet
from dataset_collection import DatasetCollection
from ui_datasets_tree import tree_view


class TestUiDatasetTree(unittest.TestCase):

    def setUp(self):
        pass

    def testImport(self):
        ds1 = DataSet(_ds_id = 'test1', _displayName = 'Test sett en')
        ds2 = DataSet(_ds_id = 'test2', _displayName = 'Test sett to')
        dc = DatasetCollection()
        dc.addDataset(ds1)
        dc.addDataset(ds2)
        dcUi = dc.configure_traits(view=tree_view)


if __name__ == '__main__':
    unittest.main()
