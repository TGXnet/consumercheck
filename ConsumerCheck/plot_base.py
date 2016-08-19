'''ConsumerCheck
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

# Enthought ETS imports
import traits.api as _traits
import traitsui.api as _traitsui
import chaco.api as _chaco
import enable.api as _enable

#==============================================================================
# Attributes to use for the plot view.
sz_plot_img = (850, 650)
bg_color = "white"
#==============================================================================


class PlotBase(_chaco.Plot):
    # The data set to return when plot window asks for the data to
    # show in table form
    # I have to override this property as well when i override the getter
    plot_data = _traits.Property()
    # The function to call if the plot is double clicked
    ld_action_func = _traits.Callable()
    # Add extra room for y axis
    padding_left = 75

    def add_left_down_action(self, left_down_action_func):
        self.ld_action_func = left_down_action_func

    def normal_left_down(self, mouse_event):
        if self.ld_action_func:
            self.ld_action_func()

    def _get_plot_data(self):
        raise NotImplementedError('plot_data getter is not implemented')

    def get_plot_name(self):
        return self.plot_data.display_name


class BasePlot(_chaco.DataView):

    # Copy from chaco.plot
    # The title of the plot.
    title = _traits.Property()

    # Use delegates to expose the other PlotLabel attributes of the plot title
    title_text = _traits.Delegate("_title", prefix="text", modify=True)

    # The PlotLabel object that contains the title.
    _title = _traits.Instance(_chaco.PlotLabel)

    def __init__(self, *args, **kwargs):
        super(BasePlot, self).__init__(*args, **kwargs)
        self._init_title()

    def _init_title(self):
        self._title = _chaco.PlotLabel(font="swiss 16", visible=False,
                                       overlay_position="top", component=self)

    def __title_changed(self, old, new):
        self._overlay_change_helper(old, new)

    def _set_title(self, text):
        self._title.text = text
        if text.strip() != "":
            self._title.visible = True
        else:
            self._title.visible = False

    def _get_title(self):
        return self._title.text

    def get_plot_name(self):
        return self.plot_data.display_name

    def export_image(self, fname, size=sz_plot_img):
        """Save plot as png image."""
        # self.outer_bounds = list(size)
        # self.do_layout(force=True)
        gc = _chaco.PlotGraphicsContext(self.outer_bounds)
        gc.render_component(self)
        gc.save(fname, file_format=None)


class NoPlotControl(_traitsui.ModelView):
    model = _traits.Instance(_chaco.DataView)
    plot_controllers = _traitsui.Group()
    traits_view = _traitsui.View(
        _traitsui.Group(
            _traitsui.Item('model',
                           editor=_enable.ComponentEditor(bgcolor=bg_color),
                           show_label=False),
            _traitsui.Include('plot_controllers'),
            orientation="vertical"
        )
    )
