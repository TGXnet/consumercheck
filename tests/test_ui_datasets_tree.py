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
from ui_datasets_tree import tree_view



import unittest

class TestUiDatasetTree(unittest.TestCase):

    def setUp(self):
        pass


    def testImport(self):
        ds1 = DataSet(_internalName = 'test1', _displayName = 'Test sett en')
        ds2 = DataSet(_internalName = 'test2', _displayName = 'Test sett to')
        dc = DatasetCollection()
        dc.addDataset(ds1)
        dc.addDataset(ds2)
        dcUi = dc.configure_traits(view=tree_view)


if __name__ == '__main__':
    unittest.main()
