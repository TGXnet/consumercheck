"""
PC plot module
--------------

.. moduleauthor:: Thomas Graff <graff.thomas@gmail.com>

"""

import numpy as np

# Enthought library imports
from chaco.api import ArrayPlotData, DataLabel, PlotGrid, PlotGraphicsContext
from chaco.tools.api import ZoomTool, PanTool
from traits.api import Bool, Int, List, HasTraits, implements
from enable.api import ColorTrait


# Local imports
from dataset import DataSet
from plot_base import PlotBase
from plot_interface import IPCScatterPlot


class PCDataSet(HasTraits):
    """Metadata for a PC plot set.

    * A list of labels for each datapoint
    """
    labels = List()
    # colors: chocolate, blue, brown, coral, darkblue, darkcyan, darkgoldenrod, darkgreen
    # darkolivegreen, darkorange, darksalmon, darkseagreen
    # from: /usr/share/pyshared/enable/colors.py
    color = ColorTrait('darkviolet')
    expl_vars = List()
    selected = List()
    view_data = DataSet()


class PCPlotData(ArrayPlotData):
    """Container for Principal Component scatterplot type dataset.

    This container will be able to hold several sets of PC type datasets:
     * The actual matrix with PC1 to PCn
     * A list of PCDataSet objects that holds metadata for each PC matrix
    """

    # Metadata for each PC set
    pc_ds = List(PCDataSet)
    # Number of PC in the datasets
    # Lowest number if we have severals sets
    n_pc = Int()
    # The PC for X the axis
    x_no = Int()
    # The PC for the Y axis
    y_no = Int()


    def add_PC_set(self, values, labels, color, expl_vars, view_data):
        """Add a PC dataset with metadata"""

        set_n = len(self.pc_ds)
        rows, cols = values.shape
        if set_n == 0:
            self.n_pc = rows
        else:
            self.n_pc = min(self.n_pc, rows)

        for i, row in enumerate(values):
            dict_name = 's{}pc{}'.format(set_n+1, (i+1))
            self.arrays[dict_name] = row

        pcds = PCDataSet()
        if labels is not None:
            pcds.labels = labels
        if color is not None:
            pcds.color = color
        if expl_vars is not None:
            pcds.expl_vars = list(expl_vars.mat.xs('cal'))
        if view_data is not None:
            pcds.view_data = view_data
        self.pc_ds.append(pcds)
        return set_n+1


