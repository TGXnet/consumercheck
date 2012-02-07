# Per directory py.test helper functions
# More info about this file her:
# http://pytest.org/latest/funcargs.html
# 
# Example functions for this file
# Argument parsers
# Provider of various objects
# ds, dsl, mock-mother

# Std lib imports
import numpy as np
from os.path import dirname, abspath, join

# Local imports
from dataset import DataSet
from plot_pc_scatter import PCScatterPlot


def pytest_runtest_setup(item):
    print("hook in conftest: setting up", item)


def pytest_funcarg__ds(request):
    """Provides a dataset object"""
    return DataSet()


def pytest_funcarg__test_ds_dir(request):
    """Yield a path to the test data directory"""
    here = dirname(__file__)
    basedir = dirname(here)
    return join(basedir, 'datasets')


def pytest_funcarg__simple_plot(request):
    """Yield a simple plot for testing plot windows"""
    set1 = np.array([
        [-0.3, 0.4, 0.9],
        [-0.1, 0.2, 0.7],
        [-0.1, 0.1, 0.1],
        ])
    label1 = ['s1pt1', 's1pt2', 's1pt3']
    expl_vars = {1:37.34, 2:9.4, 3:0.3498}
    color = (0.8, 0.2, 0.1, 1.0)
    sp = PCScatterPlot(set1, label1, color, expl_vars)
    ## sp.add_PC_set(set1, labels=label1, color=(0.8, 0.2, 0.1, 1.0))

    return sp
