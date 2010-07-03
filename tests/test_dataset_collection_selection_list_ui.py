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


import unittest


class TestSelectionListUi(unittest.TestCase):

    def setUp(self):
        self.testColl = DatasetCollection()
        set1 = DataSet(_internalName = 'set1', _displayName = 'Set 1')
        self.testColl.addDataset(set1)
        set2 = DataSet(_internalName = 'set2', _displayName = 'Set 2')
        self.testColl.addDataset(set2)


    def testTull(self):
        self.testColl.configure_traits(view = selection_list_view)



if __name__ == '__main__':
    import os
    import sys

    # path for local imports
    setConsumerCheckIncludePath()
    from dataset_collection import DatasetCollection, DataSet
    #from dataset_collection_selection_list_ui import SelectionListHandler
    from dataset_collection_selection_list_ui import selection_list_view

    unittest.main()