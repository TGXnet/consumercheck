
import os
import sys
import logging

# Enthought imports
# from etsconfig.api import ETSConfig
# ETSConfig.toolkit = 'wx'
# ETSConfig.toolkit = 'qt4'
from traits.api import HasTraits, Instance

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
from importer_main import ImporterMain


def make_dsl_mock():
    dsl = DatasetCollection()
    ds_importer = ImporterMain()
#    dsl.add_dataset(ds_importer.import_data('datasets/CheeseSensoryData.txt'))
#    dsl.add_dataset(ds_importer.import_data('datasets/SausageSensoryData.txt', True, True))
    dsl.add_dataset(ds_importer.import_data('datasets/Vine/A_labels.txt'))
    dsl.add_dataset(ds_importer.import_data('datasets/Vine/C_labels.txt'))
    dsl.add_dataset(ds_importer.import_data('datasets/Cheese/ConsumerLiking.txt'))
    dsl.add_dataset(ds_importer.import_data('datasets/Cheese/SensoryData.txt'))
    dsl._datasets['a_labels']._ds_name = 'Set A tull'
    dsl._datasets['c_labels']._ds_name = 'Set C tull'
    dsl._datasets['a_labels']._dataset_type = 'Consumer liking'
    dsl._datasets['c_labels']._dataset_type = 'Sensory profiling'
    dsl._datasets['consumerliking']._ds_name = 'Forbruker'
    dsl._datasets['consumerliking']._dataset_type = 'Consumer liking'
    dsl._datasets['sensorydata']._ds_name = 'Sensorikk'
    dsl._datasets['sensorydata']._dataset_type = 'Sensory profiling'
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
