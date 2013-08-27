
# Module imports
import pytest

import numpy as np
import pandas as pd

# Local imports
from dataset import DataSet, VisualStyle


@pytest.fixture
def line_curve():
    n = 8
    f = 1.0
    s = 0.0
    vals = []
    for i in range(n):
        f /= 2
        # s += f * 100
        s = f * 100
        vals.append(s)

    cal = np.array(vals)
    val = cal / 1.3
    ds = DataSet(
        mat=pd.DataFrame([cal, val],
                         index=['calibrated', 'validated'],
                         columns=['PC-1', 'PC-2', 'PC-3', 'PC-4', 'PC-5', 'PC-6', 'PC-7', 'PC-8']),
        display_name='My data', kind='Sensory profiling',
        style=VisualStyle(fg_color='indigo'),
        )
    return ds


@pytest.mark.ui
def test_simple_ev_line_plot(line_curve):
    from plot_ev_line import EVLinePlot
    line_curve.print_traits()
    print(line_curve.mat)
    plot = EVLinePlot(line_curve)
    plot.new_window(True)
    assert True
