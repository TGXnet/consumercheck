'''DataSet tests

What to test:
 * Unique datast id
 * Empty dataset
 * Has missing data
'''

import pytest
import warnings
import numpy as np
import pandas as pd

from dataset import DataSet


@pytest.fixture
def w2err(request):
    '''Turn warnings into errors'''
    warnings.simplefilter('error')
    request.addfinalizer(lambda *args: warnings.resetwarnings())


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
    ds1 = DataSet()
    ds2 = DataSet()
    assert isinstance(ds1.id, str)
    assert ds1.id != ds2.id


def test_missing_data(w2err):
    td = pd.DataFrame([[1, 2, np.nan], [4, 5, 6]])
    ds_missing = DataSet(mat=td)
    td = pd.DataFrame([[1, 2, 3], [4, 5, 6]])
    ds_complete = DataSet(mat=td)
    assert ds_missing.missing_data
    assert not ds_complete.missing_data


def test_shape(w2err, a_df):
    ds = DataSet(mat=a_df)
    assert isinstance(ds.var_n, list) and isinstance(ds.obj_n, list)
    assert len(ds.var_n) == ds.n_vars and len(ds.obj_n) == ds.n_objs


def test_get_ndarray(w2err, a_df):
    ds = DataSet(mat=a_df)
    assert isinstance(ds.values, np.ndarray)


def test_deprecation_varnings(w2err, a_df):
    ds = DataSet(mat=a_df)
    with pytest.raises(DeprecationWarning):
        dtest = DataSet(matrix=a_df)
    with pytest.raises(DeprecationWarning):
        arr = ds.matrix
    with pytest.raises(DeprecationWarning):
        cols = ds.n_cols
    with pytest.raises(DeprecationWarning):
        rows = ds.n_rows
    with pytest.raises(DeprecationWarning):
        vn = ds.variable_names
    with pytest.raises(DeprecationWarning):
        on = ds.object_names


# Test dataset with missing data
# To read an matrix with discrete number shoud result
# in dtype=int but nan is defined as an float
# So columns with missing data is casted to float data
# Test for expected and desired behaviour but mark test
# as expected to fail
@pytest.mark.xfail
def test_nan_dtype(discrete_nans_ds, discrete_ds):
    equal_q = discrete_nans_ds.mat.dtypes == discrete_ds.mat.dtypes
    assert np.all(equal_q)
