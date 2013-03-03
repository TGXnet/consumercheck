# Per directory py.test helper functions
'''
# FIXME: Update to py.test 2.3 funcargs
# syntetic ds
# vell know ds from file
# pure random ds
# Data set container/collection
# All datasets
# Related prefmap datasets
# Related Conjoint datasets
# Datasets with vaiable degree of missing data
'''
import pytest

# Std lib imports
import copy
import logging

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    # level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    # datefmt='%m-%d %H:%M',
    datefmt='%y%m%dT%H:%M:%S',
    # filename='/temp/myapp.log',
    # filemode='w',
    )
logging.info("Test start")

import numpy as np
import pandas as pd
import os.path as osp


@pytest.fixture
def check_trait_interface():
    import traits.has_traits
    # 0: no check, 1: log warings, 2: error
    traits.has_traits.CHECK_INTERFACES = 1


# Local imports
from dataset_ng import DataSet
from dataset_container import DatasetContainer
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
    ('Conjoint', 'design.txt', 'Tine yogurt design', 'Design variable'),
    ('Conjoint', 'consumerAttributes.txt', 'Consumers', 'Consumer characteristics'),
    ('Conjoint', 'overall_liking.txt', 'Overall', 'Consumer liking'),
    ('Conjoint', 'odour-flavour_liking.txt', 'Odour-flavor', 'Consumer liking'),
    ('Conjoint', 'consistency_liking.txt', 'Consistency', 'Consumer liking'),
    ('BarleyBread', 'BB_design.txt', 'Barley bread design', 'Design variable'),
    ('BarleyBread', 'BB_E_consAttr.txt', 'Estland consumers', 'Consumer characteristics'),
    ('BarleyBread', 'BB_E_liking.txt', 'Estland liking data', 'Consumer liking'),
    ('HamData', 'Ham_consumer_attributes.txt', 'Ham-cons char.', 'Consumer characteristics'),
    ('HamData', 'Ham_consumer_liking.txt', 'Ham-liking', 'Consumer liking'),
    ('HamData', 'Ham_design.txt', 'Ham-design', 'Design variable'),
    ]


VINE = [
    ('Vine', 'A_labels.txt', 'Vine set A', 'Consumer liking'),
    ('Vine', 'B_labels.txt', 'Vine set B', 'Consumer liking'),
    ('Vine', 'C_labels.txt', 'Vine set C', 'Consumer liking'),
    ('Vine', 'D_labels.txt', 'Vine set D', 'Consumer liking'),
    ('Vine', 'E_labels.txt', 'Vine set E', 'Consumer liking'),
    ]


CHEESE = [
    ('Cheese', 'ConsumerLiking.txt', 'Cheese liking', 'Consumer liking'),
    ('Cheese', 'ConsumerValues.txt', 'Consumer info', 'Consumer characteristics'),
    ('Cheese', 'SensoryData.txt', 'Sensory profiling', 'Sensory profiling'),
    ]


# Create datasets

@pytest.fixture
def simple_ds():
    '''Makes a simple syntetic dataset'''

    ds = DataSet(display_name='Some values')
    ds.mat = pd.DataFrame(
        [[1.1, 1.2, 1.3],
         [2.1, 2.2, 2.3],
         [3.1, 3.2, 3.3]],
        index = ['O1', 'O2', 'O3'],
        columns = ['V1', 'V2', 'V3'])

    return ds


discrete_nl = [
    [3, 5, 7, 8, 1, 9, 7, 3],
    [1, 8, 2, 5, 5, 2, 7, 5],
    [2, 1, 2, 5, 6, 3, 9, 6],
    [8, 4, 8, 4, 8, 1, 2, 4],
    [6, 5, 3, 7, 6, 9, 2, 2]]


@pytest.fixture
def discrete_ds():
    '''Make a dataset with discrete walues'''

    ds = DataSet(display_name='Discrete values')
    idxn = ['O'+str(i+1) for i in range(5)]
    coln = ['V'+str(j+1) for j in range(8)]
    ds.mat = pd.DataFrame(discrete_nl, index = idxn, columns = coln)
    return ds


@pytest.fixture
def discrete_nans_ds():
    '''Make a dataset with discrete walues'''

    missing = copy.deepcopy(discrete_nl)
    missing[1][6:8] = [np.nan for i in range(2)]
    missing[2][6:8] = [np.nan for i in range(2)]
    missing[3][0:8:3] = [np.nan for i in range(3)]
    missing[4][1:8:3] = [np.nan for i in range(3)]

    ds = DataSet(display_name='Discrete values')
    idxn = ['O'+str(i+1) for i in range(5)]
    coln = ['V'+str(j+1) for j in range(8)]
    ds.mat = pd.DataFrame(missing, index = idxn, columns = coln)

    # This does not work by now
    # When i set integer type to nan, a large value is inserted
    ## ds = discrete_ds()
    ## ds.display_name = 'Discrete values, some missing'
    ## ds.mat.ix['O2':'O3','V5':'V7'] = np.nan
    ## ds.mat.ix['O4','V1':'V8':2] = np.nan
    ## ds.mat.ix['O5','V2':'V8':2] = np.nan
    return ds


