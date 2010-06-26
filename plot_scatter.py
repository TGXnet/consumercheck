"""
Draws a simple scatterplot of a set of random points.

 Based on: /usr/share/doc/python-chaco/examples/basic/scatter.py
"""

# Major library imports
from numpy import arange, sort
from numpy.random import random

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor
from enthought.traits.api import HasTraits, Instance, Array, Str, List
from enthought.traits.ui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import ArrayPlotData, Plot, DataLabel

#===============================================================================
# Attributes to use for the plot view.
size = (650, 650)
title = "ConsumerCheck plot"
bg_color="lightgray"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class PlotScatter(HasTraits):

    ttext = Str()
    titleX = Str()
    titleY = Str()
    valPtLabel = List()
    valX = Array()
    valY = Array()

    plot = Instance(Component)

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size,
                                                            bgcolor=bg_color),
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title=title,
                    buttons = ["OK"]
                    )


#    def __init__(self, x, y):
#        super(PlotScatter3, self).__init__()
#        self.valX = x
#        self.valY = y


    def _plot_default(self):
        # Create a plot data object and give it this data

        # Plot data
        pd = ArrayPlotData()
        pd.set_data("pca1", self.valX)
        pd.set_data("pca2", self.valY)

        plot = Plot(pd)

        # Set axis limits
        xmapper = plot.x_mapper
        ymapper = plot.y_mapper
        xlim, ylim = self._calcBoundsLimits()
        xlo, xhi = xlim
        ylo, yhi = ylim
        xmapper.range.set_bounds(xlo, xhi)
        ymapper.range.set_bounds(ylo, yhi)

        plot.plot(("pca1", "pca2"),
                  type="scatter",
                  marker="circle",
                  index_sort="ascending",
                  color="orange",
                  marker_size=3,
                  bgcolor="white")

        # Tweak some of the plot properties
        plot.title = self.ttext
        plot.line_width = 0.5
        plot.padding = 50

        plot = self._addAxisTitle(plot)
        plot = self._addPtLabels(plot)

        return plot


    def _addAxisTitle(self, plot):
        plot.x_axis.title = self.titleX
        plot.y_axis.title = self.titleY
        return plot



    def _addPtLabels(self, plot):
        for i in xrange(len(self.valPtLabel)):
            label = DataLabel(
                component = plot,
                data_point = (self.valX[i], self.valY[i]),
                label_format = self.valPtLabel[i]
                )
            plot.overlays.append(label)

        return plot



    def _calcBoundsLimits(self):
        # Return tuple of tuple with x and y bounds low and high limit
        iXMin = self.valX.argmin()
        iXMax = self.valX.argmax()
        xlim = (self.valX[iXMin], self.valX[iXMax])

        iYMin = self.valY.argmin()
        iYMax = self.valY.argmax()
        ylim = (self.valY[iYMin], self.valY[iYMax])

        if xlim[0] < ylim[0]:
            minLim = xlim[0]
        else:
            minLim = ylim[0]

        if xlim[1] > ylim[1]:
            maxLim = xlim[1]
        else:
            maxLim = ylim[1]

        minLim = minLim - maxLim * 0.1
        maxLim = maxLim + maxLim * 0.1

        return ((minLim, maxLim), (minLim, maxLim))




#---EOF---