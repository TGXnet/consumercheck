# coding=utf-8

# Enthought imports
from enthought.traits.api import HasTraits, Instance, Array, Enum
from enthought.traits.ui.api import View, Item
from enthought.chaco.api import Plot, ArrayPlotData
from enthought.enable.component_editor import ComponentEditor
from enthought.chaco.chaco_plot_editor import ChacoPlotItem

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
        plot.plot(("x", "y"),
                  type="scatter",
                  color="green")
        plot.title = "Principal Componet Analysis"
        self.plot = plot

    # end PlotPca class



class PlotPcaNew(HasTraits):

    dm = Array

    pc1 = Array
    pc2 = Array

    plot_type = Enum("scatter", "line")

    traits_view = View(
        ChacoPlotItem('pc1', 'pc2',
                      type_trait='plot_type',
                      resizable=True,
                      x_label='PC1',
                      y_label='PC2',
                      x_bounds=(-15, 15),
                      x_auto=False,
                      y_bounds=(-15,15),
                      y_auto=False,
                      color='blue',
                      bgcolor='white',
                      border_visible=True,
                      border_width=1,
                      title='PCA plot',
                      padding_bg_color='lightgray'
                      ),
        resizable = True,
        buttons = ["OK"],
        title='Principal Component Analysis',
        width=900, height=800
        )

    # end Data class



if __name__== "__main__":
    PlotPca().configure_traits()
