"""ConsumerCheck plots

To use this module.
Make a ArrayPlotData object where the dataset have the following names:

PlotScatter
pc1 and pc2

PlotCorrLoad
pc1 and pc2

PlotLine
index, pc_sigma

"""
import numpy as np

# Enthought library imports
#from traits.api import HasTraits, Instance, Array, Str, List, Bool
from chaco.api import Plot, PlotGrid, DataLabel, PlotGraphicsContext
from chaco.tools.api import PanTool, ZoomTool


class CCBasePlot(Plot):
    """Plot configuration.

    Dictionary where key is pt_name and value is pt_data.
    pt_data i a 2 value tuple where first value is index in ArrayPlotData
    and second value is color for this dataset points.
    Color is either specified by name or like
    (0.5, 0.5, 0.5, 0.2) (R, G, B, Alpha)

    """

    label_refs = {}
    meta_plots = {}

    def __init__(self, *args, **kw):
        super(CCBasePlot, self).__init__(*args, **kw)
        self._customize_settings()
        self._add_plots()

    def _customize_settings(self):
        self.line_width = 0.5
        self.padding = 54

    def _add_plots(self):
        for pt_name, pt_data in self.meta_plots.iteritems():
            pt_index, pt_color = pt_data
            self._add_plot(pt_name, pt_index, pt_color)

    def export_image(self, fname):
        gc = PlotGraphicsContext(self.outer_bounds)
        gc.render_component(self)
        gc.save(fname)


class CCBasePlotScatter(CCBasePlot):
    def __init__(self, *args, **kw):
        super(CCBasePlotScatter, self).__init__(*args, **kw)
        self._add_zero_axis()
        self._add_tools()
        self._calc_box()

    # FIXME: Move to base and rename to scatterplot
    def _add_plot(self, pt_name, pt_index, pt_color):
        self.plot(
            pt_index, name=pt_name,
            type="scatter", index_sort="ascending",
            marker="dot", marker_size=3,
            color=pt_color, bgcolor="white")

    def _add_tools(self):
        self.tools.append(PanTool(self))
        zoom = ZoomTool(self, tool_mode="box", always_on=False)
        self.overlays.append(zoom)

    def _add_zero_axis(self):
        xgrid = PlotGrid(
            mapper=self.x_mapper,
            orientation='vertical',
            line_weight=1,
            grid_interval=10,
            component=self,
            ## data_min=6,
            ## data_max=9,
            ## transverse_bounds=(-0.4, 0),
            ## transverse_mapper=self.y_mapper
            )
        self.underlays.append(xgrid)
        ygrid = PlotGrid(
            mapper=self.y_mapper,
            orientation='horizontal',
            line_weight=1,
            grid_interval=10,
            component=self,
            ## data_min=-0.4,
            ## data_max=0,
            ## transverse_bounds=(6, 9),
            ## transverse_mapper=self.x_mapper
            )
        self.underlays.append(ygrid)

    def set_eq_axis(self):
        """To set the same range on both x and y axis
        """
        # FIXME: check self.plot.aspect_ratio
        # /usr/share/doc/python-chaco/examples/aspect_ratio.py
        xlim, ylim = self._calc_bounds_limits()
        xmin, xmax = xlim
        self.x_mapper.range.set_bounds(xmin, xmax)
        ymin, ymax = ylim
        self.y_mapper.range.set_bounds(ymin, ymax)

    def _calc_bounds_limits(self, margin_factor=0.15):
        """Calc bounding box for orthonormal plotting.
        """
        for pt_index, pt_color in self.meta_plots.itervalues():
            pt_xdata, pt_ydata = pt_index
            xminmax = (
                min(self.data.get_data(pt_xdata)),
                max(self.data.get_data(pt_xdata)))
            yminmax = (
                min(self.data.get_data(pt_ydata)),
                max(self.data.get_data(pt_ydata)))
            xdelta = xminmax[1] - xminmax[0]
            ydelta = yminmax[1] - yminmax[0]
            delta = max(xdelta, ydelta)
            margin = delta*margin_factor
            delta += margin
            center = (xminmax[0]+xdelta/2, yminmax[0]+ydelta/2)
            xmin = center[0]-delta/2
            xmax = center[0]+delta/2
            ymin = center[1]-delta/2
            ymax = center[1]+delta/2
        return ((xmin, xmax), (ymin, ymax))

    def _calc_box(self, margin_factor=0.15):
        index_min, index_max = self.index_range.low, self.index_range.high
        value_min, value_max = self.value_range.low, self.value_range.high
        index_range = index_max - index_min
        value_range = value_max - value_min
        index_margin = index_range * margin_factor
        value_margin = value_range * margin_factor
        self.value_range.set_bounds(
            value_min-value_margin/2, value_max+value_margin/2)
        self.index_range.set_bounds(
            index_min-index_margin/2, index_max+index_margin/2)

    def reset_axis(self):
        """Reset axix to default
        """
        self.x_mapper.range.reset()
        self.y_mapper.range.reset()

    def add_data_labels(self, labels, ds_id='x1'):
        """Add labels to datapoints

        Datapoint set names:
        x1, x2, x3, y2
        
        """
        pt_index, pt_color = self.meta_plots[ds_id]
        xname, yname = pt_index
        ref = self.label_refs[ds_id] = []
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
                text_color = pt_color,
                border_visible = False,
                marker_visible = False,
                bgcolor = (0.5, 0.5, 0.5, 0.2),
