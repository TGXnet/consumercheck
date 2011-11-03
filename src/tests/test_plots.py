
def setConsumerCheckIncludePath():
    consumerBase = findApplicationBasePath()
    addLoadPath(consumerBase)


def findApplicationBasePath():
    basePath = os.getcwd()
    while os.path.basename(basePath) != 'tests':
        basePath = os.path.dirname(basePath)
    basePath = os.path.dirname(basePath)
    return basePath


def addLoadPath(baseFolderPath):
    sys.path.append(baseFolderPath)


import unittest
import os
import sys
from numpy import array, ndarray, zeros, sort
from numpy.random import random
from chaco.api import ArrayPlotData

class TestDatasetModel(unittest.TestCase):

    def setUp(self):
        self.show_gui = False
        # Load a data set
        data = st.arrayIO('../datasets/Polser.txt')
        dataMat = data.data
        dataObjs = data.objNames
        dataVars = data.varNames
        # Run PCA
        PCA = nipals.PCA(dataMat)
        # Get results
        T = PCA.getScores()
        P = PCA.getLoadings()
        E_dict = PCA.getResidualsMatrices()
        Xhat_dict = PCA.getPredictedMatrices()
        settings_dict = PCA.getSettings()
        calExplVar_dict = PCA.getCalExplVar()
        corrLoads = PCA.getCorrLoadings()
        ellipses = PCA.getCorrLoadingsEllipses()
        # Plotting correlation loadings plot
        xcords100percent = ellipses['x100perc']
        ycords100percent = ellipses['y100perc']
        xcords50percent = ellipses['x50perc']
        ycords50percent = ellipses['y50perc']
        expl_index = [0]
        expl_val = [0]
        for index, value in calExplVar_dict.iteritems():
            expl_index.append(index)
            expl_val.append(expl_val[index-1] + value)
        self.labels = dataVars
        self.pd = ArrayPlotData(
            pc_x=corrLoads[:,0],
            pc_y=corrLoads[:,1],
            index=expl_index,
            y_val=expl_val,
            ell_full_x=xcords100percent,
            ell_full_y=ycords100percent,
            ell_half_x=xcords50percent,
            ell_half_y=ycords50percent)

    def test1EmptySinglePlotWindow(self):
        spw = SinglePlotWindow()
        # s_ui = spw.configure_traits()
        # or
        if self.show_gui:
            s_ui = spw.configure_traits()

    def test2SingleScatterPlot(self):
        ps = PlotScatter(self.pd)
        spw = SinglePlotWindow(plot=ps)
        if self.show_gui:
            spw_ui = spw.configure_traits()

    def test3SetEqAxis(self):
        ps = PlotScatter(self.pd)
        ps.set_eq_axis()
        spw = SinglePlotWindow(plot=ps)
        if self.show_gui:
            spw_ui = spw.configure_traits()

    def test4PlotLabels(self):
        ps = PlotScatter(self.pd)
        ps.addPtLabels(self.labels)
        spw = SinglePlotWindow(plot=ps)
        if self.show_gui:
            spw_ui = spw.configure_traits()

    def test5MultiPlot(self):
        ps1 = PlotScatter(self.pd)
        ps2 = PlotScatter(self.pd)
        ps3 = PlotScatter(self.pd)
        plots = [ps1, ps2 ,ps3]
        spw = MultiPlotWindow()
        spw.plots.component_grid = plots
        spw.plots.shape = (2,2)
        if self.show_gui:
            spw_ui = spw.configure_traits()

    def test6SingleLinePlot(self):
        ps = PlotLine(self.pd)
        spw = SinglePlotWindow(plot=ps)
        if self.show_gui:
            spw_ui = spw.configure_traits()


    def test7SingleCorrLoadPlot(self):
        ps = PlotCorrLoad(self.pd)
        spw = SinglePlotWindow(plot=ps)
        if self.show_gui:
            spw_ui = spw.configure_traits()



if __name__ == '__main__':
    # path for local imports
    setConsumerCheckIncludePath()
    from plot_windows import SinglePlotWindow, MultiPlotWindow
    from plots import PlotScatter, PlotLine, PlotCorrLoad
    import nipals
    import statTools as st
    unittest.main()