class PCScatterPlot(PlotBase):
    """Principal Component scatter plot.

    Draw scatterplot for one or several sets of principal components.
    *set_x_y_pc()* selects which PC to draw from each of the axis.

    .. note::
       This is a testnote in PCScatterPlot class

    """
    implements(IPCScatterPlot)

    # Should new labels be visible?
    visible_new_labels = Bool(True)
    visible_datasets = Int(3)


    # def __init__(self, pc_matrix=None, labels=None, color=None, expl_vars=None, view_data=None):
    def __init__(self, pc_matrix=None, expl_vars=None):
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
        super(PCScatterPlot, self).__init__(data)
        self._adjust_range()

        if pc_matrix is not None:
            self.add_PC_set(pc_matrix, expl_vars)

        self._add_zero_axis()
        self.tools.append(PanTool(self))
        self.overlays.append(ZoomTool(self, tool_mode="box", always_on=False))
        

    def add_PC_set(self, pc_matrix, expl_vars=None):
        """Add a PC dataset with metadata.

        Args:
          1. pc_matrix: DataSet with PC datapoints
          2. expl_vars: DataSet with explained variance
        """
        matrix_t = pc_matrix.values.transpose()
        labels = pc_matrix.obj_n
        color = pc_matrix.style.fg_color
        set_id = self.data.add_PC_set(matrix_t, labels, color, expl_vars, pc_matrix)
        self._plot_PC(set_id)


    def show_points(self):
        """Shows or hide datapoints for PC set."""
        
        if self.visible_datasets == 3:
            self.plots['plot_1'][0].visible = False
            self.visible_datasets = 2
        elif self.visible_datasets == 2 :
            self.plots['plot_1'][0].visible = True
            self.plots['plot_2'][0].visible = False
            self.visible_datasets = 1
        else:
            self.plots['plot_2'][0].visible = True
            self.visible_datasets = 3
            
        self.plots['plot_1'][0].request_redraw()
        self.plots['plot_2'][0].request_redraw()



    def show_labels(self, set_id=None, show=True):
        """Shows or hide datapoint labels for selected PC set."""
        self.visible_new_labels = show
        if set_id is None:
            for sid in range(1, len(self.data.pc_ds)+1):
                self._show_set_labels(sid, show)
        else:
            self._show_set_labels(set_id, show)


    def _show_set_labels(self, set_id, show):
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
                       marker='dot', marker_size=2,
                       color=self.data.pc_ds[set_id-1].color,)
        # Set axis title
        self._set_plot_axis_title()
        #adding data labels
        self._add_plot_data_labels(rl[0], pd, set_id)
        return pn


    def _set_plot_axis_title(self):
        tx = ['PC{0}'.format(self.data.x_no)]
        ty = ['PC{0}'.format(self.data.y_no)]
        for pcds in self.data.pc_ds:
            try:
                ev_x = pcds.expl_vars[self.data.x_no-1]
                ev_y = pcds.expl_vars[self.data.y_no-1]
                tx.append('({0:.0f}%)'.format(ev_x))
                ty.append('({0:.0f}%)'.format(ev_y))
            except IndexError:
                pass
        if len(tx)==3:
            self.x_axis.title = tx[0]+' X'+tx[1]+', Y'+tx[2]
            self.y_axis.title = ty[0]+' X'+ty[1]+', Y'+ty[2]
        else:
            self.x_axis.title = ' '.join(tx)  
            self.y_axis.title = ' '.join(ty)           


    def _add_plot_data_labels(self, plot_render, point_data, set_id):
        xname, yname = point_data
        x = self.data.get_data(xname)
        y = self.data.get_data(yname)
        labels = self.data.pc_ds[set_id-1].labels
        color = self.data.pc_ds[set_id-1].color
        for i, label in enumerate(labels):
            label_obj = DataLabel(
                component = plot_render,
                data_point = (x[i], y[i]),
                label_format = str(label),
                visible = self.visible_new_labels,
                ## marker_color = pt_color,
                # text_color = 'black',
                text_color = color,
                border_visible = False,
                marker_visible = False,
                # bgcolor = color,
                bgcolor = (0.5, 0.5, 0.5, 0.1),
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
            color="blue", bgcolor="white",)
        if show_half:
            self.plot(
                ("ell_half_x", "ell_half_y"), name="ell_half",
                type="line", index_sort="ascending",
                marker="dot", marker_size=1,
                color="blue", bgcolor="white",)

        ## self._set_axis_margin()


    def toggle_eq_axis(self, set_equal):
        """Set orthonormal or normal plot range."""
        if set_equal:
            self._set_axis_equal()
        else:
            ## self._set_axis_margin()
            self._reset_axis()
        ## self.request_redraw()


    def export_image(self, fname, size=(800,600)):
        """Save plot as png image."""
        # self.outer_bounds = list(size)
        # self.do_layout(force=True)
        gc = PlotGraphicsContext(self.outer_bounds)
        gc.render_component(self)
        gc.save(fname, file_format=None)


    def _set_axis_equal(self, margin_factor=0.15):
        """For orthonormal ploting"""
        self._reset_axis()
        index_tight_bounds = self.index_range.low, self.index_range.high
        value_tight_bounds = self.value_range.low, self.index_range.high
        xdelta = index_tight_bounds[1] - index_tight_bounds[0]
        ydelta = value_tight_bounds[1] - value_tight_bounds[0]
        delta = max(xdelta, ydelta)
        xcenter = index_tight_bounds[0] + xdelta/2
        ycenter = value_tight_bounds[0] + ydelta/2
        xmin = xcenter - delta/2
        xmax = xcenter + delta/2
        ymin = ycenter - delta/2
        ymax = ycenter + delta/2
        index_eq_bounds = xmin, xmax
        value_eq_bounds = ymin, ymax
        index_bounds = self._calc_margin_bounds(*index_eq_bounds, margin_factor=margin_factor)
        value_bounds = self._calc_margin_bounds(*value_eq_bounds, margin_factor=margin_factor)
        self.index_range.set_bounds(*index_bounds)
        self.value_range.set_bounds(*value_bounds)


    def _set_axis_margin(self, margin_factor=0.15):
        self._reset_axis()
        index_tight_bounds = self.index_range.low, self.index_range.high
        value_tight_bounds = self.value_range.low, self.index_range.high
        index_bounds = self._calc_margin_bounds(*index_tight_bounds, margin_factor=margin_factor)
        value_bounds = self._calc_margin_bounds(*value_tight_bounds, margin_factor=margin_factor)
        self.index_range.set_bounds(*index_bounds)
        self.value_range.set_bounds(*value_bounds)


    def _calc_margin_bounds(self, low, high, margin_factor=0.15):
        space = high - low
        space_margin = space * margin_factor
        margin_low = low - space_margin / 2
        margin_high = high + space_margin / 2
        return margin_low, margin_high


    def _adjust_range(self):
        self.index_range.margin = 0.15
        self.value_range.margin = 0.15
        self.index_range.tight_bounds = False
        self.value_range.tight_bounds = False
        self.index_range.bounds_func = calc_bounds
        self.value_range.bounds_func = calc_bounds


    def _reset_axis(self):
        self.index_range.reset()
        self.value_range.reset()


    def _add_zero_axis(self):
        xgrid = PlotGrid(
            mapper=self.x_mapper,
            orientation='vertical',
            line_weight=1,
            grid_interval=1,
            component=self,
            data_min=-0.5,
            data_max=0.5,
            # transverse_bounds=(-99, 99),
            transverse_mapper=self.y_mapper
            )
        self.underlays.append(xgrid)
        ygrid = PlotGrid(
            mapper=self.y_mapper,
            orientation='horizontal',
            line_weight=1,
            grid_interval=1,
            component=self,
            data_min=-0.5,
            data_max=0.5,
            # transverse_bounds=(-99, 99),
            transverse_mapper=self.x_mapper
            )
        self.underlays.append(ygrid)


def calc_bounds(data_low, data_high, margin, tight_bounds):
    if tight_bounds:
        return data_low , data_high
    else:
        return data_low * (1 + margin) , data_high * (1 + margin)


if __name__ == '__main__':

    set1 = np.array([
        [-0.3, 0.4, 0.9],
        [-0.1, 0.2, 0.7],
        [-0.1, 0.1, 0.1],
        ])

    set2 = np.array([
        [-1.3, -0.4, -0.9],
        #[-1.1, -0.2, -0.7],
        [-1.1, 1, -0.7],
        [-1.2, -0.1, -0.1],
        ])

    label1 = ['s1pt1', 's1pt2', 's1pt3']
    label2 = ['s2pt1', 's2pt2', 's2pt3']
    plot = PCScatterPlot()
    ## plot = PCScatterPlot(set1, labels=label1, color=(0.8, 0.2, 0.1, 1.0))
    plot.add_PC_set(set1, labels=label1, color=(0.8, 0.2, 0.1, 1.0))
    plot.add_PC_set(set2, labels=label2, color=(0.2, 0.9, 0.1, 1.0))
    plot.plot_circle(True)

    with np.errstate(invalid='ignore'):
        plot.new_window(True)
