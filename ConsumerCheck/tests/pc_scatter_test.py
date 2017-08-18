'''py.test test for plot_pc_scatter

debug inspection:
import pudb; pu.db
'''
import pytest

#Stdlib imports
import os

# Scipy imports
import numpy as np
import pandas as pd

# Local imports
import dataset as mx
from plot_windows import SinglePlotWindow
from importer_text_file import ImporterTextFile

# Test subject
import plot_pc_scatter as pps
from plot_pc_scatter import PCScatterPlot


@pytest.fixture
def clust1ds():
    """Manual random pick from the Iris datast: setosa"""
    ds = mx.DataSet(
        mat=pd.DataFrame(
            [[5.1,3.5,1.4,0.2],
             [4.6,3.4,1.4,0.3],
             [5.4,3.7,1.5,0.2],
             [5.7,3.8,1.7,0.3],
             [5.4,3.4,1.7,0.2],
             [4.8,3.1,1.6,0.2],
             [4.6,3.6,1.0,0.2]],
            index=['O1', 'O2', 'O3', 'O4', 'O5', 'O6', 'O7'],
            columns=['V1', 'V2', 'V3', 'V4']),
        display_name='Some values', kind='Descriptive analysis / sensory profiling',
        # style=VisualStyle(fg_color=(0.8, 0.2, 0.1, 1.0)),
        style=mx.VisualStyle(fg_color='indigo')
    )
    return ds


@pytest.fixture
def clust2ds():
    """Manual random pick from the Iris datast: versicolor"""
    ds = mx.DataSet(
        mat=pd.DataFrame(
            [[6.9,3.1,4.9,1.5],
             [4.9,2.4,3.3,1.0],
             [5.7,3.0,4.2,1.2],
             [5.1,2.5,3.0,1.1],
             [5.7,2.6,3.5,1.0],
             [5.1,2.5,3.0,1.1],
             [6.1,2.9,4.7,1.4]],
            index=['O1', 'O2', 'O3', 'O4', 'O5', 'O6', 'O7'],
            columns=['V1', 'V2', 'V3', 'V4']),
        display_name='Some values', kind='Descriptive analysis / sensory profiling',
        style=mx.VisualStyle(fg_color='saddlebrown')
    )
    return ds


@pytest.fixture
def clust3ds():
    """Manual random pick from the Iris datast: virginica"""
    ds = mx.DataSet(
        mat=pd.DataFrame(
            [[5.8,2.7,5.1,1.9],
             [6.5,3.0,5.8,2.2],
             [7.2,3.6,6.1,2.5],
             [6.8,3.0,5.5,2.1],
             [6.2,2.8,4.8,1.8],
             [6.4,3.1,5.5,1.8],
             [6.2,3.4,5.4,2.3]],
            index=['O1', 'O2', 'O3', 'O4', 'O5', 'O6', 'O7'],
            columns=['V1', 'V2', 'V3', 'V4']),
        display_name='Some values', kind='Descriptive analysis / sensory profiling',
        style=mx.VisualStyle(fg_color='olive')
    )
    return ds


@pytest.fixture
def expvar1ds():
    """Simulated explained variance"""
    ds = mx.DataSet(
        mat=pd.DataFrame(
            [[50.8,20.7,5.1,1.9],
             [30.2,12.4,5.4,2.3]],
            index=['calibrated', 'validated'],
            columns=['V1', 'V2', 'V3', 'V4']),
        display_name='Some values', kind='Descriptive analysis / sensory profiling',
        style=mx.VisualStyle(fg_color='olive')
    )
    return ds


@pytest.fixture
def expvar2ds():
    """Simulated explained variance"""
    ds = mx.DataSet(
        mat=pd.DataFrame(
            [[38.4,25.7,10.1,7.9],
             [67.2,18.4,9.4,1.3]],
            index=['calibrated', 'validated'],
            columns=['V1', 'V2', 'V3', 'V4']),
        display_name='Some values', kind='Descriptive analysis / sensory profiling',
        style=mx.VisualStyle(fg_color='olive')
    )
    return ds


@pytest.mark.ui
def test_pc_plot(clust1ds, expvar1ds):
    plot = pps.PCScatterPlot(clust1ds, expvar1ds)

    with np.errstate(invalid='ignore'):
        plot.new_window(True)
    assert 0


@pytest.mark.ui
def test_corre_correlation_plot(clust1ds, clust2ds, expvar1ds, expvar2ds):
    plot = pps.PCScatterPlot()
    plot.add_PC_set(clust1ds, expvar1ds)
    plot.add_PC_set(clust2ds, expvar2ds)
    plot.plot_circle(True)

    with np.errstate(invalid='ignore'):
        plot.new_window(True)
    assert 0


def test_color_factor():
    # from tests.conftest import iris_ds
    np.random.seed(10)
    gobli = (np.random.random((30, 4)) - 0.5) * 2
    pda = pd.DataFrame(gobli)
    pda.columns = ["V{0}".format(i+1) for i in range(pda.shape[1])]
    pda.index = ["O{0}".format(i+1) for i in range(pda.shape[0])]

    irds = mx.DataSet(mat=pda)

    factor = mx.Factor('TestColorFactor', irds.mat.shape[0])
    # sd = []
    # sd = ['red', 'green', 'blue']
    # for en, color in enumerate(sd):
    #     en *= 10
    #     rs = range(en, en+10)
    #     level = mx.Level(rs, name=color, color=color)
    #     factor.add_level(level)

    # dpath = os.environ['CC_TESTDATA']
    # dfile = dpath + '/Iris/iris_multiclass.csv'

    # itf = ImporterTextFile(
    #     file_path=dfile,
    #     delimiter=',',
    #     have_obj_names=False
    # )
    # itf.configure_traits()
    # ds = itf.import_data()

    # plot = PCScatterPlot(ds)
    plot = pps.SelectionScatterPlot(irds)
    # plot = pps.SelectionScatterPlot(irds, factor=factor)
    plot.data.coloring_factor = factor
    plot_control = pps.PCPlotControl(plot)
    pw = SinglePlotWindow(plot=plot_control)

    with np.errstate(invalid='ignore'):
        pw.configure_traits()



# Test generating and exporting plot image
# Use py.test tempdir facility
# see https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/noninteractive.py
# for more info plot image export.
