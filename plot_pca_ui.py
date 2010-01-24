# coding=utf-8

# Enthought imports
from enthought.traits.api import HasTraits, Instance, Array
from enthought.traits.ui.api import View, Item
from enthought.chaco.api import Plot, ArrayPlotData
from enthought.enable.component_editor import ComponentEditor

from numpy import linspace, sin



class PlotPca(HasTraits):
    """PCA Plot GUI"""

    dm = Array()
    plot = Instance(Plot)

    traits_view = View(
        Item('plot',editor=ComponentEditor(), show_label=False),
        width=500, height=500, resizable=True, title="Chaco Plot")

    def __init__(self, dataMatrix):
        super(PlotPca, self).__init__()
        self.dm = dataMatrix
        x = self.dm[:,0]
        y = self.dm[:,1]
        plotdata = ArrayPlotData(x=x, y=y)
        plot = Plot(plotdata)
        plot.plot(("Pricipal 1", "Principal 2"), type="scatter", color="blue")
        plot.title = "Principal Componet Analysis"
        self.plot = plot



if __name__== "__main__":
    PlotPca().configure_traits()
