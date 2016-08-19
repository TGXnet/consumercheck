'''DataSet tests

What to test:
 * Unique datast id
 * Empty data set
 * Has missing data
'''

import pytest
import warnings
import numpy as np
import pandas as pd

from dataset import DataSet, SubSet, VisualStyle


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


def test_style(a_df):
    ds = DataSet(mat=a_df, style=VisualStyle(fg_color='beige', bg_color=(0.3, 0.7, 0.9, 1.0)))
    ds.style.print_traits()
    assert True


def test_subset(a_df):
    ds = DataSet(mat=a_df)
    sub1 = SubSet(id='tor', name='Test 1',
                  row_selector=[0, 2],
                  col_selector=[1, 2],
                  gr_style=VisualStyle(fg_color='green', bg_color='red'))
    ds.subs.append(sub1)
    print(ds.mat)
    assert True


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
