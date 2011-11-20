
import unittest
import test_tools

from traits.api import HasTraits, Str, Instance
from traitsui.api import View, Item

# ConsumerCheck imports
from dataset import DataSet
from dataset_collection import DatasetCollection
from ui_datasets_tree import tree_view


class TestUiDatasetTree(unittest.TestCase):

    def setUp(self):
        pass

    def testImport(self):
        ds1 = DataSet(_ds_id = 'test1', _ds_name = 'Test sett en')
        ds2 = DataSet(_ds_id = 'test2', _ds_name = 'Test sett to')
        dc = DatasetCollection()
        dc.add_dataset(ds1)
        dc.add_dataset(ds2)
        dcUi = dc.configure_traits(view=tree_view)


if __name__ == '__main__':
    unittest.main()