@pytest.fixture
def hist_ds():
    '''Make dataset for histograms'''
    rows_cols = (12, 45)
    random = False

    if random:
        norm = np.random.normal(loc=5.0, scale=2.0, size=rows_cols)
        normi = norm.astype('int')
        end = normi.max()
        hl = []
        for row in normi:
            hl.append(list(np.bincount(row, minlength=end+1)))
    else:
        hl = [[ 0,  3,  5,  8,  9,  5,  5,  8,  0,  2,],
              [ 1,  3,  6,  6, 11,  7,  5,  4,  2,  0,],
              [ 1,  2,  2,  9,  8,  8,  7,  6,  1,  1,],
              [ 0,  1,  7,  8, 12,  3,  4,  7,  2,  1,],
              [ 0,  2,  2,  4,  5, 13, 10,  6,  1,  2,],
              [ 0,  4,  6,  3, 15,  8,  6,  1,  2,  0,],
              [ 1,  2,  5, 10,  4, 11,  6,  5,  1,  0,],
              [ 1,  3,  1, 11, 10,  9,  8,  0,  0,  2,],
              [ 1,  2,  4, 10, 11,  3,  3, 10,  1,  0,],
              [ 2,  3,  3,  5, 10,  8,  4,  5,  3,  2,],
              [ 1,  1,  4,  8,  7,  9,  9,  3,  1,  2,],
              [ 1,  2,  6,  8,  4, 10,  6,  3,  4,  1,],]

    rown = ["O{}".format(i+1) for i in range(rows_cols[0])]
    hdf = pd.DataFrame(hl, index=rown)
    return DataSet(mat=hdf, display_name="Test histogram")


@pytest.fixture
def boxplot_ds():
    '''Make dataset for testing box plot'''
    rows_cols = (12, 45)
    random = False
    rown = ["O{}".format(i+1) for i in range(rows_cols[0])]

    if random:
        norm = np.random.normal(loc=5.0, scale=2.0, size=rows_cols)
        normi = norm.astype('int')
        stat = pd.DataFrame(index=rown)
        stat['mean'] = normi.mean(axis=1)
        stat['std'] = normi.std(axis=1)
        stat['max'] = normi.max(axis=1)
        stat['min'] = normi.min(axis=1)
    else:
        stat = pd.DataFrame(
            data=[[4.733333, 2.184796, 10, 1],
                  [4.533333, 1.961859, 9, 1],
                  [4.844444, 1.685962, 9, 2],
                  [4.422222, 1.960600, 8, 1],
                  [4.711111, 2.146027, 9, 0],
                  [4.511111, 1.927834, 9, 0],
                  [4.577778, 1.971901, 10, 1],
                  [4.800000, 1.571977, 8, 1],
                  [3.822222, 1.980896, 9, 0],
                  [4.133333, 2.295890, 10, 0],
                  [4.444444, 1.880373, 10, 1],
                  [4.244444, 1.863754, 9, 0]],
            index=rown,
            columns=['mean', 'std', 'max', 'min'])

    return DataSet(mat=stat, display_name="Test box plot")



@pytest.fixture
def iris_ds():
    '''Return the Iris dataset

    http://archive.ics.uci.edu/ml/datasets/Iris
    '''
    home = tdd()
    importer = ImporterMain()
    iris_url = osp.join(home, 'Iris', 'irisNoClass.data')
    ds = importer.import_data(iris_url, False, False, ',')
    return ds



@pytest.fixture
def synth_dsc():
    dsc = DatasetContainer()
    dsc.add(simple_ds(), discrete_ds(), iris_ds())
    return dsc


# Read datasets from files

@pytest.fixture(scope="module")
def conjoint_dsc():
    '''Get Conjoint std. test datasets '''
    dsc = DatasetContainer()

    for mi in CONJOINT:
        dsc.add(imp_ds(mi))

    return dsc


@pytest.fixture(scope="module")
def prefmap_dsc():
    '''Get Conjoint std. test datasets '''
    dsc = DatasetContainer()

    for mi in CHEESE:
        dsc.add(imp_ds(mi))

    return dsc


