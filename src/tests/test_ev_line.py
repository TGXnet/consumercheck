


# Module imports
import pytest
import numpy as np

# Local imports
from plot_ev_line import EVLinePlot


## @pytest.mark.ui
def test_simple_ev_line_plot():
    line = np.array([56.4, 78.9, 96.0, 99.4])
    plot = EVLinePlot()
    plot.add_EV_set(line)
    plot.new_window(True)
