
import os
import sys
import logging

# Enthought imports
# from enthought.etsconfig.api import ETSConfig
# ETSConfig.toolkit = 'wx'
# ETSConfig.toolkit = 'qt4'
from enthought.traits.api import HasTraits, Instance

def setConsumerCheckIncludePath():
    consumerBase = findApplicationBasePath()
#     consumerBase = '..'
    addLoadPath(consumerBase)

def findApplicationBasePath():
    basePath = __file__
    while os.path.basename(basePath) != 'tests':
        basePath = os.path.dirname(basePath)
    basePath = os.path.dirname(basePath)
    return basePath

def addLoadPath(baseFolderPath):
    sys.path.append(baseFolderPath)

logging.basicConfig(level=logging.DEBUG)
logging.info('Starts testing')

setConsumerCheckIncludePath()

from dataset_collection import DatasetCollection
from dataset import DataSet
from file_importer import FileImporter


def make_dsl_mock():
    dsl = DatasetCollection()
    ds_importer = FileImporter()
    dsl.addDataset(ds_importer.noninteractiveImport('datasets/Ost.txt'))
    dsl.addDataset(ds_importer.noninteractiveImport('datasets/Polser.txt', True, True))
    dsl.addDataset(ds_importer.noninteractiveImport('datasets/A_labels.txt'))
    dsl.addDataset(ds_importer.noninteractiveImport('datasets/C_labels.txt'))
    dsl.addDataset(ds_importer.noninteractiveImport('datasets/Ost_forbruker.txt'))
    dsl.addDataset(ds_importer.noninteractiveImport('datasets/Ost_sensorikk.txt'))
    dsl._dataDict['a_labels']._ds_name = 'Set A tull'
    dsl._dataDict['c_labels']._ds_name = 'Set C tull'
    dsl._dataDict['a_labels']._dataset_type = 'Consumer liking'
    dsl._dataDict['c_labels']._dataset_type = 'Sensory profiling'
    dsl._dataDict['ost_forbruker']._ds_name = 'Forbruker'
    dsl._dataDict['ost_forbruker']._dataset_type = 'Consumer liking'
    dsl._dataDict['ost_sensorikk']._ds_name = 'Sensorikk'
    dsl._dataDict['ost_sensorikk']._dataset_type = 'Sensory profiling'
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
            if hasattr(old, 'main_ui_ptr'):
                old.main_ui_ptr = None
        if new is not None:
            if hasattr(new, 'main_ui_ptr'):
                new.main_ui_ptr = self


if __name__== '__main__':
    container = TestContainer()
