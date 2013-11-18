
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
    assert numpy_meta.parsed_version >= V('1.6.2')


def test_traits():
    traits_meta  = GD("traits")
    assert traits_meta.parsed_version >= V('4.2.0')


def test_pyparsing():
    pyparsing_meta  = GD("pyparsing")
    # FIXME: SVG button stuff is failing with 2.0.1
    assert pyparsing_meta.parsed_version == V('1.5.6')


def test_xlrd():
    xlrd_meta = GD("xlrd")
    assert xlrd_meta.parsed_version >= V('0.8.0')


def test_openpyxl():
    openpyxl_meta = GD("openpyxl")
    assert openpyxl_meta.parsed_version >= V('1.5.8')


def test_pandas():
    pandas_meta = GD("pandas")
    assert pandas_meta.parsed_version >= V('0.10.0')


def test_pyper():
    pyper_meta = GD("pyper")
    assert pyper_meta.parsed_version >= V('1.1.1')


def test_colormath():
    color_meta = GD("colormath")
    assert color_meta.parsed_version == V('1.0.8')


def test_wxpython():
    ## wx_meta = GD("wx")
    import wx
    wx_ver = V(wx.__version__)
    assert wx_ver >= V('2.8.12.1')
    del(wx)


def test_pyside():
    # pyside_meta = GD("PySide")
    import PySide
    qt_ver = V(PySide.__version__)
    assert qt_ver >= V('1.1.2')
    del(PySide)
