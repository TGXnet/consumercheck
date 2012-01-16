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

        self.set2 = array([
            [-1.3, -0.4, -0.9],
            [-1.1, -0.2, -0.7],
            [-1.2, -0.1, -0.1],
            ])

        self.label1 = ['s1pt1', 's1pt2', 's1pt3']
        self.label2 = ['s2pt1', 's2pt2', 's2pt3']


    def test_plot_one_set(self):
        plot = CCScatterPCPlot()
        # (0.5, 0.5, 0.5, 0.2) (R, G, B, Alpha)
        plot.add_PC_set(self.set1, self.label1)
        plot.new_window(True)

    def test_plot_two_sets(self):
        plot = CCScatterPCPlot()
        # (0.5, 0.5, 0.5, 0.2) (R, G, B, Alpha)
        plot.add_PC_set(self.set1, color=(0.8, 0.2, 0.1, 1.0), labels=self.label1)
        plot.add_PC_set(self.set2, color=(0.2, 0.9, 0.1, 1.0), labels=self.label2)
        plot.new_window(True)
