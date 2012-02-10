
from traits.api import Interface


class IPlot(Interface):
    """Interface for ploting objects"""

    def show_labels(set_id=None, show=True):
        """Controls label visibility in plot"""

    def export_image(fname, size=(800, 600)):
        """Save this plot as an image"""


class IPCScatterPlot(IPlot):
    """Interface for scatter type plots for Principal Components"""

    def add_PC_set(matrix, labels=None, color=None, expl_vars=None):
        """Add different sets of plot data to plot window"""


class IEVLinePlot(IPlot):
    """Interface for line type plots for Explained variance."""

    def add_EV_set(ev_vector, color=None, legend=None):
        """Add a line to the plot window"""
