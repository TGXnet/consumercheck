
import os
import sys
import logging

# Enthought imports
from enthought.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'wx'
# ETSConfig.toolkit = 'qt4'
from enthought.traits.api import HasTraits, Instance

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

logging.basicConfig(level=logging.DEBUG)
logging.info('Starts unittest')

setConsumerCheckIncludePath()

from dataset_collection import DatasetCollection
from dataset import DataSet

class TestMain(HasTraits):
    """Main frame for testing method tabs
    """
    to_be_tested = Instance(HasTraits)
    dsl = DatasetCollection()

    def __init__(self, *args, **kwargs):
        super(TestMain, self).__init__(*args, **kwargs)
        ds1 = DataSet()
        ds1.importDataset('../datasets/Ost.txt')
        ds2 = DataSet()
        ds2.importDataset('../datasets/Polser.txt', True, True)
        self.dsl.addDataset(ds1)
        self.dsl.addDataset(ds2)

    def _to_be_tested_changed(self, old, new):
        if old is not None:
            old.main_ui_ptr = None
        if new is not None:
            new.main_ui_ptr = self


if __name__== '__main__':
    container = TestMain()
