"""Test to be used with py.test

What is the important aspects with dataset to test:
 * Creation of an empty dataset
 * Maintain conistency between number of object and variable names and shape of matrix
 * Active var and objecs = matrix.shap
 * Check that we get expected subset()
"""

import pytest
from numpy import array, array_equal, allclose

# Local imports
from dataset import DataSet


ref = array(
    [[ 1.1, 1.2, 1.3],
     [ 2.1, 2.2, 2.3],
     [ 3.1, 3.2, 3.3],
     [ 4.1, 4.2, 4.3]])

refa = array(
    [[ 1.1, 1.2],
     [ 2.1, 2.2]])


def test_empty_ds():
    ds = DataSet()
    assert ds.n_rows == 0
    assert ds.n_cols == 0


def test_simple_ds():
    ds = DataSet(matrix=ref)
    assert ds.n_cols == 3
    assert ds.n_rows == 4
    assert len(ds.active_variables) == 3
    assert len(ds.active_objects) == 4


def test_mod_ds():
    ds = DataSet(matrix=ref)
    assert ds.n_rows == 4
    assert len(ds.active_objects) == 4
    ds.matrix = refa
    assert ds.n_rows == 2
    assert len(ds.active_objects) == 2


def test_subset_ds():
    ds = DataSet(matrix=ref)
    ds.active_objects = [0,1]
    ds.active_variables = [0,1]
    out = ds.subset()
    assert array_equal(out.matrix, refa)
