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
from new_plots import CCScatterPCPlot


class TestCCScatterPCPlot(object):

    def setup_method(self, method):
        self.set1 = array([
            [-0.3, 0.4, 0.9],
            [-0.1, 0.2, 0.7],
            [-0.1, 0.1, 0.1],
            ])

        self.label1 = ['pt1', 'pt2', 'pt3']


    def test_data(self):
        print(self.set1)
        print(self.label1)


    def test_plot1(self):
        plot = CCScatterPCPlot()
        # (0.5, 0.5, 0.5, 0.2) (R, G, B, Alpha)
        plot.add_PC_set(self.set1, self.label1)
        plot.new_window(True)
