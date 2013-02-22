
# Module imports
import pytest


@pytest.fixture
def line_curve():
    import numpy as np
    n = 8
    f = 1.0
    s = 0.0
    vals = []
    for i in range(n):
        f /= 2
        s += f * 100
        vals.append(s)

    return np.array(vals)


## @pytest.mark.ui
def test_simple_ev_line_plot(line_curve):
    from plot_ev_line import EVLinePlot
    plot = EVLinePlot()
    plot.add_EV_set(line_curve)
    plot.new_window(True)
