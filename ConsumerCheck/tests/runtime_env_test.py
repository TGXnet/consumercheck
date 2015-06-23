
import pytest

# Tools for version checking
# http://pythonhosted.org/distribute/pkg_resources.html
#
# Check for API differences
#
# http://aima.cs.berkeley.edu/python/utils.html
#
# Module version format
# Module Version Numbers
# http://www.python.org/dev/peps/pep-0396/
# Changing the version comparison module in Distutils
# http://www.python.org/dev/peps/pep-0386/
# PEP 427: Wheel format?
#
import sys
from pkg_resources import get_distribution as GD
from pkg_resources import parse_version as V


def test_python_ver():
    req_ver = (2, 7)
    cur_ver = sys.version_info
    assert cur_ver >= req_ver


def test_numpy():
    numpy_meta = GD("numpy")
    assert numpy_meta.parsed_version >= V('1.9.0')


def test_traits():
    traits_meta  = GD("traits")
    assert traits_meta.parsed_version >= V('4.4.0')


def test_pyparsing():
    pyparsing_meta  = GD("pyparsing")
    assert pyparsing_meta.parsed_version == V('2.0.3')


def test_xlrd():
    xlrd_meta = GD("xlrd")
    assert xlrd_meta.parsed_version >= V('0.9.2')


def test_openpyxl():
    openpyxl_meta = GD("openpyxl")
    assert openpyxl_meta.parsed_version >= V('1.8.5')


def test_pandas():
    pandas_meta = GD("pandas")
    assert pandas_meta.parsed_version >= V('0.14.0')


def test_pyper():
    '''version 1.1.2: the row index is not importet to Pandas DataFrames'''
    pyper_meta = GD("pyper")
    assert pyper_meta.parsed_version >= V('1.1.1')


def test_colormath():
    color_meta = GD("colormath")
    assert color_meta.parsed_version == V('2.1.0')


#def test_wxpython():
#    # wx_meta = GD("wx")
#    import wx
#    wx_ver = V(wx.__version__)
#    assert wx_ver >= V('2.8.12.1')
#    del(wx)


# @pytest.mark.xfail
#def test_pyside():
#    # pyside_meta = GD("PySide")
#    import PySide
#    qt_ver = V(PySide.__version__)
#    assert qt_ver >= V('1.1.2')
#    del(PySide)


# @pytest.mark.xfail
def test_pyqt4():
    from PyQt4.QtCore import QT_VERSION_STR
    from PyQt4.Qt import PYQT_VERSION_STR
    from sip import SIP_VERSION_STR
    print("Qt version:", QT_VERSION_STR)
    print("SIP version:", SIP_VERSION_STR)
    print("PyQt version:", PYQT_VERSION_STR)
    assert V(PYQT_VERSION_STR) >= V('4.10.0')


#@pytest.mark.skipif(sys.platform != 'win32', reason='Only on win dev')
#def test_bbfreeze():
#    freeze_meta = GD("bbfreeze")
#    assert freeze_meta.parsed_version == V('1.1.3')
