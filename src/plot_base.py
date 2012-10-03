
# Enthought ETS imports
from traits.api import Callable
from chaco.api import Plot


class PlotBase(Plot):
    # The function to call if the plot i double clicked
    dclk_action = Callable()

    def add_dclk_action(self, dclk_action_func):
        self.dclk_action = dclk_action_func


    def normal_left_dclick(self, mouse_event):
        if self.dclk_action:
            self.dclk_action()
