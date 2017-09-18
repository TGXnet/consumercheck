"""Dummify test

Test: Empty dataframe, int, char, string, exception
"""
import pytest
import warnings
import pandas as pd

from dataset import DataSet
from dummify import dummify


@pytest.fixture
def testdata():
    td = DataSet(display_name='Some values', kind='Consumer characteristics')
    td.mat = pd.DataFrame(
        [[1, 'M', 'Good'],
         [2, 'F', 'Poor'],
         [1, 'M', 'Alive'],
         [2, 'F', 'Good']],
        index = ['V1', 'V2', 'V3', 'V4'],
        columns = ['AgeGr', 'Sex', 'Health'])
    return td


def test_en(testdata):
    res = dummify(testdata, ['AgeGr', 'Sex', 'Health'])
    assert len(res.mat.columns) == 7
    assert len(res.mat.index) == 4
