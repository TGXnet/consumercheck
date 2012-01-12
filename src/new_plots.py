# Enthought library imports
from chaco.api import Plot, ArrayPlotData


class PCPlotData(ArrayPlotData):
    """Container for Principal Component scatterplot type dataset.

    This container will be able to hold several sets of PC type datasets:
     * The actual matrix with PC1 to PCn
     * A list of labels for each datapoint
     * A color style specification for the dataset
    """
    # arrays:     {} Map of names to arrays.
    # selectable: True Can consumers (Plots) set selections?
    # writable:   True Can consumers (Plots) write data back
    # through this interface using set_data()?
    # from abstract_plot_data import AbstractPlotData

    def add_PC_set(values_matrix, labels_list, set_id_name, style_color):
        """Add a PC dataset with metadata"""

    def list_PC_sets():
        """List the id of each added dataset"""

    def len_PC_set(set_id):
        """The number of datapoint for the selected dataset"""


class CCScatterPCPlot(Plot):
    """A specialized class for plotting Principal Component scatterplot type plots"""
    # data: The PlotData instance that drives this plot.
    # plots = Dict(Str, List): Mapping of plot names to *lists* of plot renderers.
    # title = Property(): The title of the plot.
    # plot() -> list of renderers created in response to this call to plot()
    # delplot(self, *names): Removes the named sub-plots.
    # hideplot(self, *names): Convenience function to sets the named plots to be invisible.
    # showplot(self, *names):
    # new_window(self, configure=False):
    # Convenience function that creates a window containing the Plot
    # from data_view import DataView

    def add_PC_set(self, values, labels):
        """Add a PC dataset with metadata"""

    def plot_PC(self, set_id, PCx=1, PCy=2):
        """Draw the points for a selected dataset and selecte PC for x and y axis"""

    def show_points(self, set_id, show=True):
        """Shows or hide datapoints for selected PC set"""

    def show_labels(self, set_id, show=True):
        """Shows or hide datapoint labels for selected PC set"""
