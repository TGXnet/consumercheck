"""Plotting stand alone windows

"""
# Enthought library imports
from enthought.enable.api import Component, ComponentEditor
from enthought.traits.api import HasTraits, Instance, Bool, Str, on_trait_change
from enthought.traits.ui.api import View, Group, Item, Label, Handler
from enthought.chaco.api import GridPlotContainer, HPlotContainer

#===============================================================================
# Attributes to use for the plot view.
size = (850, 650)
title = "ConsumerCheck plot"
bg_color="white"

#===============================================================================

class TitleHandler(Handler):
    """ Change the title on the UI.

    """

    def object_title_text_changed(self, info):
        """ Called whenever the title_text attribute changes on the handled object.

        """
        info.ui.title = info.object.title_text




class SinglePlotWindow(HasTraits):
    """Window for embedding single plot
    """
    plot = Instance(Component)
    eq_axis = Bool(False)
    show_x1 = Bool(True)
    title_text = Str("ConsumerCheck")

    @on_trait_change('show_x1')
    def switch_labels(self, object, name, new):
        ds_id = name.partition('_')[2]
        object.plot.switchLabellVisibility(ds_id, new)

    @on_trait_change('eq_axis')
    def switch_axis(self, object, name, new):
        object.plot.toggleEqAxis(new)

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
                Item('eq_axis', label="Set equal axis"),
                Item('show_x1', label="Show labels"),
                orientation="horizontal",
                ),
            layout="normal",
            ),
        resizable=True,
        title=title,
        handler=TitleHandler(),
        # kind = 'nonmodal',
        buttons = ["OK"]
        )


class MultiPlotWindow(HasTraits):
    """Window for embedding multiple plots

    Set plots.component_grid with list of plots to add the plots
    Set plots.shape to tuple(rows, columns) to indicate the layout of the plots
    """
    plots = Instance(Component)
    title_text = Str("ConsumerCheck")

    traits_view = View(
        Group(
            Item('plots',
                 editor=ComponentEditor(
                     size = size,
                     bgcolor = bg_color),
                 show_label=False),
            orientation = "vertical"),
        resizable=True,
        title=title,
        handler=TitleHandler(),
        # kind = 'nonmodal',
        buttons = ["OK"]
        )

    def _plots_default(self):
        container = GridPlotContainer(background=bg_color)
        return container
