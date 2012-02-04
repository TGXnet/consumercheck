
from numpy import array
import numpy as np

# Enthought library imports
from chaco.api import Plot, ArrayPlotData, DataLabel
from chaco.tools.api import ZoomTool, PanTool
from traits.api import Bool, Int, List, HasTraits
from enable.api import ColorTrait


class PCDataSet(HasTraits):
    """Metadata for a PC array

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

    pc_ds = List(PCDataSet)
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
    """A specialized class for plotting Principal Component scatterplot type plots"""

    # Is all the labels visible or not
    visible_labels = Bool(True)


    def __init__(self, pc_matrix=None, pc_labels=None, **kwtraits):
        data = PCPlotData()
        super(CCScatterPCPlot, self).__init__(data, **kwtraits)
        self.tools.append(PanTool(self))
        self.overlays.append(ZoomTool(self, tool_mode="box",always_on=False))


    def add_PC_set(self, matrix, labels=None, color='cyan'):
        """Add a PC dataset with metadata"""
        matrix_t = matrix.transpose()
        set_id = self.data.add_PC_set(matrix_t, labels, color)
        self._plot_PC(set_id)


    def show_points(self, set_id, show=True):
        """Shows or hide datapoints for selected PC set"""


    def show_labels(self, set_id, show=True):
        """Shows or hide datapoint labels for selected PC set"""
        self.visible_labels = show
        pn = 'plot_{}'.format(set_id)
        plot = self.plots[pn][0]
        for lab in plot.overlays:
            lab.visible = show
        plot.request_redraw()


    def get_x_y_status(self):
        """Which PC is ploted for X and Y axis

        Returns a tuple (x_no, y_no, n_pc) with:
        * PC no for X axis
        * PC no for Y axis
        * max no of PC's
        """
        return (self.data.x_no, self.data.y_no, self.data.n_pc)


    def set_x_y_pc(self, x, y):
        """Change PC for X and Y axis

        Parameters:
        * PC index for X axis
        * PC index for Y axis
        """

        n_ds = len(self.data.pc_ds)

        plot_ids = ['plot_{}'.format(i+1) for i in range(n_ds)]
        self.delplot(*plot_ids)

        for i in range(n_ds):
            self._plot_PC(i+1, PCx=x, PCy=y)

        self.request_redraw()


    def _plot_PC(self, set_id, PCx=1, PCy=2):
        """Draw the points for a selected dataset and selecte PC for x and y axis"""

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
        rl = self.plot(
            pd,
            type='scatter',
            name=pn,
            color=self.data.pc_ds[set_id-1].color)

        # Set axis title
        self.x_axis.title = 'PC{}'.format(PCx)
        self.y_axis.title = 'PC{}'.format(PCy)

        #adding data labels
        self._add_plot_data_labels(rl[0], pd, set_id)

        return pn


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


if __name__ == '__main__':
    errset = np.seterr(all="ignore")
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
    plot.plot_circle(True)
    # plot.show_labels(2, show=False)
    plot.new_window(True)
    np.seterr(**errset)
