"""Plotting stand alone windows

"""
import os.path

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, Bool, Dict, Str, File,List, Button, on_trait_change
from traitsui.api import View, Group, Item, Label, Handler
from chaco.api import GridPlotContainer
from pyface.api import FileDialog, OK
from enable.savage.trait_defs.ui.svg_button import SVGButton

#Local imports
from ui_results import TableViewController

#===============================================================================
# Attributes to use for the plot view.
size = (850, 650)
bg_color="white"
#===============================================================================

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
    show_labels = Bool(True)
    view_table = Button('View result table')
    save_plot = Button('Save plot image')

    x_up = Button('X+')
    x_down = Button('X-')
    y_up = Button('Y+')
    y_down = Button('Y-')
    reset_xy = Button('Reset axis')
    
    title_text = Str("ConsumerCheck")

    @on_trait_change('show_labels')
    def switch_labels(self, obj, name, new):
        for i in range(len(obj.plot.data.pc_ds)):
            obj.plot.show_labels(i+1, new)

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

    @on_trait_change('view_table')
    def show_table(self, obj, name, new):
        tvc = TableViewController(model=obj.plot)
        tvc.configure_traits()

    @on_trait_change('save_plot')
    def render_plot(self, obj, name, old, new):
        fe = FileEditor()
        fe._save_as_img(obj)

#    #SVG Params
#    width = 32
#    height = 32

#    def _make_svg_btn(self,name):
#        d = SVGButton(
#                      filename=os.path.join(os.path.dirname(__file__),
#                                            '{}.svg'.format(name)),
#                      width=self.width,
#                      height=self.height)
#        return d



#    btn_list = ['save_plot','x_up','x_down','y_down','y_up','reset_xy']
#    btn_dict = Dict()


#    def _btn_dict_default(self):
#        for i in self.btn_list:
#            vars(self)[i] = self._make_svg_btn(i)


    save_plot = SVGButton(
                          filename=os.path.join(os.path.dirname(__file__),
                                                'save.svg'),
                          width=32,
                          height=32)

    y_down = SVGButton(
                            filename=os.path.join(os.path.dirname(__file__),
                                                  'y_down.svg'),
                            width=32,
                            height=32)
    
    y_up = SVGButton(
                            filename=os.path.join(os.path.dirname(__file__),
                                                  'y_up.svg'),
                            width=32,
                            height=32)

    x_down = SVGButton(
                            filename=os.path.join(os.path.dirname(__file__),
                                                  'x_down.svg'),
                            width=32,
                            height=32)

    x_up = SVGButton(
                            filename=os.path.join(os.path.dirname(__file__),
                                                  'x_up.svg'),
                            width=32,
                            height=32)

    reset_xy = SVGButton(
                            filename=os.path.join(os.path.dirname(__file__),
                                                  'reset_xy.svg'),
                            width=32,
                            height=32)





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
                Item('eq_axis', label="Orthonormal axis"),
                Item('show_labels', label="Show labels"),
#                Item('view_table', show_label=False),
                Item('save_plot', show_label=False),
                Item('x_down', show_label=False),
                Item('x_up', show_label=False),
                Item('reset_xy', show_label=False),
                Item('y_up', show_label=False),
                Item('y_down', show_label=False),
                orientation="horizontal",
                ),
            layout="normal",
            ),
        resizable=True,
        handler=TitleHandler(),
        # kind = 'nonmodal',
        buttons = ["OK"]
        )


class LinePlotWindow(HasTraits):
    """Window for embedding line plot

    """
    plot = Instance(Component)
    eq_axis = Bool(False)
    show_labels = Bool(True)
    view_table = Button('View result table')
    title_text = Str("ConsumerCheck")

    @on_trait_change('show_labels')
    def switch_labels(self, obj, name, new):
        ds_id = name.partition('_')[2]
        obj.plot.show_labels(ds_id, new)

    @on_trait_change('eq_axis')
    def switch_axis(self, obj, name, new):
        obj.plot.toggle_eq_axis(new)

    @on_trait_change('view_table')
    def show_table(self, obj, name, new):
        tvc = TableViewController(model=obj.plot)
        tvc.configure_traits()

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
                Item('view_table', show_label=False),
                orientation="horizontal",
                ),
            layout="normal",
            ),
        resizable=True,
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
    show_labels = Bool(True)

    @on_trait_change('show_labels')
    def switch_labels(self, obj, name, new):
        #ds_id = name.partition('_')[2]
        #for i in range(obj.plots.component_grid[0][0].data.ds_counter):
        obj.plots.component_grid[0][0].show_labels(1, new)
        obj.plots.component_grid[0][1].show_labels(1, new)
        obj.plots.component_grid[1][0].show_labels(1, new)

    traits_view = View(
        Group(
            Item('plots',
                 editor=ComponentEditor(
                     size = size,
                     bgcolor = bg_color),
                 show_label=False),
            Item('show_labels', label="Show labels"),
            orientation = "vertical"),
        resizable=True,
        handler=TitleHandler(),
        # kind = 'nonmodal',
        buttons = ["OK"]
        )

    def _plots_default(self):
        container = GridPlotContainer(background=bg_color)
        return container

if __name__ == '__main__':
    a = FileEditor()
    a.configure_traits()