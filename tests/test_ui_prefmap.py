# -*- coding: utf-8 -*-

import unittest
import test_tools

from enthought.traits.api import HasTraits, Str, Instance
from enthought.traits.ui.api import View, Item

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
		ds1.importDataset(baseFolder + '/testdata/A_lables.txt', True, True)
		ds2 = DataSet()
		ds2.importDataset(baseFolder + '/testdata/C_lables.txt', True, True)
		dc = DatasetCollection()
		prefmap = PrefmapModel(dsl=dc)
		dc.addDataset(ds1)
		dc.addDataset(ds2)
		prefmapUi = prefmap.configure_traits(view = prefmap_tree_view)


if __name__ == '__main__':
	unittest.main()
