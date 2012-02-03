"""Test to be used with py.test.
"""

import pytest
from os.path import join
from numpy import array, array_equal, allclose

# Local imports
from importer_text_file import ImporterTextFile


class TestTextfileImport(object):

    def setup_method(self, method):
        self.ref = array(
            [[ 7.1,   2.7,   4.95,  5.35,  1.,  ],
             [ 6.75,  1.,    4.65,  3.1,   2.6, ],
             [ 6.35,  4.55,  2.65,  1.,    1.,  ],
             [ 6.5,   3.85,  5.,    2.7,   1.3, ],
             [ 6.85,  3.9,   3.75,  2.05,  1.7, ],
             [ 5.5,   2.85,  3.2,   1.45,  1.,  ],
             [ 4.55,  2.15,  1.7,   1.,    1.,  ],
             [ 5.75,  3.5,   3.6,   1.6,   1.,  ],
             [ 6.4,   5.45,  1.4,   1.,    1.,  ],
             [ 4.2,   4.15,  1.45,  2.3,   1.55,],
             [ 4.05,  2.4,   2.25,  1.3,   1.25,],
             [ 4.75,  4.5,   3.5,   2.05,  1.,  ]])
        self.var_names = ['Var1','Var2','Var3','Var4','Var5']
        self.obj_names = ['O1', 'O2', 'O3', 'O4', 'O5', 'O6', 'O7', 'O8', 'O9', 'O10', 'O11', 'O12']

    def test_simple_tab_sep(self, datasets):
        print(datasets)
        ifp = ImporterTextFile(
            file_path=join(datasets, 'Variants', 'TabSep.txt'),
            have_var_names=False,
            have_obj_names=False,
            )
        ds = ifp.import_data()
        assert array_equal(self.ref, ds.matrix)


    def test_comma_decimal_mark(self, datasets):
        ifp = ImporterTextFile(
            file_path=join(datasets, 'Variants', 'CommaDecimalMark.txt'),
            decimal_mark='comma',
            have_var_names=False,
            have_obj_names=False,
            )
        ds = ifp.import_data()
        assert array_equal(self.ref, ds.matrix)


    def test_var_names(self, datasets):
        ifp = ImporterTextFile(
            file_path=join(datasets, 'Variants', 'VariableNames.txt'),
            have_var_names=True,
            have_obj_names=False,
            )
        ds = ifp.import_data()
        assert array_equal(self.ref, ds.matrix)
        assert self.var_names == ds.variable_names


    def test_obj_var_names(self, datasets):
        ifp = ImporterTextFile(
            file_path=join(datasets, 'Variants', 'ObjVarNames.txt'),
            have_var_names=True,
            have_obj_names=True,
            )
        ds = ifp.import_data()
        assert array_equal(self.ref, ds.matrix)
        assert self.var_names == ds.variable_names
        assert self.obj_names == ds.object_names


    def test_csv_empty_corner(self, datasets):
        ifp = ImporterTextFile(
            file_path=join(datasets, 'Variants', 'CommaSeparated.csv'),
            separator=',',
            have_var_names=True,
            have_obj_names=True,
            )
        ds = ifp.import_data()
        assert array_equal(self.ref, ds.matrix)
        assert self.var_names == ds.variable_names
        assert self.obj_names == ds.object_names
