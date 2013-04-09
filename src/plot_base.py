
# Enthought ETS imports
from traits.api import Callable, Property
from chaco.api import Plot


class PlotBase(Plot):
    # The dataset to return when plot window asks for the data to show in table form
    # I have to override this property as well when i override the getter
    plot_data = Property()
    # The function to call if the plot is double clicked
    ld_action_func = Callable()
    # Add extra room for y axis
    padding_left = 75


    def add_left_down_action(self, left_down_action_func):
        self.ld_action_func = left_down_action_func


    def normal_left_down(self, mouse_event):
        if self.ld_action_func:
            self.ld_action_func()


    def _get_plot_data(self):
        raise NotImplementedError('plot_data getter is not implemented')
