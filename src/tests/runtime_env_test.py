
import pytest

# Tools for version checking
# http://pythonhosted.org/distribute/pkg_resources.html
# 
# Check for API differences
# 
# http://aima.cs.berkeley.edu/python/utils.html
#
# Module version format
# http://www.python.org/dev/peps/pep-0396/
#
# from distutils.version import StrictVersion
#
import pkg_resources


def test_python_ver():
    import sys
    req_ver = (2, 7)
    cur_ver = sys.version_info
    assert cur_ver >= req_ver


def test_numpy():
    numpy_meta = pkg_resources.get_distribution("numpy")
    assert numpy_meta.version == '1.6.2'
#    print(numpy_meta.parsed_version)
#    assert numpy_meta.parsed_version >= (1, 5, 3)


def test_traits():
    traits_meta  = pkg_resources.get_distribution("traits")
    assert traits_meta.version == '4.2.0'


def test_pyparsing():
    pyparsing_meta  = pkg_resources.get_distribution("pyparsing")
    assert pyparsing_meta.version == '1.5.6'


def test_xlrd():
    xlrd_meta = pkg_resources.get_distribution("xlrd")
    assert xlrd_meta.version == '0.8.0'


def test_openpyxl():
    openpyxl_meta = pkg_resources.get_distribution("openpyxl")
    assert openpyxl_meta.version == '1.5.8'


def test_pandas():
    pandas_meta = pkg_resources.get_distribution("pandas")
    assert pandas_meta.version == '0.10.0'


def test_pyper():
    pyper_meta = pkg_resources.get_distribution("pyper")
    assert pyper_meta.version == '1.1.1'
