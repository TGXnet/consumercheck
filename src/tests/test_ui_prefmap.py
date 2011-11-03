
import unittest
import test_tools

from enthought.traits.api import HasTraits, Str, Instance
from enthought.traitsui.api import View, Item

# ConsumerCheck imports
from dataset import DataSet
from dataset_collection import DatasetCollection
from ui_tab_prefmap import PrefmapModel, prefmap_tree_view, prefmap_control


class TestUiPrefmap(unittest.TestCase):

    def setUp(self):
        pass

    def testImport(self):
        baseFolder = test_tools.findApplicationBasePath()
        ds1 = DataSet()
        ds1.importDataset(baseFolder + '/datasets/A_lables.txt', True, True)
        ds2 = DataSet()
        ds2.importDataset(baseFolder + '/datasets/C_lables.txt', True, True)
        dc = DatasetCollection()
        prefmap = PrefmapModel(dsl=dc)
        dc.add_dataset(ds1)
        dc.add_dataset(ds2)
        prefmapUi = prefmap.configure_traits(view = prefmap_tree_view)


if __name__ == '__main__':
    unittest.main()