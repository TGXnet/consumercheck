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
from importer_text_file import TextFileImporter
from importer_text_previewer import ImportFileParameters


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
        self.tfi = TextFileImporter()

    def test_simple_tab_sep(self):
        ifp = ImportFileParameters(
            file_path='../datasets/Variants/TabSep.txt',
            have_var_names=False,
            have_obj_names=False,
            )
        ds = self.tfi.import_data(ifp)
        assert array_equal(self.ref, ds.matrix)


    def test_comma_decimal_mark(self):
        ifp = ImportFileParameters(
            file_path='../datasets/Variants/CommaDecimalMark.txt',
            decimal_mark='comma',
            have_var_names=False,
            have_obj_names=False,
            )
        ds = self.tfi.import_data(ifp)
        assert array_equal(self.ref, ds.matrix)
