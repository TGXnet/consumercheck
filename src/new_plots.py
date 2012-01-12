# Enthought library imports
from chaco.api import Plot, ArrayPlotData
from numpy import array
from traits.api import Int


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

    ds_counter = Int(0)

    def add_PC_set(self, values, labels=None, style_color=None):
        """Add a PC dataset with metadata"""
        
        self.ds_counter += 1
        
        for row in range(len(values)):
            dict_name = 's{}pc{}'.format(self.ds_counter,(row+1))
            self.arrays[dict_name] = values[row]

        return 's'+str(self.ds_counter)
    
        
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
    # Default behaviour is to plot first and second PC for each added dataset
    # The __init__ will take data for the first dataset as parameters


    def __init__(self, pc_matrix=None, pc_labels=None, **kwtraits):
        data = PCPlotData()
        super(CCScatterPCPlot, self).__init__(data, **kwtraits)


    def add_PC_set(self, matrix, labels=None):
        """Add a PC dataset with metadata"""
        set_id = self.data.add_PC_set(matrix, labels=None)
        plot_name = self.plot_PC(set_id)


    def plot_PC(self, set_id, PCx=1, PCy=2):
        """Draw the points for a selected dataset and selecte PC for x and y axis"""
        # Typical id: ('s1pc1', 's1pc2')
        x_id = '{}pc{}'.format(set_id, PCx)
        y_id = '{}pc{}'.format(set_id, PCy)
        # plot definition
        pd = (x_id, y_id)
        # plot name
        pn = 'plot_{}'.format(set_id)
        rl = self.plot(pd,
                       type='scatter',
                       name=pn)
        return pn


    def show_points(self, set_id, show=True):
        """Shows or hide datapoints for selected PC set"""


    def show_labels(self, set_id, show=True):
        """Shows or hide datapoint labels for selected PC set"""


if __name__ == '__main__':
    plot = CCScatterPCPlot()
