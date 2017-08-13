'''DataSet tests
'''

import pytest
import numpy as np
import pandas as pd

# Test subject
import dataset as mx


@pytest.fixture
def a_df(request):
    '''Makes a simple DataFrame'''
    shape = (3, 4)
    df = pd.DataFrame(
        np.random.randn(*shape),
        index=["O{}".format(i+1) for i in range(shape[0])],
        columns=["v{}".format(j+1) for j in range(shape[1])])
    return df


def test_ds_unique_id(w2err):
    ds1 = mx.DataSet()
    ds2 = mx.DataSet()
    assert isinstance(ds1.id, str)
    assert ds1.id != ds2.id


def test_missing_data(w2err):
    td = pd.DataFrame([[1, 2, np.nan], [4, 5, 6]])
    ds_missing = mx.DataSet(mat=td)
    td = pd.DataFrame([[1, 2, 3], [4, 5, 6]])
    ds_complete = mx.DataSet(mat=td)
    assert ds_missing.missing_data
    assert not ds_complete.missing_data


def test_shape(w2err, a_df):
    ds = mx.DataSet(mat=a_df)
    assert isinstance(ds.var_n, list) and isinstance(ds.obj_n, list)
    assert len(ds.var_n) == ds.n_vars and len(ds.obj_n) == ds.n_objs


def test_get_ndarray(w2err, a_df):
    ds = mx.DataSet(mat=a_df)
    assert isinstance(ds.values, np.ndarray)


def test_factor(a_df):
    fac = mx.Factor('Aldersgruppe')
    fac.add_level(mx.Level([0,1,2,3], 'tor'), check_idx="no")

    with pytest.raises(ValueError):
        fac.add_level(mx.Level([], 'tor'), check_idx="no")
    assert len(fac) == 1

    fac.add_level(mx.Level([2,3,4,5], 'petter'), check_idx="toss_overlaping")
    assert len(fac.get_idx('petter')) == 2


# Test data set with missing data
# To read an matrix with discrete number shoud result
# in dtype=int but nan is defined as an float
# So columns with missing data is casted to float data
# Test for expected and desired behaviour but mark test
# as expected to fail
@pytest.mark.xfail
def test_nan_dtype(discrete_nans_ds, discrete_ds):
    equal_q = discrete_nans_ds.mat.dtypes == discrete_ds.mat.dtypes
    assert np.all(equal_q)
