
import pytest

from basic_stat_model import BasicStat, BasicStatPlugin, extract_summary, extract_histogram


# Testing one analysis module

def test_discrete(discrete_ds):

    bs = BasicStat(ds=discrete_ds)
    print("\n")
    res = bs.stat_res
    summary = extract_summary(res)
    assert summary.mat.shape == (5, 4)
    assert summary.var_n == ['mean', 'std', 'min', 'max']
    hist = extract_histogram(res)
    assert hist.mat.shape == (5, 11)
    # FIXME: Maybe this should be converted to strings
    assert hist.var_n == range(11)
    assert hist.obj_n == ['O{}'.format(i+1) for i in range(5)]


def test_missing():
    assert False


def test_continous():
    '''Not needed by now'''
    assert True



# Testing the plugin
