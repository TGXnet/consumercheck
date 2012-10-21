# Per directory py.test helper functions

import pytest

# Std lib imports
import logging
# Configure logging
logging.basicConfig(leve=logging.INFO)
logging.info("Test start")

import numpy as np
# from os.path import dirname, abspath, join
import os.path as osp


@pytest.fixture
def check_trait_interface():
    import traits.has_traits
    # 0: no check, 1: log warings, 2: error
    traits.has_traits.CHECK_INTERFACES = 1


# @pytest.fixture(params=['wx', 'qt'])
# def ets_gui_toolkit(request):
#     from traits.etsconfig.api import ETSConfig
#     ETSConfig.toolkit = request.param


@pytest.fixture
def gui_qt():
    from traits.etsconfig.api import ETSConfig
    ETSConfig.toolkit = 'qt'


@pytest.fixture
def gui_wx():
    from traits.etsconfig.api import ETSConfig
    ETSConfig.toolkit = 'wx'


from traits.api import HasTraits, Instance, Bool, Event, on_trait_change

# Local imports
from dataset import DataSet
from plot_pc_scatter import PCScatterPlot
from dataset_collection import DatasetCollection
from importer_main import ImporterMain


@pytest.fixture
def tdd():
    '''Test data dir (tdd)'''
    here = osp.dirname(__file__)
    basedir = osp.dirname(here)
    return osp.join(basedir, 'datasets')


@pytest.fixture
def dsc_mock(tdd):
    '''Data set container/collection mock'''
    dsl = DatasetCollection()
    importer = ImporterMain()
    tdd = get_test_ds_path()
    dsl.add_dataset(importer.import_data(osp.join(tdd, 'Vine', 'A_labels.txt')))
    dsl._datasets['a_labels']._ds_name = 'Set A tull'
    dsl._datasets['a_labels']._dataset_type = 'Consumer liking'
    dsl.add_dataset(importer.import_data(osp.join(tdd, 'Vine', 'C_labels.txt')))
    dsl._datasets['c_labels']._ds_name = 'Set C tull'
    dsl._datasets['c_labels']._dataset_type = 'Sensory profiling'
    dsl.add_dataset(importer.import_data(osp.join(tdd, 'Cheese', 'ConsumerLiking.txt')))
    dsl._datasets['consumerliking']._ds_name = 'Forbruker'
    dsl._datasets['consumerliking']._dataset_type = 'Consumer liking'
    dsl.add_dataset(importer.import_data(osp.join(tdd, 'Cheese', 'SensoryData.txt')))
    dsl._datasets['sensorydata']._ds_name = 'Sensorikk'
    dsl._datasets['sensorydata']._dataset_type = 'Sensory profiling'

    # Conjoint test data
    dsl.add_dataset(importer.import_data(
        osp.join(tdd, 'Conjoint', 'design.txt')))
    dsl._datasets['design']._ds_name = 'Conjoint design'
    dsl._datasets['design']._dataset_type = 'Design variable'

    dsl.add_dataset(importer.import_data(
        osp.join(tdd, 'Conjoint', 'consumerAttributes.txt')))
    dsl._datasets['consumerattributes']._ds_name = 'Consumer Attributes'
    dsl._datasets['consumerattributes']._dataset_type = 'Consumer attributes'

    dsl.add_dataset(importer.import_data(
        osp.join(tdd, 'Conjoint', 'odour-flavour_liking.txt')))
    dsl._datasets['odour-flavour_liking']._ds_name = 'Odour flavor liking'
    dsl._datasets['odour-flavour_liking']._dataset_type = 'Consumer liking'

    dsl.add_dataset(importer.import_data(
        osp.join(tdd, 'Conjoint', 'consistency_liking.txt')))
    dsl._datasets['consistency_liking']._ds_name = 'Consistency liking'
    dsl._datasets['consistency_liking']._dataset_type = 'Consumer liking'

    dsl.add_dataset(importer.import_data(
        osp.join(tdd, 'Conjoint', 'overall_liking.txt')))
    dsl._datasets['overall_liking']._ds_name = 'Overall liking'
    dsl._datasets['overall_liking']._dataset_type = 'Consumer liking'

    return dsl


def make_ds_mock():
    importer = ImporterMain()
    tdd = get_test_ds_path()
    ds = importer.import_data(osp.join(tdd, 'Data_1', 'Data_1_liking.xlsx'))
    return ds


def make_non_ascii_ds_mock():
    importer = ImporterMain()
    tdd = get_test_ds_path()
    ds = importer.import_data(osp.join(tdd, 'Polser_data_nordisk.xls'))
    return ds


class TestContainer(HasTraits):
    """Main frame for testing method tabs
    """
    test_subject = Instance(HasTraits)
    dsl = Instance(DatasetCollection)
    ds_event = Event()
    dsname_event = Event()
    en_advanced = Bool(True)

    def _dsl_default(self):
        return dsc_mock()

    def _test_subject_changed(self, old, new):
        if old is not None:
            if hasattr(old, 'mother_ref'):
                old.mother_ref = None
        if new is not None:
            if hasattr(new, 'mother_ref'):
                new.mother_ref = self


    # @on_trait_change('dsl', post_init=True)
    @on_trait_change('dsl')
    def _dsl_updated(self, obj, name, new):
        print("main: dsl changed")
        self.ds_event = True


    ## @on_trait_change('')
    ## def _ds_name_updated(self, obj, name, new):
    ##     print("main: ds name changed")
    ##     self.dsname_event = True



def pytest_funcarg__test_container(request):
    return TestContainer()



def pytest_funcarg__simple_plot(request):
    """Yield a simple plot for testing plot windows"""
    set1 = np.array([
        [-0.3, 0.4, 0.9],
        [-0.1, 0.2, 0.7],
        [-0.1, 0.3, 0.1],
        [0.1, 0.2, 0.1],
        ])
    label1 = ['s1pt1', 's1pt2', 's1pt3', 's1pt4']
    expl_vars = [37.34, 9.4, 0.3498]
    color = (0.7, 0.9, 0.4, 1.0)
    sp = PCScatterPlot(set1, label1, color, expl_vars)
    ## sp.add_PC_set(set1, labels=label1, color=(0.8, 0.2, 0.1, 1.0))

    return sp




# Update to py.test 2.3 funcargs

import pytest

# syntetic ds

# vell know ds from file

# pure random ds

# Data set container/collection
# All datasets
# Related prefmap datasets
# Related Conjoint datasets
# Datasets with vaiable degree of missing data
