# Enthought library imports
from chaco.api import Plot, ArrayPlotData, DataLabel
from numpy import array
from traits.api import Int, List, HasTraits
import numpy as np



class PCDataSet(HasTraits):
    """Metadata for a PC array

    * A list of labels for each datapoint
    """
    labels = List()
    label_ref = List()
    selected = List()


class PCPlotData(ArrayPlotData):
    """Container for Principal Component scatterplot type dataset.

    This container will be able to hold several sets of PC type datasets:
     * The actual matrix with PC1 to PCn
     * A list of PCDataSet objects that holds metadata for each PC matrix
    """
    # arrays:     {} Map of names to arrays.
    # selectable: True Can consumers (Plots) set selections?
    # writable:   True Can consumers (Plots) write data back
    # through this interface using set_data()?
    # from abstract_plot_data import AbstractPlotData

    ds_counter = Int(0)
    pc_ds = List(PCDataSet)

    def add_PC_set(self, values, labels=None):
        """Add a PC dataset with metadata"""

        for row in range(len(values)):
            dict_name = 's{}pc{}'.format(self.ds_counter+1,(row+1))
            self.arrays[dict_name] = values[row]

        self.pc_ds.append(PCDataSet())
        self.pc_ds[self.ds_counter].labels = labels

        self.ds_counter += 1

        return self.ds_counter

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


    def add_PC_set(self, matrix, labels=None, color='blue'):
        """Add a PC dataset with metadata"""
        set_id = self.data.add_PC_set(matrix, labels)
        plot_name = self._plot_PC(set_id, color, labels)
        

    def _add_data_labels(self, labels, bg_color, point_data, set_id):
        xname, yname = point_data
        
        f = self.data.pc_ds[set_id-1].label_ref
        for i, label in enumerate(labels):
            # label attributes: text_color, border_visible, overlay_border,
            # marker_visible, invisible_layout, bgcolor
            label_obj = DataLabel(
                component = self,
                data_point = (
                    self.data.get_data(xname)[i],
                    self.data.get_data(yname)[i]),
                label_format = label,
#                marker_color = pt_color,
                text_color = 'black',
                border_visible = False,
                marker_visible = False,
                bgcolor = bg_color,
#                bgcolor = 'transparent',
                )

            f.append(label_obj)
            self.overlays.append(label_obj)
    
    def _plot_PC(self, set_id, color='blue', labels=None, PCx=1, PCy=2):
        """Draw the points for a selected dataset and selecte PC for x and y axis"""
        # Typical id: ('s1pc1', 's1pc2')
        x_id = 's{}pc{}'.format(set_id, PCx)
        y_id = 's{}pc{}'.format(set_id, PCy)
        # plot definition
        pd = (x_id, y_id)
        #adding data labels
        self._add_data_labels(labels, color, pd, set_id)
        
        # plot name
        pn = 'plot_{}'.format(set_id)
        rl = self.plot(pd,
                       type='scatter',
                       name=pn,
                       color=color)
        return pn


    def show_points(self, set_id, show=True):
        """Shows or hide datapoints for selected PC set"""

    def show_labels(self, set_id, show=True):
        """Shows or hide datapoint labels for selected PC set"""
        for i in self.data.pc_ds[set_id-1].label_ref:
            i.visible = show
        self.request_redraw()


if __name__ == '__main__':
    plot = CCScatterPCPlot()
    
    set1 = array([
        [-0.3, 0.4, 0.9],
        [-0.1, 0.2, 0.7],
        [-0.1, 0.1, 0.1],
        ])

    set2 = array([
        [-1.3, -0.4, -0.9],
        [-1.1, -0.2, -0.7],
        [-1.2, -0.1, -0.1],
        ])
    
    label1 = ['s1pt1', 's1pt2', 's1pt3']
    label2 = ['s2pt1', 's2pt2', 's2pt3']
    plot.add_PC_set(set1, color=(0.8, 0.2, 0.1, 1.0), labels=label1)
    plot.add_PC_set(set2, color=(0.2, 0.9, 0.1, 1.0), labels=label2)
    # plot.show_labels(2, show=False)
    plot.new_window(True)
