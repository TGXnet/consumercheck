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

# SciPy imports
import numpy as np

# Enthought library imports
from chaco.api import ArrayPlotData, PlotGraphicsContext
from traits.api import List, HasTraits, implements, Property
from enable.api import ColorTrait
from chaco.tools.api import ZoomTool, PanTool


# Local imports
from dataset import DataSet
from plot_base import PlotBase
from plot_interface import IEVLinePlot


class EVDataSet(HasTraits):
    """Metadata for an Explained Variance line plot.

    * A color for each line
    """
    # (0.8, 0.2, 0.1, 1.0)
    color = ColorTrait('darkviolet')
    view_data = DataSet()



class EVPlotData(ArrayPlotData):
    """Container for an Explained Variance line plot type data set.

    This container will be able to hold several sets of PC type data sets:
     * The actual data for each line/data set
     * The name of each plot
    """

    #List with data sets
    pc_ds = List(EVDataSet())
    
    #Plot name
    pn = List()


    def add_line_ds(self, values, color, view_data=None):
        """Add data set for a EV line plot"""
        
        set_n = len(self.pc_ds)
        
        try:
            self.arrays['index'] = range(max(len(self.arrays['index']), len(values)))
        except KeyError:
            self.arrays['index'] = range(len(values))
        
        dict_name = 'line_{}'.format(set_n+1)
        self.arrays[dict_name] = values
        
        lds = EVDataSet()
        if color is not None:
            lds.color = color
        if view_data is not None:
            lds.view_data = view_data
        self.pc_ds.append(lds)
        return set_n+1



class EVLinePlot(PlotBase):
    """Explained variance line plot.

    """
    implements(IEVLinePlot)

    plot_data = Property()


    def __init__(self, expl_var=None, **kwargs):
        """Constructor signature.

        :param expl_var: Calibrated and validated explained variance for each calculated PC.
        :type pc_matrix: DataSet

        Returns:
          A new created plot object

        """
        data = EVPlotData()
        super(EVLinePlot, self).__init__(data, **kwargs)

        if expl_var is not None:
            # FIXME: Do more inteligente coloring based on the data set.style
            self.add_EV_set(expl_var.mat.xs('calibrated'), 'darkviolet', 'Calibrated', expl_var)
            self.add_EV_set(expl_var.mat.xs('validated'), 'darkgoldenrod', 'Validated', expl_var)

        self.x_axis.title = "# of principal components"
        self.y_axis.title = "Explained variance [%]"
        self.x_axis.tick_interval = 1.0
        self.legend_alignment = 'ul'
        self.legend.visible = True

        self.tools.append(PanTool(self))
        self.overlays.append(ZoomTool(self, tool_mode="box",always_on=False))


    def add_EV_set(self, expl_var, color=None, legend=None, ev_data=None):
        """Add a PC data set with metadata.

        Args:
          1. expl_var: List() with datapoints for a explained variance line
          2. color: Color used in plot for this PC set

        """
        
        cum_expl_var = np.cumsum(np.insert(expl_var.values, 0, 0, axis=0), axis=0)

        set_id = self.data.add_line_ds(cum_expl_var, color, ev_data)
        self._plot_EV(set_id, legend)


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

        line_styles = ['solid', 'dot dash', 'dash', 'dot', 'long dash']

        #plot
        self.plot(pd, type='line', name=pn,
                  color=self.data.pc_ds[set_id-1].color,
                  line_style=line_styles[set_id-1%4])

        self.plots.values()[0][0].index._data = self.data.arrays['index']
        
        return pn


    def _get_plot_data(self):
        return self.data.pc_ds[0].view_data


    def export_image(self, fname, size=(800,600)):
        """Save plot as png image."""
        # self.outer_bounds = list(size)
        # self.do_layout(force=True)
        gc = PlotGraphicsContext(self.outer_bounds)
        gc.render_component(self)
        gc.save(fname, file_format=None)



if __name__ == '__main__':
    import pandas as pd
    cal = np.array([56.4, 78.9, 96.0, 99.4, 99.99])
    val = np.array([26.4, 38.9, 76.0, 79.4, 80.0])
    df = pd.DataFrame([cal, val], index=['calibrated', 'validated'])
    ds = DataSet(mat=df)
    print(ds.mat)

    plot = EVLinePlot(ds)
    # plot.legend.visible = True
    plot.new_window(True)
