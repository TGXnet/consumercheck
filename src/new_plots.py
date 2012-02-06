"""
PC plot module
--------------

.. moduleauthor:: Thomas Graff <graff.thomas@gmail.com>

"""

from numpy import array
import numpy as np

# Enthought library imports
from chaco.api import Plot, ArrayPlotData, DataLabel
from chaco.tools.api import ZoomTool, PanTool
from traits.api import Bool, Dict, Int, List, HasTraits
from enable.api import ColorTrait


class PCDataSet(HasTraits):
    """Metadata for a PC plot set.

    * A list of labels for each datapoint
    """
    labels = List()
    color = ColorTrait()
    selected = List()


class PCPlotData(ArrayPlotData):
    """Container for Principal Component scatterplot type dataset.

    This container will be able to hold several sets of PC type datasets:
     * The actual matrix with PC1 to PCn
     * A list of PCDataSet objects that holds metadata for each PC matrix
    """

    # Metadata for each PC set
    pc_ds = List(PCDataSet)
    # Explained variance for each PC
    expl_vars = Dict()
    # Number of PC in the datasets
    # Lowest number if we have severals sets
    n_pc = Int()
    # The PC for X the axis
    x_no = Int()
    # The PC for the Y axis
    y_no = Int()


    def add_PC_set(self, values, labels, color):
        """Add a PC dataset with metadata"""

        set_n = len(self.pc_ds)
        rows, cols = values.shape
        if set_n == 0:
            self.n_pc = cols
        else:
            self.n_pc = min(self.n_pc, cols)

        for i,row in enumerate(values):
            dict_name = 's{}pc{}'.format(set_n+1, (i+1))
            self.arrays[dict_name] = row

        pcds = PCDataSet()
        pcds.labels = labels
        pcds.color = color
        self.pc_ds.append(pcds)
        return set_n+1


