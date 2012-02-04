"""Test to be used with py.test.
"""

import numpy as np
from numpy import array
import pytest

# Local imports
from new_plots import CCScatterPCPlot
from plot_windows import SinglePlotWindow


def pytest_funcarg__plot(request):
    print("\nHello")
    print(request)
    return CCScatterPCPlot()


class TestPlotBase(object):
    pass

@pytest.mark.classone
class TestPCPlotSingleSet(TestPlotBase):

    def setup_method(self, method):
        self.set1 = array([
            [-0.3, 0.4, 0.9],
            [-0.1, 0.2, 0.7],
            [-0.1, 0.1, 0.1],
            ])

        self.label1 = ['s1pt1', 's1pt2', 's1pt3']

    @pytest.mark.ui
    def test_plot_one_set(self, plot):
        # (0.5, 0.5, 0.5, 0.2) (R, G, B, Alpha)
        plot.add_PC_set(self.set1, color=(0.8, 0.2, 0.1, 1.0), labels=self.label1)
        plot.new_window(True)


@pytest.mark.classtwo
class TestPCPlotMultipleSet(TestPCPlotSingleSet):

    def setup_method(self, method):
        super(TestPCPlotMultipleSet, self).setup_method(method)

        self.set2 = array([
            [-1.3, -0.4, -0.9],
            [-1.1, -0.2, -0.7],
            [-1.2, -0.1, -0.1],
            ])

        self.label2 = ['s2pt1', 's2pt2', 's2pt3']

    @pytest.mark.two
    def test_plot_two_sets(self):
        plot = CCScatterPCPlot()
        # (0.5, 0.5, 0.5, 0.2) (R, G, B, Alpha)
        plot.add_PC_set(self.set1, color=(0.8, 0.2, 0.1, 1.0), labels=self.label1)
        plot.add_PC_set(self.set2, color=(0.2, 0.9, 0.1, 1.0), labels=self.label2)
        plot.plot_circle(True)
        assert plot.plots.keys().sort() == [
            'ell_half', 'ell_full', 'plot_2', 'plot_1'
            ].sort()
        # plot.new_window(True)


@pytest.mark.window
def test_plot_window(simple_plot):
    spw = SinglePlotWindow(plot=simple_plot)
    with np.errstate(invalid='ignore'):
        spw.configure_traits()
