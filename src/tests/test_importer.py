"""Test to be used with py.test.
"""

# Stdlib imports
import pytest
from os.path import join
from numpy import array, array_equal, allclose

# Local imports
from importer_text_file import ImporterTextFile
from importer_main import ImporterMain


@pytest.fixture
def ref():
    class RefData(object):
        def __init__(self):
            self.arr = array(
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
            self.obj_names = ['O1', 'O2', 'O3', 'O4', 'O5', 'O6',
                              'O7', 'O8', 'O9', 'O10', 'O11', 'O12']
            self.varn_utf8 = [u'\xf8re1', u'\xe5re2', u'\xe6re3',
                              u'\xf8re4', u'\xe5re5']
            self.objn_utf8 = [u'\xc61', u'\xd82', u'\xc53', u'O4', u'O5', u'O6',
                              u'O7', u'O8', u'O9', u'O10', u'O11', u'O12']

    return RefData()



class TestTextfileImport(object):

    def test_simple_tab_sep(self, tdd, ref):
        ifp = ImporterTextFile(
            file_path=join(tdd, 'Variants', 'TabSep.txt'),
            have_var_names=False,
            have_obj_names=False,
            )
        ds = ifp.import_data()
        assert array_equal(ref.arr, ds.matrix)


    def test_comma_decimal_mark(self, tdd, ref):
        ifp = ImporterTextFile(
            file_path=join(tdd, 'Variants', 'CommaDecimalMark.txt'),
            decimal_mark='comma',
            have_var_names=False,
            have_obj_names=False,
            )
        ds = ifp.import_data()
        assert array_equal(ref.arr, ds.matrix)


    def test_var_names(self, tdd, ref):
        ifp = ImporterTextFile(
            file_path=join(tdd, 'Variants', 'VariableNames.txt'),
            have_var_names=True,
            have_obj_names=False,
            )
        ds = ifp.import_data()
        assert array_equal(ref.arr, ds.matrix)
        assert ref.var_names == ds.variable_names


    def test_obj_var_names(self, tdd, ref):
        ifp = ImporterTextFile(
            file_path=join(tdd, 'Variants', 'ObjVarNames.txt'),
            have_var_names=True,
            have_obj_names=True,
            )
        ds = ifp.import_data()
        assert array_equal(ref.arr, ds.matrix)
        assert ref.var_names == ds.variable_names
        assert ref.obj_names == ds.object_names


    def test_csv_empty_corner(self, tdd, ref):
        ifp = ImporterTextFile(
            file_path=join(tdd, 'Variants', 'CommaSeparated.csv'),
            separator=',',
            have_var_names=True,
            have_obj_names=True,
            )
        ds = ifp.import_data()
        assert array_equal(ref.arr, ds.matrix)
        assert ref.var_names == ds.variable_names
        assert ref.obj_names == ds.object_names


    def test_utf8_text(self, tdd, ref):
        ifp = ImporterTextFile(
            file_path=join(tdd, 'Variants', 'Names_UTF-8.txt'),
            char_encoding='utf_8',
            have_var_names=True,
            have_obj_names=True,
            )
        ds = ifp.import_data()
        assert array_equal(ref.arr, ds.matrix)
        assert ds.variable_names == ref.varn_utf8
        assert ds.object_names == ref.objn_utf8


    def test_latin1_text(self, tdd,ref):
        ifp = ImporterTextFile(
            file_path=join(tdd, 'Variants', 'Names_iso-8859-1.txt'),
            char_encoding='latin_1',
            have_var_names=True,
            have_obj_names=True,
            )
        ds = ifp.import_data()
        assert array_equal(ref.arr, ds.matrix)
        assert ds.variable_names == ref.varn_utf8
        assert ds.object_names == ref.objn_utf8


@pytest.mark.ui
def test_ui_import(tdd):
    di = ImporterMain()
    dsl = di.dialog_multi_import()
    for ds in dsl:
        ds.print_traits()


def test_add_name(tdd):
    file_path=join(tdd, 'test_number.txt')
    di = ImporterMain()
    ds = di.import_data(file_path, False, False)
    assert ds.n_cols == len(ds.variable_names)
    assert ds.n_rows == len(ds.object_names)