#                bgcolor = 'transparent',
                )
            ref.append(label_obj)
            self.overlays.append(label_obj)

    def switch_labels_visibility(self, ds_id, is_visible):
        sel_set = self.label_refs[ds_id]
        for label in sel_set:
            label.visible = is_visible
        self.request_redraw()

    def toggle_eq_axis(self, is_eq_axis):
        if is_eq_axis:
            self.set_eq_axis()
        else:
            self._calc_box()
            # self.reset_axis()
        self.request_redraw()


class CCPlotScatter(CCBasePlotScatter):
    """This is a specialization of the Plot class for convenience

    This have to be instantiated with an ArrayPlotData object.
    Where data key names is *pc_x* and *pc_y*.
    Other values to set:
    title
    [x|y]_axis.title

    The intended use of this plots is PC scatter plot.
    """
    meta_plots = {
        'x1': (('pc1', 'pc2'), 'orange'), # (0.451, 0.137, 0.459, 1)
        }


class CCPlotCorrLoad(CCBasePlotScatter):
    """Convenient correlation loading plotting

    This plots takes data for ploting 2 ellipses.

    This have to be instantiated with an ArrayPlotData object.
    Where data key names is *pc_x* and *pc_y* for PC data.
    ell_full_x and ell_full_y for full ellipse.
    ell_half_x and ell_half_y for half ellipse.
    Other values to set:
    title
    [x|y]_axis.title

    The intended use of this plots is PC scatter plot.
    """
    meta_plots = {
        'x1': (('pc1', 'pc2'), 'orange'), # (0.451, 0.137, 0.459, 1)
        }

    def __init__(self, *args, **kw):
        super(CCPlotCorrLoad, self).__init__(*args, **kw)
        self._add_circle(True)
        self._calc_box()
        # self.set_eq_axis()

    def _add_circle(self, show_half=False):
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


class CCPlotXYCorrLoad(CCPlotCorrLoad):
    """Convenient correlation loading plotting

    This plots takes data for ploting 2 ellipses.

    This have to be instantiated with an ArrayPlotData object.
    Where data key names is *pc_x* and *pc_y* for PC data.
    ell_full_x and ell_full_y for full ellipse.
    ell_half_x and ell_half_y for half ellipse.
    Other values to set:
    title
    [x|y]_axis.title

    The intended use of this plots is PC scatter plot.
    """
    meta_plots = {
        'x1': (('pc1', 'pc2'), 'orange'), # (0.451, 0.137, 0.459, 1)
        'y1': (('pcy1', 'pcy2'), 'red'),
        }

    def switch_labels_visibility(self, ds_id, is_visible):
        super(CCPlotXYCorrLoad, self).switch_labels_visibility('x1', is_visible)
        super(CCPlotXYCorrLoad, self).switch_labels_visibility('y1', is_visible)


class CCPlotLine(CCBasePlot):
    """This is a specialization of the Plot class for convenience

    This have to be instantiated with an ArrayPlotData object.
    Where data key names is *index* and *y_val*.
    Other values to set:
    title
    [x|y]_axis.title
    [x|y]mapper.range.set_bounds(lo, hi)

    The intended use of this plot is PCA explained variance.
    """
    meta_plots = {
        'x1': (('index', 'pc_sigma'), 'orange') # (0.451, 0.137, 0.459, 1)
        }

    # FIXME: Move to base an rename to add line plot
    def _add_plot(self, pt_name, pt_index, pt_color):
        self.plot(
            pt_index, name=pt_name,
            type="line", index_sort="ascending",
            marker="dot", marker_size=3,
            color=pt_color, bgcolor="white")


class CCPlotCalValExplVariance(CCBasePlot):
    """This is a specialization of the Plot class for convenience

    This have to be instantiated with an ArrayPlotData object.
    Where data key names is *index* and *y_val*.
    Other values to set:
    title
    [x|y]_axis.title
    [x|y]mapper.range.set_bounds(lo, hi)

    The intended use of this plot is PCA explained variance.
    """
    meta_plots = {
        'x1': (('index', 'pc_cal_sigma'), 'orange'), # (0.451, 0.137, 0.459, 1)
        'x2': (('index', 'pc_val_sigma'), 'red'), # (0.451, 0.137, 0.459, 1)
        }

    # FIXME: Move to base an rename to add line plot
    def _add_plot(self, pt_name, pt_index, pt_color):
        self.plot(
            pt_index, name=pt_name,
            type="line", index_sort="ascending",
            marker="dot", marker_size=3,
            color=pt_color, bgcolor="white")



if __name__ == '__main__':
    from chaco.api import ArrayPlotData
    from plot_windows import SinglePlotWindow
    
    x1 = [-0.2, 0.4, 0.4]
    y1 = [-0.8, -0.6, 0.4]
    ## x1 = [-2.0, -1.0, -1.25]
    ## y1 = [-0.3, -0.2, -0.1]
    pd = ArrayPlotData(
        pc1=x1,
        pc2=y1,
        )
    plot = CCPlotScatter(pd)
    labels1 = ['x11', 'x12', 'x13']
    plot.add_data_labels(labels1, 'x1')
    spw = SinglePlotWindow(plot=plot)
    spw.configure_traits()
    # spw.edit_traits()
