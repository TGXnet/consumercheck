
import pytest

from basic_stat_model import BasicStat, BasicStatPlugin, extract_summary, extract_histogram


# Testing one analysis module

def test_discrete_row_wise(discrete_ds):
    # Row-wise is default
    bs = BasicStat(ds=discrete_ds)
    res = bs.stat_res
    summary = extract_summary(res)
    hist = extract_histogram(res)
    assert summary.var_n == ['mean', 'std', 'min', 'max']
    assert hist.mat.shape == (5, 11)
    assert summary.mat.shape == (5, 4)
    # FIXME: Maybe this should be converted to strings
    assert hist.var_n == range(11)
    assert hist.obj_n == ['O{}'.format(i+1) for i in range(5)]


def test_discrete_column_wise(discrete_ds):
    bs = BasicStat(ds=discrete_ds)
    bs.summary_axis = 'Column-wise'
    res = bs.stat_res
    summary = extract_summary(res)
    hist = extract_histogram(res)
    assert summary.var_n == ['mean', 'std', 'min', 'max']
    assert hist.mat.shape == (8, 11)
    assert summary.mat.shape == (8, 4)
    # FIXME: Maybe this should be converted to strings
    assert hist.var_n == range(11)
    assert hist.obj_n == ['V{}'.format(i+1) for i in range(8)]



def test_missing():
    assert False


def test_continous():
    '''Not needed by now'''
    assert True



# Testing the plugin
