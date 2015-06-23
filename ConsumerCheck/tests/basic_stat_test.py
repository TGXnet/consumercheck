'''Things to test;
 * Test GUI logic for one BasicStat
 * Make basic stat handle continuous values
'''
import pytest

# Local imports
from basic_stat_model import BasicStat
from basic_stat_gui import BasicStatPluginController
from dataset_container import DatasetContainer
from plugin_base import CalcContainer


# Testing one analysis module

@pytest.mark.model
def test_discrete_row_wise(discrete_ds):
    # Row-wise is default
    bs = BasicStat(ds=discrete_ds)
    res = bs.res
    summary = res.summary
    hist = res.hist
    assert summary.var_n == ['min', 'perc25', 'median', 'perc75', 'max']
    assert hist.mat.shape == (5, 9)
    assert summary.mat.shape == (5, 5)
    # FIXME: Maybe this should be converted to strings
    assert hist.var_n == range(1, 10)
    assert hist.obj_n == ['O{}'.format(i+1) for i in range(5)]


@pytest.mark.model
def test_discrete_column_wise(discrete_ds):
    bs = BasicStat(ds=discrete_ds)
    bs.summary_axis = 'Column-wise'
    res = bs.res
    summary = res.summary
    hist = res.hist
    assert summary.var_n == ['min', 'perc25', 'median', 'perc75', 'max']
    assert hist.mat.shape == (8, 9)
    assert summary.mat.shape == (8, 5)
    # FIXME: Maybe this should be converted to strings
    assert hist.var_n == range(1, 10)
    assert hist.obj_n == ['V{}'.format(i+1) for i in range(8)]


@pytest.mark.model
def test_missing(discrete_nans_ds):
    bs = BasicStat(ds=discrete_nans_ds)

    bs.summary_axis = 'Row-wise'
    res = bs.res
    summary = res.summary
    hist = res.hist
    nans = hist.mat['missing']
    assert nans.sum() == 10
    hist_sums = hist.mat.sum(axis=1)
    sane_sum = hist_sums == discrete_nans_ds.n_vars
    assert sane_sum.all()

    bs.summary_axis = 'Column-wise'
    res = bs.res
    summary = res.summary
    hist = res.hist
    nans = hist.mat['missing']
    assert nans.sum() == 10
    hist_sums = hist.mat.sum(axis=1)
    sane_sum = hist_sums == discrete_nans_ds.n_objs
    assert sane_sum.all()


@pytest.mark.model
def test_continous():
    '''Not needed by now'''
    assert True



# Testing the plugin
@pytest.mark.gui
def test_update_propagation(discrete_ds):
    # Assemble object graph
    dsc = DatasetContainer()
    bsp = CalcContainer(dsc=dsc)
    bspc = BasicStatPluginController(bsp)
    # Verify that empty dsc gives empty selection list
    print("Available", bspc.available_ds)
    assert len(bspc.available_ds) == 0
    # Simulate data set added
    dsc.add(discrete_ds)
    # Verify that the added data set i available in the selection list
    print("Available", bspc.available_ds)
    assert len(bspc.available_ds) == 1
    # Simulat that data set i selected for computation
    bspc.selected_ds.append(bspc.available_ds[0][0])
    print("Selected", bspc.selected_ds)
    print("Calculations", bspc.model.calculations)
    # Simulat removal of data set
    del dsc[bspc.available_ds[0][0]]
    # Verify that it is also removed from selection list
    assert len(bspc.available_ds) == 0
