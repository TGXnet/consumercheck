'''Plotting stand alone windows
'''
#-----------------------------------------------------------------------------
#  Copyright (C) 2014 Thomas Graff <thomas.graff@tgxnet.no>
#
#  This file is part of ConsumerCheck.
#
#  ConsumerCheck is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  ConsumerCheck is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ConsumerCheck.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------

import os
from os.path import join as pjoin

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import (HasTraits, Any, Instance, Bool, Str,
                        File, List, Button, on_trait_change)
from traitsui.api import (View, Group, Item, Handler,
                          Include, InstanceEditor)
# from traitsui.menu import OKButton
from chaco.api import GridPlotContainer
from pyface.api import FileDialog, OK
from enable.savage.trait_defs.ui.svg_button import SVGButton

#Local imports
import cc_config as conf
# from ui_results import TableViewController
# from ds_matrix_view import TableViewer
# from plot_pc_scatter import PCScatterPlot
from ds_table_view import DSTableViewer
from plugin_tree_helper import ViewNavigator, WindowLauncher


#==============================================================================
# Attributes to use for the plot view.
# width, height
sz_abs = (600, 600)
sz_rel = (0.7, 1.0)
bg_color = "white"
img_path = conf.graphics_path()
#==============================================================================


class PWC(Handler):
    """ Change the title on the UI.

    """
    def init(self, info):
        info.object.hwin = info.ui.control

    def object_title_text_changed(self, info):
        """ Called when the title_text changes on the handled object.

        """
        info.ui.title = info.object.title_text

    def object_save_plot_changed(self, info):
        fe = FileEditor()
        fe._save_as_img(info.object)


class PlotWindow(HasTraits):
    """Base class for both single and multiplot windows

    """
    res = Any()
    hwin = Any()
    view_loop = List(WindowLauncher)
    title_text = Str
    save_plot = SVGButton(filename=pjoin(img_path, 'save.svg'),
                          width=32, height=32)


class SinglePWC(PWC):
    """ Change the title on the UI.
    """
    def object_plot_changed(self, info):
        if info.object.res:
            wt = info.object.res.method_name
            pt = info.object.plot.model.get_plot_name()
            info.object.title_text = "{0} | {1} - ConsumerCheck".format(wt, pt)

    def object_title_text_changed(self, info):
        """ Called when the title_text changes on the handled object.

        """
        # info.ui.title = info.object.title_text
        super(SinglePWC, self).object_title_text_changed(info)
        # info.object.plot.model.title = info.object.title_text
        info.object.plot.model.title = info.object.plot.model.get_plot_name()

    def object_view_table_changed(self, info):
        tv = DSTableViewer(info.object.plot.model.plot_data)
        tv.edit_traits(view=tv.get_view(), parent=info.object.hwin)

    def object_next_plot_changed(self, info):
        info.object.plot = info.object.plot_navigator.show_next()

    @on_trait_change('previous_plot')
    def object_previous_plot_changed(self, info):
        info.object.plot = info.object.plot_navigator.show_previous()


class SinglePlotWindow(PlotWindow):
    """Window for embedding line plot

    """
    plot = Instance(Handler)
    plot_navigator = Instance(ViewNavigator)
    next_plot = Button('Next plot')
    previous_plot = Button('Previous plot')
    view_table = Button('View result table')

    def _plot_navigator_default(self):
        if self.res and self.view_loop:
            return ViewNavigator(res=self.res, view_loop=self.view_loop)
        else:
            return None

    plot_gr = Group(
        Item('plot', editor=InstanceEditor(),
             style='custom', show_label=False,
             width=sz_abs[0], height=sz_abs[1]),
        )

    main_gr = Group(
        Item('save_plot', show_label=False),
        Item('view_table', show_label=False),
        Item('previous_plot', show_label=False, defined_when='plot_navigator'),
        Item('next_plot', show_label=False, defined_when='plot_navigator'),
        orientation="horizontal",
        )

    ## def default_traits_view(self):
    traits_view = View(
        Group(
            Include('plot_gr'),
            Include('main_gr'),
            layout="normal",
            ),
        resizable=True,
        handler=SinglePWC(),
        # kind = 'nonmodal',
#        width=sz_rel[0],
#        height=sz_rel[1],
        buttons=["OK"]
        )


class MultiPlotWindow(PlotWindow):
    plots = Instance(Component)


class OverviewPlotWindow(MultiPlotWindow):
    """Window for embedding multiple plots

    Set plots.component_grid with list of plots to add the plots
    Set plots.shape to tuple(rows, columns) to indicate the layout of the plots

    """
    show_labels = Bool(True)

    @on_trait_change('show_labels')
    def switch_labels(self, obj, name, new):
        # FIXME: This can be done nicer
        obj.plots.component_grid[0][0].show_labels(show=new)
        obj.plots.component_grid[0][1].show_labels(show=new)
        obj.plots.component_grid[1][0].show_labels(show=new)
        obj.plots.component_grid[1][1].show_labels(show=new)

    traits_view = View(
        Item('plots',
             editor=ComponentEditor(bgcolor=bg_color),
             show_label=False,
             width=sz_abs[0], height=sz_abs[1]),
        Group(
            Item('show_labels', label="Show labels"),
            orientation="vertical"),
        resizable=True,
        handler=PWC(),
        # kind = 'nonmodal',
#        width=sz_rel[0],
#        height=sz_rel[1],
        buttons=["OK"]
        )

    def _plots_default(self):
        container = GridPlotContainer(background=bg_color)
        return container


class FileEditor(HasTraits):

    file_name = File()

    def _save_img(self, obj):
        """ Attaches a .png extension and exports the image.
        """
        a, b, c = self.file_name.rpartition('.')
        if c == 'png':
            obj.plot.model.export_image(self.file_name)
        else:
            self.file_name = '{}.png'.format(self.file_name)
            obj.plot.model.export_image(self.file_name)

    def _save_as_img(self, obj):
        """ Specify a filename for the image, in destination folder.
        """
        fd = FileDialog(action='save as',
                        default_path=self.file_name,
                        default_filename='test.png',
                        wildcard="PNG files (*.png)|*.png|")
        if fd.open() == OK:
            self.file_name = fd.path
            if self.file_name != '':
                self._save_img(obj)


if __name__ == '__main__':
    import numpy as np
    from tests.conftest import clust1ds
    from plot_pc_scatter import PCScatterPlot, PCPlotControl, ScatterSectorPlot, PCSectorPlotControl
    # from plot_base import NoPlotControl

    mydata = clust1ds()
    plot = ScatterSectorPlot(mydata)
    # plot_control = NoPlotControl(model=plot)
    plot_control = PCSectorPlotControl(model=plot)
    pw = SinglePlotWindow(plot=plot_control)

    with np.errstate(invalid='ignore'):
        pw.configure_traits()
