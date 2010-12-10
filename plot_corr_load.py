# -*- coding: utf-8 -*-
"""
Draws a simple scatterplot of a set of random points.
Based on: /usr/share/doc/python-chaco/examples/basic/scatter.py
FIXME: This is a copy of PlotScatter. Make a inherrited plot hiearcy
and have a closer look at the interface in ui_tab_pca.py
"""

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor
from enthought.traits.api import HasTraits, Instance, Array, Str, List
from enthought.traits.ui.api import Item, Group, View
from enthought.chaco.api import ArrayPlotData, Plot, DataLabel

#===============================================================================
# Attributes to use for the plot view.
size = (650, 650)
title = "ConsumerCheck plot"
bg_color="lightgray"

#===============================================================================
class PlotCorrLoad(HasTraits):

    ttext = Str()
    titleX = Str()
    titleY = Str()
    valPtLabel = List()
    valX = Array()
    valY = Array()
    elXF = Array()
    elYF = Array()
    elXH = Array()
    elYH = Array()

    plot = Instance(Component)

    traits_view = View(
                    Group(
                        Item('plot',
                             editor=ComponentEditor(size = size,
                                                    bgcolor = bg_color),
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title=title,
                    buttons = ["OK"]
                    )


#    def __init__(self, x, y):
#        super(PlotCorrLoad3, self).__init__()
#        self.valX = x
#        self.valY = y


    def _plot_default(self):
        # Create a plot data object and give it this data

        # Plot data
        pd = ArrayPlotData()
        pd.set_data("pca1", self.valX)
        pd.set_data("pca2", self.valY)
        pd.set_data("elxf", self.elXF)
        pd.set_data("elyf", self.elYF)
        pd.set_data("elxh", self.elXH)
        pd.set_data("elyh", self.elYH)

        plot = Plot(pd)

        plot.plot(("pca1", "pca2"),
                  name = 'datapoints',
                  type="scatter",
                  marker="circle",
                  index_sort="ascending",
                  color="orange",
                  marker_size=3,
                  bgcolor="white")



        plot.plot(("elxf", "elyf"),
                  name = 'fullellipse',
                  type="line")



        plot.plot(("elxh", "elyh"),
                  name = 'halfellipse',
                  type="line")



        # Tweak some of the plot properties
        plot.title = self.ttext
        plot.line_width = 0.5
        plot.padding = 50

        # Set axis limits
#        plot = self._setPlotAxix(plot)
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



    def _setPlotAxix(self, plot):
        xmapper = plot.x_mapper
        ymapper = plot.y_mapper
        xlim, ylim = self._calcBoundsLimits()
        xlo, xhi = xlim
        ylo, yhi = ylim
        xmapper.range.set_bounds(xlo, xhi)
        ymapper.range.set_bounds(ylo, yhi)

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
