"""Test to be used with py.test

What is the important aspects with dataset to test:
 * Creation of an empty dataset
 * Maintain conistency between number of object and variable names and shape of matrix
 * Active var and objecs = matrix.shap
 * Check that we get expected subset()
 * Find a way to test the reactive (event) aspcet of the dataset
"""

import pytest
from numpy import array, array_equal, allclose

# Local imports
from dataset_ng import DataSet


refa = array(
    [[ 1.1, 1.2],
     [ 2.1, 2.2]])


@pytest.fixture
def void_ds():
    return DataSet()


@pytest.fixture
def syntetic_ds():
    ref = array(
        [[ 1.1, 1.2, 1.3],
         [ 2.1, 2.2, 2.3],
         [ 3.1, 3.2, 3.3],
         [ 4.1, 4.2, 4.3]])
    return DataSet(matrix=ref)


# FIXME:
# Functionality to test
# Dataset id uuid, check for uniq id
# ds_type check for expected default type and only allowed types
# var/obj name consistency, is alway read or generated
# n_row/n_cols consistent with row and cols
# Dataset should check consitency and make row/column names
# active/selected var and objects
# test subset()
# Clean api for making consistent DS objet from numpy array



def test_empty_ds(void_ds):
    from traits.api import TraitError
    assert void_ds.n_rows == 0
    assert void_ds.n_cols == 0
    assert void_ds.object_names == []
    assert void_ds.variable_names == []
    assert void_ds.ds_type == 'Design variable'
    with pytest.raises(TraitError):
        void_ds.ds_type = 'Tor'


def test_simple_ds(syntetic_ds):
    assert syntetic_ds.n_cols == 3
    assert syntetic_ds.n_rows == 4
    assert len(syntetic_ds.active_variables) == 3
    assert len(syntetic_ds.active_objects) == 4


def test_mod_ds(syntetic_ds):
    assert syntetic_ds.n_rows == 4
    assert len(syntetic_ds.active_objects) == 4
    syntetic_ds.matrix = refa
    assert syntetic_ds.n_rows == 2
    assert len(syntetic_ds.active_objects) == 2


def test_subset_ds(syntetic_ds):
    syntetic_ds.active_objects = [0,1]
    syntetic_ds.active_variables = [0,1]
    out = syntetic_ds.subset()
    assert array_equal(out.matrix, refa)
