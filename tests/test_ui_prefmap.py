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


from enthought.traits.api import HasTraits, Str, Instance
from enthought.traits.ui.api import View, Item


# path for local imports
import os
import sys

setConsumerCheckIncludePath()
from ds import DataSet
from dataset_collection import DatasetCollection
from ui_tab_prefmap import PrefmapModel, prefmap_tree_view, prefmap_overview


import unittest

class TestUiPrefmap(unittest.TestCase):

    def setUp(self):
        pass


    def testImport(self):
        baseFolder = findApplicationBasePath()
        ds1 = DataSet()
        ds1.importDataset(baseFolder + '/testdata/test.txt')
        ds2 = DataSet()
        ds2.importDataset(baseFolder + '/testdata/Ost.txt')
        dc = DatasetCollection()
        prefmap = PrefmapModel(dsl=dc)
        dc.addDataset(ds1)
        dc.addDataset(ds2)
        prefmapUi = prefmap.configure_traits(view = prefmap_tree_view)


if __name__ == '__main__':
    unittest.main()
