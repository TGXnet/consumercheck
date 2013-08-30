"""Plotting stand alone windows

"""
import os
from os.path import join as pjoin

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Any, Instance, Bool, Str, File, List, Button, on_trait_change
from traitsui.api import View, Group, Item, Label, Handler, Include
# from traitsui.menu import OKButton
from chaco.api import DataView, GridPlotContainer
from pyface.api import FileDialog, OK
from enable.savage.trait_defs.ui.svg_button import SVGButton

#Local imports
# from ui_results import TableViewController
# from ds_matrix_view import TableViewer
from plot_pc_scatter import PCScatterPlot
from ds_table_view import DSTableViewer
from plugin_tree_helper import ViewNavigator, WindowLauncher


#===============================================================================
# Attributes to use for the plot view.
size = (850, 650)
bg_color="white"
#===============================================================================


class PWC(Handler):
    """ Change the title on the UI.

    """
    def init(self, info):
        info.object.hwin = info.ui.control


    def object_title_text_changed(self, info):
        """ Called whenever the title_text attribute changes on the handled object.

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
    title_text = Str("ConsumerCheck")
    save_plot = SVGButton(filename=pjoin(os.getcwd(), 'save.svg'),
                          width=32, height=32)



class SinglePWC(PWC):
    """ Change the title on the UI.

    """
    def object_view_table_changed(self, info):
        tv = DSTableViewer(info.object.plot.plot_data)
        tv.edit_traits(view=tv.get_view(), parent=info.object.hwin)

    def object_next_plot_changed(self, info):
        info.object.plot = info.object.plot_navigator.show_next()

    @on_trait_change('previous_plot')
    def object_previous_plot_changed(self, info):
        info.object.plot = info.object.plot_navigator.show_previous()



class SinglePlotWindow(PlotWindow):
    """Window for embedding line plot

    """
    plot = Instance(DataView)
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
        Item('plot', editor=ComponentEditor(size = size, bgcolor = bg_color),
             show_label=False),
        orientation = "vertical"
        )

    main_gr = Group(
        Item('save_plot', show_label=False),
        Item('view_table', show_label=False),
        Item('previous_plot', show_label=False, defined_when='plot_navigator'),
        Item('next_plot', show_label=False, defined_when='plot_navigator'),
        orientation="horizontal",
        )

    extra_gr = Group()

    ## def default_traits_view(self):
    traits_view = View(
        Group(
            Include('plot_gr'),
            Label('Scroll to zoom and drag to pan in plot.'),
            Include('main_gr'),
            Include('extra_gr'),
            layout="normal",
            ),
        resizable=True,
        handler=SinglePWC(),
        # kind = 'nonmodal',
        width = .5,
        height = .7,
        buttons = ["OK"]
        )




class PCPlotWindow(SinglePlotWindow):
    """Window for embedding principal component plots

    """
    eq_axis = Bool(False)
    show_labels = Bool(True)
    # Prefmap correlation loading visibility togling
    vis_toggle = Button('Visibility')
    vistog = Bool(False)
    show_extra = Bool(False)

    y_down = SVGButton(filename=pjoin(os.getcwd(), 'y_down.svg'),
                       width=32, height=32)
    y_up = SVGButton(filename=pjoin(os.getcwd(), 'y_up.svg'),
                     width=32, height=32)
    x_down = SVGButton(filename=pjoin(os.getcwd(), 'x_down.svg'),
                       width=32, height=32)
    x_up = SVGButton(filename=pjoin(os.getcwd(), 'x_up.svg'),
                     width=32, height=32)
    reset_xy = SVGButton(filename=pjoin(os.getcwd(), 'reset_xy.svg'),
                         width=32, height=32)


    @on_trait_change('plot')
    def _update_controls(self, obj, name, new):
        if isinstance(new, PCScatterPlot):
            obj.show_extra = True
        else:
            obj.show_extra = False

    
    @on_trait_change('show_labels')
    def switch_labels(self, obj, name, new):
        obj.plot.show_labels(show= new)

    @on_trait_change('eq_axis')
    def switch_axis(self, obj, name, new):
        obj.plot.toggle_eq_axis(new)

    @on_trait_change('reset_xy')
    def pc_axis_reset(self, obj, name, new):
        obj.plot.set_x_y_pc(1, 2)

    @on_trait_change('x_up')
    def pc_axis_x_up(self, obj, name, new):
        x, y, n = obj.plot.get_x_y_status()
        if x<n:
            x += 1
        else:
            x = 1
        obj.plot.set_x_y_pc(x, y)

    @on_trait_change('x_down')
    def pc_axis_x_down(self, obj, name, new):
        x, y, n = obj.plot.get_x_y_status()
        if x>1:
            x -= 1
        else:
            x = n
        obj.plot.set_x_y_pc(x, y)

    @on_trait_change('y_up')
    def pc_axis_y_up(self, obj, name, new):
        x, y, n = obj.plot.get_x_y_status()
        if y<n:
            y += 1
        else:
            y = 1
        obj.plot.set_x_y_pc(x, y)

    @on_trait_change('y_down')
    def pc_axis_y_down(self, obj, name, new):
        x, y, n = obj.plot.get_x_y_status()
        if y>1:
            y -= 1
        else:
            y = n
        obj.plot.set_x_y_pc(x, y)

    @on_trait_change('vis_toggle')
    def switch_visibility(self, obj, name, new):
        obj.plot.show_points()

    extra_gr = Group(
        Item('x_down', show_label=False),
        Item('x_up', show_label=False),
        Item('reset_xy', show_label=False),
        Item('y_up', show_label=False),
        Item('y_down', show_label=False),
        Item('eq_axis', label="Orthonormal axis"),
        Item('show_labels', label="Show labels"),
        Item('vis_toggle', show_label=False, defined_when='vistog'),
        orientation="horizontal",
        visible_when='show_extra',
        )


class MultiPlotWindow(PlotWindow):
    pass


class OverviewPlotWindow(MultiPlotWindow):
    """Window for embedding multiple plots

    Set plots.component_grid with list of plots to add the plots
    Set plots.shape to tuple(rows, columns) to indicate the layout of the plots

    """
    plots = Instance(Component)
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
             editor=ComponentEditor(
                 size = size,
                 bgcolor = bg_color),
             show_label=False),
        Group(
            Item('show_labels', label="Show labels"),
            orientation = "vertical"),
        resizable=True,
        handler=PWC(),
        # kind = 'nonmodal',
        width = .5,
        height = .7,
        buttons = ["OK"]
        )

    def _plots_default(self):
        container = GridPlotContainer(background=bg_color)
        return container



class FileEditor(HasTraits):
    
    file_name = File()
    
    def _save_img(self, obj):
        """ Attaches a .png extension and exports the image.
        """
        a,b,c = self.file_name.rpartition('.')
        if c == 'png':
            obj.plot.export_image(self.file_name)
        else:
            self.file_name = '{}.png'.format(self.file_name)
            obj.plot.export_image(self.file_name)


    def _save_as_img(self, obj):
        """ Used to browse to a destination folder, and specify a filename for the image.
        """
        fd = FileDialog(action='save as',default_path=self.file_name, default_filename='test.png',
            wildcard = "PNG files (*.png)|*.png|")
        if fd.open() == OK:
            self.file_name = fd.path
            if self.file_name != '':
                self._save_img(obj)




if __name__ == '__main__':
    import numpy as np
    from tests.conftest import clust1ds

    mydata = clust1ds()
    plot = PCScatterPlot(mydata)
    pw = PCPlotWindow(plot=plot)

    with np.errstate(invalid='ignore'):
        pw.configure_traits()
