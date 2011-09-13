
import os
import sys
import logging

# Enthought imports
from enthought.etsconfig.api import ETSConfig
# ETSConfig.toolkit = 'wx'
# ETSConfig.toolkit = 'qt4'
from enthought.traits.api import HasTraits, Instance

def setConsumerCheckIncludePath():
#    consumerBase = findApplicationBasePath();
    consumerBase = '../src'
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
from file_importer import FileImporter


def make_dsl_mock():
    dsl = DatasetCollection()
    ds_importer = FileImporter()
    dsl.addDataset(ds_importer.noninteractiveImport('../src/datasets/Ost.txt'))
    dsl.addDataset(ds_importer.noninteractiveImport('../src/datasets/Polser.txt', True, True))
    return dsl

class TestContainer(HasTraits):
    """Main frame for testing method tabs
    """
    test_subject = Instance(HasTraits)
    dsl = Instance(DatasetCollection)

    def _dsl_default(self):
        return make_dsl_mock()

    def _test_subject_changed(self, old, new):
        if old is not None:
            old.main_ui_ptr = None
        if new is not None:
            new.main_ui_ptr = self


if __name__== '__main__':
    container = TestContainer()
