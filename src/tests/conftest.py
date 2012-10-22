# Per directory py.test helper functions
# FIXME: Update to py.test 2.3 funcargs
# syntetic ds
# vell know ds from file
# pure random ds
# Data set container/collection
# All datasets
# Related prefmap datasets
# Related Conjoint datasets
# Datasets with vaiable degree of missing data

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
from dataset_collection import DatasetCollection
from importer_main import ImporterMain


@pytest.fixture
def tdd():
    '''Test data dir (tdd)'''
    here = osp.dirname(__file__)
    basedir = osp.dirname(here)
    return osp.join(basedir, 'datasets')


# Available test data
# Format: folder, file_name, ds_name, ds_type

CONJOINT = [
    ('Conjoint', 'design.txt', 'Ham design', 'Design variable'),
    ('Conjoint', 'consumerAttributes.txt', 'Consumers', 'Consumer attributes'),
    ('Conjoint', 'overall_liking.txt', 'Overall', 'Consumer liking'),
    ('Conjoint', 'odour-flavour_liking.txt', 'Odour-flavor', 'Consumer liking'),
    ('Conjoint', 'consistency_liking.txt', 'Consistency', 'Consumer liking'),]


VINE = [
    ('Vine', 'A_labels.txt', 'Vine set A', 'Consumer liking'),
    ('Vine', 'B_labels.txt', 'Vine set B', 'Consumer liking'),
    ('Vine', 'C_labels.txt', 'Vine set C', 'Consumer liking'),
    ('Vine', 'D_labels.txt', 'Vine set D', 'Consumer liking'),
    ('Vine', 'E_labels.txt', 'Vine set E', 'Consumer liking'),]


CHEESE = [
    ('Cheese', 'ConsumerLiking.xls', 'Cheese liking', 'Consumer liking'),
    ('Cheese', 'ConsumerValues.xls', 'Consumer info', 'Consumer attributes'),
    ('Cheese', 'SensoryData.xls', 'Sensory profiling', 'Sensory profiling'),]



@pytest.fixture
def iris_ds(tdd):
    '''Return the Iris dataset

    http://archive.ics.uci.edu/ml/datasets/Iris
    '''
    importer = ImporterMain()
    iris_url = osp.join(tdd, 'Iris', 'irisNoClass.data')
    ds = importer.import_data(iris_url, False, False, ',')
    return ds


@pytest.fixture
def conjoint_dsc():
    '''Get Conjoint std. test datasets '''
    dsc = DatasetCollection()

    for mi in CONJOINT:
        dsc.add_dataset(imp_ds(mi))

    return dsc


@pytest.fixture
def all_dsc():
    '''Data set container/collection mock'''
    dsc = DatasetCollection()

    ad = CONJOINT + VINE + CHEESE

    for mi in ad:
        dsc.add_dataset(imp_ds(mi))

    return dsc


def imp_ds(ds_meta_info):
    folder, file_name, ds_name, ds_type = ds_meta_info
    importer = ImporterMain()
    home = tdd()
    ds_url = osp.join(home, folder, file_name)
    ds = importer.import_data(ds_url)
    ds._ds_name = ds_name
    ds._dataset_type = ds_type
    return ds


@pytest.fixture
def plugin_mother_mock():
    return PluginMotherMock()


class PluginMotherMock(HasTraits):
    """Main frame for testing method tabs
    """
    test_subject = Instance(HasTraits)
    dsl = Instance(DatasetCollection)
    ds_event = Event()
    dsname_event = Event()
    en_advanced = Bool(True)

    def _dsl_default(self):
        return all_dsc()

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



# FIXME: Old stuff

def pytest_funcarg__simple_plot(request):
    """Yield a simple plot for testing plot windows"""
    from plot_pc_scatter import PCScatterPlot
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
