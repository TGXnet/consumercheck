# -*- coding: utf-8 -*-
"""
Draws a simple lineplot.

Based on: /usr/share/doc/python-chaco/examples/basic/scatter.py
"""

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor
from enthought.traits.api import HasTraits, Instance, Array, Str, List, Tuple
from enthought.traits.ui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import ArrayPlotData, Plot, DataLabel

#===============================================================================
# Attributes to use for the plot view.
size = (650, 650)
title = "ConsumerCheck plot"
bg_color="lightgray"

class PlotLine(HasTraits):

    ttext = Str()
    titleX = Str()
    titleY = Str()
    valPtLabel = List()
    valX = Array()
    valY = Array()
    limX = Tuple()
    limY = Tuple()

    plot = Instance(Component)

    traits_view = View(
                    Group(
                        Item('plot',
                             editor = ComponentEditor( size=size,
                                                       bgcolor=bg_color),
                             show_label = False),
                        orientation = "vertical"),
                    resizable = True, title = title,
                    buttons = ["OK"]
                    )


    def _plot_default(self):
        # Create a plot data object and give it this data

        # Plot data
        pd = ArrayPlotData()
        pd.set_data("index", self.valX)
        pd.set_data("y0", self.valY)

        plot = Plot(pd, title = self.ttext, line_width = 0.5, padding = 50)

        plot.plot(("index", "y0"),
                  type="line",
                  index_sort="ascending",
                  color="orange",
                  bgcolor="white")

        # Set axis limits
        plot = self._setAxisLimits(plot)

        # Add title to axis
        plot = self._addAxisTitle(plot)

        # Add labels to datapoints
#        plot = self._addPtLabels(plot)

        return plot




    def _setAxisLimits(self, plot):
        if self.limX:
            xlo, xhi = self.limX
            xmapper = plot.x_mapper
            xmapper.range.set_bounds(xlo, xhi)

        if self.limY:
            ylo, yhi = self.limY
            ymapper = plot.y_mapper
            ymapper.range.set_bounds(ylo, yhi)

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


#---EOF---
