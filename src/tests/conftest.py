# Per directory py.test helper functions
# More info about this file her:
# http://pytest.org/latest/funcargs.html
# 
# Example functions for this file
# Argument parsers
# Provider of various objects
# ds, dsl, mock-mother

from os.path import dirname, abspath, join


from dataset import DataSet


def pytest_runtest_setup(item):
    print("hook in conftest: setting up", item)


def pytest_funcarg__ds(request):
    """Provides a dataset object"""
    return DataSet()


def pytest_funcarg__datasets(request):
    """Yield a path to the test data directory"""
    here = dirname(__file__)
    basedir = dirname(here)
    return join(basedir, 'datasets')
