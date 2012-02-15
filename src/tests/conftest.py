# Per directory py.test helper functions
# More info about this file her:
# http://pytest.org/latest/funcargs.html
# 
# Example functions for this file
# Argument parsers
# Provider of various objects
# ds, dsl, mock-mother

# Std lib imports
import logging
# Configure logging
logging.basicConfig(leve=logging.INFO)
logging.info("Test start")

import numpy as np
# from os.path import dirname, abspath, join
import os.path as osp

# Enthought Toolkit imports
import traits.has_traits
# 0: no check, 1: log warings, 2: error
traits.has_traits.CHECK_INTERFACES = 1
from traits.api import HasTraits, Instance

# Local imports
from dataset import DataSet
from plot_pc_scatter import PCScatterPlot
from dataset_collection import DatasetCollection
from importer_main import ImporterMain


## def pytest_runtest_setup(item):
##     print("hook in conftest: setting up", item)


def pytest_funcarg__ds(request):
    """Provides a dataset object"""
    return DataSet()


def get_test_ds_path():
    here = osp.dirname(__file__)
    basedir = osp.dirname(here)
    return osp.join(basedir, 'datasets')


def pytest_funcarg__test_ds_dir(request):
    """Yield a path to the test data directory"""
    return get_test_ds_path()


def pytest_funcarg__simple_plot(request):
    """Yield a simple plot for testing plot windows"""
    set1 = np.array([
        [-0.3, 0.4, 0.9],
        [-0.1, 0.2, 0.7],
        [-0.1, 0.3, 0.1],
        [0.1, 0.2, 0.1],
        ])
    label1 = ['s1pt1', 's1pt2', 's1pt3', 's1pt4']
    expl_vars = {1:37.34, 2:9.4, 3:0.3498}
    color = (0.7, 0.9, 0.4, 1.0)
    sp = PCScatterPlot(set1, label1, color, expl_vars)
    ## sp.add_PC_set(set1, labels=label1, color=(0.8, 0.2, 0.1, 1.0))

    return sp


def make_dsl_mock():
    dsl = DatasetCollection()
    importer = ImporterMain()
    tdd = get_test_ds_path()
#    dsl.add_dataset(importer.import_data('datasets/CheeseSensoryData.txt'))
#    dsl.add_dataset(importer.import_data('datasets/SausageSensoryData.txt', True, True))
    dsl.add_dataset(importer.import_data(osp.join(tdd, 'Vine', 'A_labels.txt')))
    dsl.add_dataset(importer.import_data(osp.join(tdd, 'Vine', 'C_labels.txt')))
    dsl.add_dataset(importer.import_data(osp.join(tdd, 'Cheese', 'ConsumerLiking.txt')))
    dsl.add_dataset(importer.import_data(osp.join(tdd, 'Cheese', 'SensoryData.txt')))
    dsl._datasets['a_labels']._ds_name = 'Set A tull'
    dsl._datasets['c_labels']._ds_name = 'Set C tull'
    dsl._datasets['a_labels']._dataset_type = 'Consumer liking'
    dsl._datasets['c_labels']._dataset_type = 'Sensory profiling'
    dsl._datasets['consumerliking']._ds_name = 'Forbruker'
    dsl._datasets['consumerliking']._dataset_type = 'Consumer liking'
    dsl._datasets['sensorydata']._ds_name = 'Sensorikk'
    dsl._datasets['sensorydata']._dataset_type = 'Sensory profiling'
    return dsl


def pytest_funcarg__dsl_data(request):
    """Makes a test dataset collection"""
    return make_dsl_mock()


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


def pytest_funcarg__test_container(request):
    return TestContainer()
