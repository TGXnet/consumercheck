
# SciPy imports
import numpy as np

# Enthought library imports
from chaco.api import Plot, ArrayPlotData
from traits.api import List, HasTraits, implements
from enable.api import ColorTrait
from chaco.tools.api import ZoomTool, PanTool


# Local imports
from plot_interface import IEVLinePlot


class EVDataSet(HasTraits):
    """Metadata for an Explained Variance line plot.

    * A color for each line
    """
    # (0.8, 0.2, 0.1, 1.0)
    color = ColorTrait('darkviolet')


class EVPlotData(ArrayPlotData):
    """Container for an Explained Variance line plot type dataset.

    This container will be able to hold several sets of PC type datasets:
     * The actual data for each line/dataset
     * The name of each plot
    """

    #List with datasets
    l_ds = List(EVDataSet())
    
    #Plot name
    pn = List()


    def add_line_ds(self, values, color):
        """Add dataset for a EV line plot"""
        
        set_n = len(self.l_ds)
        
        try:
            self.arrays['index'] = range(max(len(self.arrays['index']), len(values)))
        except KeyError:
            self.arrays['index'] = range(len(values))
        
        dict_name = 'line_{}'.format(set_n+1)
        self.arrays[dict_name] = values
        
        lds = EVDataSet()
        if color is not None:
            lds.color = color
        self.l_ds.append(lds)
        return set_n+1


class EVLinePlot(Plot):
    """Explained variance line plot.

    """
    implements(IEVLinePlot)

    def __init__(self, ev_vector=None, color=None, legend=None, **kwtraits):
        """Constructor signature.

        :param pc_matrix: Array with PC datapoints
        :type pc_matrix: array

        Args:
          1. pc_matrix: Array with PC datapoints
          2. lables: Labels for the PC datapoints
          3. color: Color used in plot for this PC set
          4. expl_vars: Map with PC to explained variance contribution (%) for PC

        Returns:
          A new created plot object

        """
        data = EVPlotData()
        super(EVLinePlot, self).__init__(data, **kwtraits)

        if ev_vector is not None:
            self.add_EV_set(ev_vector, color, legend)

        self.x_axis.title = "# of principal components"
        self.y_axis.title = "Explained variance [%]"
        self.legend_alignment = 'ul'

        self.tools.append(PanTool(self))
        self.overlays.append(ZoomTool(self, tool_mode="box",always_on=False))


    def add_EV_set(self, ev_vector, color=None, legend=None):
        """Add a PC dataset with metadata.

        Args:
          1. ev_vector: List() with datapoints for a explained variance line
          2. color: Color used in plot for this PC set

        """
        
        #Insert a 0 to start vector in origo
        # ev_vector = np.insert(ev_vector,0,0)
        
        set_id = self.data.add_line_ds(ev_vector, color)
        self._plot_EV(set_id,legend)


    def show_labels(self, set_id=None, show=True):
        pass

    
    def _plot_EV(self, set_id, legend):
        # Adds a EV line plot rendrer to the plot object

        # Typical id: ('s1pc1', 's1pc2')
        y_id = 'line_{}'.format(set_id)
        x_id = 'index'

        # plot definition
        pd = (x_id, y_id)

        # plot name
        if legend is not None:
            pn = legend
            for i in self.data.pn:
                if pn == i:
                    raise Exception("The name: {} is already taken".format(pn))

        else:
            pn = 'Plot {}'.format(set_id)
        
        self.data.pn.append(pn)

        #plot
        rl = self.plot(pd, type='line', name=pn,
                       color=self.data.l_ds[set_id-1].color)

        self.plots.values()[0][0].index._data = self.data.arrays['index']
        
        return pn


if __name__ == '__main__':
    line = np.array([56.4, 78.9, 96.0, 99.4])
    line2 = np.array([26.4, 38.9, 76.0, 79.4, 80.0])
    plot = EVLinePlot()
    plot.add_EV_set(line, legend='Fantastisk')
    plot.add_EV_set(line2, color='blue', legend='Fantastisk Nr. 2')
    plot.legend.visible = True
    plot.new_window(True)
