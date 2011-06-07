"""Plotting stand alone windows

"""
# Enthought library imports
from enthought.enable.api import Component, ComponentEditor
from enthought.traits.api import HasTraits, Instance, Bool, on_trait_change
from enthought.traits.ui.api import View, Group, Item, Label
from enthought.chaco.api import GridPlotContainer, HPlotContainer

#===============================================================================
# Attributes to use for the plot view.
size = (850, 650)
title = "ConsumerCheck plot"
bg_color="white"

#===============================================================================
class SinglePlotWindow(HasTraits):
    """Window for embedding single plot
    """
    plot = Instance(Component)
    show_x1 = Bool(True)
    show_x2 = Bool(True)
    show_x3 = Bool(True)
    show_y2 = Bool(True)

    @on_trait_change('show_x1, show_x2, show_x3, show_y2')
    def switch_labels(self, object, name, new):
        ds_id = name.partition('_')[2]
        object.plot.switchLabellVisibility(ds_id, new)

    traits_view = View(
        Group(
            Group(
                Item('plot',
                     editor=ComponentEditor(
                         size = size,
                         bgcolor = bg_color),
                     show_label=False),
                orientation = "vertical"
                ),
            Label('Mouse scroll and drag to zoom and pan in plot'),
            Group(
                Item('show_x1', label="Show sensory attributes"),
                Item('show_x2', label="Show consumer ID"),
                Item('show_x3', label="Show question no"),
                Item('show_y2', label="Show product ID"),
                orientation="horizontal",
                ),
            layout="normal",
            ),
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
        container = GridPlotContainer(background=bg_color)
        return container