class CCScatterPCPlot(Plot):
    """Scatter plot principal components.

    Draw scatterplot for one or several sets of principal components.
    *set_x_y_pc()* selects which PC to draw from each of the axis.

    .. note::
       This is a testnote in CCScatterPCPlot class

    """

    # Is all the labels visible or not
    visible_labels = Bool(True)


    def __init__(self, pc_matrix, labels=None, color=None, expl_vars=None):
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
        data = PCPlotData()
        super(CCScatterPCPlot, self).__init__(data)
        ## self.index_range.margin = 0.1
        ## self.value_range.margin = 0.1
        ## self.index_range.tight_bounds = False
        ## self.value_range.tight_bounds = False
        ## scale_tracking_amount(self, multiplier):
        ## set_bounds(self, low, high):
        if expl_vars is not None:
            self.data.expl_vars = expl_vars
        if pc_matrix is not None:
            self.add_PC_set(pc_matrix, labels, color)
        self.tools.append(PanTool(self))
        self.overlays.append(ZoomTool(self, tool_mode="box",always_on=False))


    def add_PC_set(self, matrix, labels=None, color='cyan'):
        """Add a PC dataset with metadata.

        Args:
          1. matrix: Array with PC datapoints
          2. lables: Labels for the PC datapoints
          3. color: Color used in plot for this PC set

        """
        matrix_t = matrix.transpose()
        set_id = self.data.add_PC_set(matrix_t, labels, color)
        self._plot_PC(set_id)


    def show_points(self, set_id, show=True):
        """Shows or hide datapoints for selected PC set."""
        pass


    def show_labels(self, set_id, show=True):
        """Shows or hide datapoint labels for selected PC set."""
        self.visible_labels = show
        pn = 'plot_{}'.format(set_id)
        plot = self.plots[pn][0]
        for lab in plot.overlays:
            lab.visible = show
        plot.request_redraw()


    def get_x_y_status(self):
        """Query which PC is ploted for X and Y axis.

        Returns:
          A tuple (x_no, y_no, n_pc) with:
          1. PC no for X axis
          2. PC no for Y axis
          3. max no of PC's

        """
        return (self.data.x_no, self.data.y_no, self.data.n_pc)


    def set_x_y_pc(self, x, y):
        """Set which PC to plot for X and Y axis.

        Args:
          1. PC index for X axis
          2. PC index for Y axis
          
        """
        n_ds = len(self.data.pc_ds)

        plot_ids = ['plot_{}'.format(i+1) for i in range(n_ds)]
        self.delplot(*plot_ids)

        for i in range(n_ds):
            self._plot_PC(i+1, PCx=x, PCy=y)

        self.request_redraw()


    def _plot_PC(self, set_id, PCx=1, PCy=2):
        # Adds a PC plot rendrer to the plot object

        # Typical id: ('s1pc1', 's1pc2')
        x_id = 's{}pc{}'.format(set_id, PCx)
        y_id = 's{}pc{}'.format(set_id, PCy)

        # FIXME: Value validation
        #sending to metadata for get_x_y_status
        if PCx < 1 or PCx > self.data.n_pc or PCy < 1 or PCy > self.data.n_pc:
            raise Exception(
                "Requested PC x:{}, y:{} for plot axis is out of range:{}".format(
                    PCx, PCy, self.data.n_pc))
        self.data.x_no, self.data.y_no = PCx, PCy

        # plot definition
        pd = (x_id, y_id)

        # plot name
        pn = 'plot_{}'.format(set_id)

        #plot
        rl = self.plot(pd, type='scatter', name=pn,
                       color=self.data.pc_ds[set_id-1].color)

        # Give plot space
        self._set_axis_margin()

        # Set axis title
        self._set_plot_axis_title()

        #adding data labels
        self._add_plot_data_labels(rl[0], pd, set_id)

        return pn


    def _set_plot_axis_title(self):
        try:
            ev_x = self.data.expl_vars[self.data.x_no]
            ev_y = self.data.expl_vars[self.data.y_no]
            self.x_axis.title = 'PC{0} ({1:.0f}%)'.format(self.data.x_no, ev_x)
            self.y_axis.title = 'PC{0} ({1:.0f}%)'.format(self.data.y_no, ev_y)
        except KeyError:
            self.x_axis.title = 'PC{0}'.format(self.data.x_no)
            self.y_axis.title = 'PC{0}'.format(self.data.y_no)


    def _add_plot_data_labels(self, plot_render, point_data, set_id):
        xname, yname = point_data
        x = self.data.get_data(xname)
        y = self.data.get_data(yname)
        labels = self.data.pc_ds[set_id-1].labels
        bg_color = self.data.pc_ds[set_id-1].color
        for i, label in enumerate(labels):
            label_obj = DataLabel(
                component = plot_render,
                data_point = (x[i], y[i]),
                label_format = label,
                visible = self.visible_labels,
                ## marker_color = pt_color,
                text_color = 'black',
                border_visible = False,
                marker_visible = False,
                bgcolor = bg_color,
                ## label_position = 'bottom left',
                ## bgcolor = 'transparent',
                )
            plot_render.overlays.append(label_obj)


    def plot_circle(self, show_half=False):
        """Add bounding circles to the plot."""
        # Create range for ellipses
        vec = np.arange(0.0, 2*np.pi, 0.01)
        # Computing the outer circle (100 % expl. variance)
        xcords100perc = np.cos(vec)
        ycords100perc = np.sin(vec)
        # Computing inner circle
        xcords50perc = 0.707 * np.cos(vec)
        ycords50perc = 0.707 * np.sin(vec)
        self.data.set_data('ell_full_x', xcords100perc)
        self.data.set_data('ell_full_y', ycords100perc)
        self.data.set_data('ell_half_x', xcords50perc)
        self.data.set_data('ell_half_y', ycords50perc)
        # FIXME: Add to meta_plots instead and use that
        self.plot(
            ("ell_full_x", "ell_full_y"), name="ell_full",
            type="line", index_sort="ascending",
            marker="dot", marker_size=1,
            color="blue", bgcolor="white")
        if show_half:
            self.plot(
                ("ell_half_x", "ell_half_y"), name="ell_half",
                type="line", index_sort="ascending",
                marker="dot", marker_size=1,
                color="blue", bgcolor="white")

        self._set_axis_margin()


    def _set_axis_margin(self, margin_factor=0.15):
        self.reset_axis()
        index_bounds = self._calc_margin_bounds(self.index_range.low, self.index_range.high)
        value_bounds = self._calc_margin_bounds(self.value_range.low, self.value_range.high)
        self.index_range.set_bounds(*index_bounds)
        self.value_range.set_bounds(*value_bounds)


    def _calc_margin_bounds(self, low, high, margin_factor=0.15):
        space = high - low
        space_margin = space * margin_factor
        margin_low = low - space_margin / 2
        margin_high = high + space_margin / 2
        return margin_low, margin_high


    def reset_axis(self):
        """Reset axix to default
        """
        self.index_range.reset()
        self.value_range.reset()




if __name__ == '__main__':
    errset = np.seterr(all="ignore")

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
    plot = CCScatterPCPlot(set1, labels=label1, color=(0.8, 0.2, 0.1, 1.0))
    plot.add_PC_set(set2, labels=label2, color=(0.2, 0.9, 0.1, 1.0))
    plot.plot_circle(True)
    # plot.show_labels(2, show=False)
    plot.new_window(True)
    np.seterr(**errset)
