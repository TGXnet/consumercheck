"""Test to be used with py.test.
"""

import sys
from os.path import dirname, abspath
# add directory containing the package to sys.path
# or put it on PYTHONPATH
# or put a appropriate *.pth on PYTHONPATH
home = dirname(dirname(abspath(__file__)))
sys.path.append(home)

from numpy import array, array_equal, allclose

import py

# Local imports
## from importer_text_file import TextFileImporter
## from importer_text_previewer import ImportFileParameters
from dataset import DataSet


class TestTextfileImport(object):

    def setup_method(self, method):
        self.ref = array(
            [[ 1.1, 1.2, 1.3],
             [ 2.1, 2.2, 2.3],
             [ 3.1, 3.2, 3.3]])
        self.ds = DataSet()
        self.ds.matrix = self.ref

    def test_setting_matrix(self):
        assert array_equal(self.ref, self.ds.matrix)

    def test_subset_matrix(self):
        ref = array(
            [[ 1.2, 1.3],
             [ 3.2, 3.3]])
        self.ds.active_variables = [1,2]
        self.ds.active_objects = [0,2]
        subset = self.ds.subset()
        print('\n')
        subset.print_traits()
        print(subset.matrix)
        assert array_equal(ref, subset.matrix)
