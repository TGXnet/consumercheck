
# Enthought ETS imports
from traits.api import Callable
from chaco.api import Plot


class PlotBase(Plot):
    # The function to call if the plot i double clicked
    ld_action_func = Callable()
    # Add extra room for y axis
    padding_left = 75


    def add_left_down_action(self, left_down_action_func):
        self.ld_action_func = left_down_action_func


    def normal_left_down(self, mouse_event):
        if self.ld_action_func:
            self.ld_action_func()