@pytest.fixture(scope="module")
def all_dsc():
    '''Data set container/collection mock'''
    dsc = DatasetContainer()

    # ad = CONJOINT + VINE + CHEESE
    ad = CHEESE + CONJOINT

    for mi in ad:
        dsc.add(imp_ds(mi))
    dsc.add(discrete_ds())

    return dsc


def imp_ds(ds_meta_info):
    folder, file_name, ds_name, ds_type = ds_meta_info
    importer = ImporterMain()
    home = tdd()
    ds_url = osp.join(home, folder, file_name)
    ds = importer.import_data(ds_url)
    ds.display_name = ds_name
    ds.ds_type = ds_type
    return ds


@pytest.fixture
def conj_res():
    import pickle

    # Filename for result cache file
    cache_fn = 'conj_cached.pkl'

    try:
        fp = open(cache_fn, 'r')
        print("Read result data from: {0}.".format(cache_fn))
        res = pickle.load(fp)
        fp.close()
    except IOError:
        print("Cache file ({0}) not found".format(cache_fn))

        from conjoint_machine import ConjointMachine
        dsc = conjoint_dsc()
        consAttr = dsc.get_by_id('consumerattributes')
        odflLike = dsc.get_by_id('odour-flavour_liking')
        consistencyLike = dsc.get_by_id('consistency_liking')
        overallLike = dsc.get_by_id('overall_liking')
        designVar = dsc.get_by_id('design')
        selected_structure = 2
        selected_consAttr = ['Sex']
        selected_designVar = ['Flavour', 'Sugarlevel']
        consLiking = odflLike

        cm = ConjointMachine()
        res = cm.synchronous_calculation(selected_structure,
                                     consAttr, selected_consAttr,
                                     designVar, selected_designVar,
                                     consLiking)

        with open(cache_fn, 'w') as fp:
            pickle.dump(res, fp)

    return res



@pytest.fixture
def plugin_mother_mock():
    from traits.api import HasTraits, Instance, Bool, Event, on_trait_change

    class PluginMotherMock(HasTraits):
        """Main frame for testing method tabs
        """
        test_subject = Instance(HasTraits)
        dsl = Instance(DatasetContainer)
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


        @on_trait_change('dsl')
        def _dsl_updated(self, obj, name, new):
            print("main: dsl changed")
            self.ds_event = True

    
    return PluginMotherMock()


## More ideas
'''
# Taken fra a PyConAU presentation
# http://www.youtube.com/watch?v=DTNejE9EraI
# Examples
# https://github.com/lunaryorn/pyudev/blob/develop/tests
# skip examples
import sys

win32only = pytest.mark.skipif("sys.platform != 'win32'")

@win32only
def test_foo():
    pass

# Example markers
@py.test.mark.slow
@py.test.mark.dstAffected
@py.test.mark.trac1543 # Refere to Trac bug ticket
@py.test.mark.flaky
@py.test.mark.unicode
@py.test.mark.regression

# test expected to fail
@py.test.mark.xfail(reason='This is a bad idea')
def test_foo4():
    assert False


# parameterize testing
# ex to increate the ratio of missing data in a matrix

# monkeypatching - can be problematic

# funcargs - dependency injection
# https://github.com/lunaryorn/pyudev/blob/develop/tests/test_libudev.py

# Where shoud this code go to enable this
def pytest_addoption(parser):
    # pytest hook that adds a GFE specific option.

    # Add options.
    group = parser.getgroup('graphical forecast editor options')
    group.addoption('--winpdb', dest='usewinpdb', action='store_true', default=False,
                    help=('start the WinPDB Python debugger before calling each test function.'
                          'Suggest only using this with a single test at a time (i.e. -k .'))


def pytest_configure(config):
    # Only do these if this process is the master.
    if not hasattr(config, 'slaveinput'):
        config.pluginmanager.register(WinPdbInvoke(), 'winpdb')


class WinPdbInvoke(object):

    def __init__(self):
        print("initialising winpdb invoker")

    def pytest_pyfunc_call(self, pyfuncitem):
        import rpdb2
        rpdb2.start_embedded_debugger('0')


# Suggestion for how to simulate a user in testing

import time
import threading

from test_ui import MyClass, MyController

class MocAsyncTestUser(threading.Thread):

    def __init__(self, app):
        super(MocAsyncTestUser, self).__init__()
        self.ts = app
        self.in_test = True


    def run(self):
        while(self.in_test):
            time.sleep(5)
            self.ts.open_button = True
            time.sleep(1,7)
            for win in ts.uis:
                win.dispose()


ts = MyController(MyClass())
tu = MocAsyncTestUser(ts)
tu.start()
ts.configure_traits()

'''
