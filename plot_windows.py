"""Frames (view) for plotting

"""

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import View, Group, Item
from enthought.chaco.api import GridPlotContainer, HPlotContainer

#===============================================================================
# Attributes to use for the plot view.
size = (650, 650)
title = "ConsumerCheck plot"
bg_color="lightgray"

#===============================================================================
class SinglePlotWindow(HasTraits):
    """Window for embedding single plot
    """
    plot = Instance(Component)
    traits_view = View(
        Group(
            Item('plot',
                 editor=ComponentEditor(
                     size = size,
                     bgcolor = bg_color),
                 show_label=False),
            orientation = "vertical"),
        resizable=True, title=title,
#       kind = 'nonmodal',
        buttons = ["OK"]
        )


class MultiPlotWindow(HasTraits):
    """Window for embedding multiple plots

    Set plots.component_grid with list of plots to add the plots
    Set plots.shape to tuple(rows, columns) to indicate the layout of the plots
    """
    plots = Instance(Component)
    traits_view = View(
        Group(
            Item('plots',
                 editor=ComponentEditor(
                     size = size,
                     bgcolor = bg_color),
                 show_label=False),
            orientation = "vertical"),
        resizable=True, title=title,
#       kind = 'nonmodal',
        buttons = ["OK"]
        )

    def _plots_default(self):
        container = GridPlotContainer(background="lightgray")
        return container
