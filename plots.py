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
#from enthought.traits.api import HasTraits, Instance, Array, Str, List, Bool
from enthought.chaco.api import Plot, PlotGrid, DataLabel
from enthought.chaco.tools.api import PanTool, ZoomTool


class CCBasePlot(Plot):
    label_refs = {}
    meta_plots = {}
    """Plot configuration.

    Dictionary where key is pt_name and value is pt_data.
    pt_data i a 2 value tuple where first value is index in ArrayPlotData
    and second value is color for this dataset points.
    Color is either specified by name or like
    (0.5, 0.5, 0.5, 0.2) (R, G, B, Alpha)

    """
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


class CCBasePlotScatter(CCBasePlot):
    def __init__(self, *args, **kw):
        super(CCBasePlotScatter, self).__init__(*args, **kw)
        self._add_zero_axis()
        self._add_tools()

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
        xlim, ylim = self._calcBoundsLimits()
        self.x_mapper.range.set_bounds(*xlim)
        self.y_mapper.range.set_bounds(*ylim)

    ## def _calcBoundsLimits(self, margin_factor=0.0):
    ##     # Return tuple of tuple with x and y bounds low and high limit
    ##     minLim = None
    ##     maxLim = None
    ##     for pt_index, pt_color in self.meta_plots.itervalues():
    ##         pt_xdata, pt_ydata = pt_index
    ##         xlim = (min(self.data.get_data(pt_xdata)), max(self.data.get_data(pt_xdata)))
    ##         ylim = (max(self.data.get_data(pt_ydata)), max(self.data.get_data(pt_ydata)))
    ##         if minLim:
    ##             minLim = min(xlim[0], ylim[0], minLim)
    ##             maxLim = max(xlim[1], ylim[1], maxLim)
    ##         else:
    ##             minLim = min(xlim[0], ylim[0])
    ##             maxLim = max(xlim[1], ylim[1])
    ##     minLim = minLim - maxLim * margin_factor
    ##     maxLim = maxLim + maxLim * margin_factor
    ##     return ((minLim, maxLim), (minLim, maxLim))

    def _calcBoundsLimits(self, marginFactor=0.1):
        for pt_index, pt_color in self.meta_plots.itervalues():
            pt_xdata, pt_ydata = pt_index
            xMinMax = (min(self.data.get_data(pt_xdata)), max(self.data.get_data(pt_xdata)))
            yMinMax = (min(self.data.get_data(pt_ydata)), max(self.data.get_data(pt_ydata)))
            xDelta = xMinMax[1] - xMinMax[0]
            yDelta = yMinMax[1] - yMinMax[0]
            delta = max(xDelta, yDelta)
            print("Delta: {0}".format(delta))
            margin = delta*marginFactor
            delta += margin
            print("Delta + margin: {0}".format(delta))
            center = (xMinMax[0]+xDelta/2, yMinMax[0]+yDelta/2)
            print("Center: {0}".format(center))
            xMin = center[0]-delta/2
            xMax = center[0]+delta/2
            yMin = center[1]-delta/2
            yMax = center[1]+delta/2
        return ((xMin, xMax), (yMin, yMax))

    def reset_axis(self):
        """Reset axix to default
        """
        self.x_mapper.range.reset()
        self.y_mapper.range.reset()

    def addDataLabels(self, labels, ds_id='x1'):
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
            labelObj = DataLabel(
                component = self,
                data_point = (self.data.get_data(xname)[i], self.data.get_data(yname)[i]),
                label_format = label,
#                marker_color = pt_color,
                text_color = pt_color,
                border_visible = False,
                marker_visible = False,
                bgcolor = (0.5, 0.5, 0.5, 0.2),
#                bgcolor = 'transparent',
                )
            ref.append(labelObj)
            self.overlays.append(labelObj)

    def switchLabellVisibility(self, ds_id, isVisible):
        sel_set = self.label_refs[ds_id]
        for label in sel_set:
            label.visible = isVisible
        self.request_redraw()

    def toggleEqAxis(self, axisEq):
        if axisEq:
            self.set_eq_axis()
        else:
            self.reset_axis()
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

    def __init__(self, *args, **kw):
        super(CCPlotScatter, self).__init__(*args, **kw)
        # self.set_eq_axis()


class CCPlotCorrLoad(CCBasePlotScatter):
    """Specialization of the PlotScatter class customized for convenient correlation loading plotting

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
        self._add_circle()
        # self.set_eq_axis()

    def _add_circle(self, show_half=False):
        # Create range for ellipses
        t = np.arange(0.0, 2*np.pi, 0.01)
        # Computing the outer circle (100 % expl. variance)
        xcords100perc = np.cos(t)
        ycords100perc = np.sin(t)
        # Computing inner circle
        xcords50perc = 0.707 * np.cos(t)
        ycords50perc = 0.707 * np.sin(t)
        self.data.set_data('ell_full_x', xcords100perc)
        self.data.set_data('ell_full_y', ycords100perc)
        self.data.set_data('ell_half_x', xcords50perc)
        self.data.set_data('ell_half_y', ycords50perc)
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
        'x1': (('index', 'pc_sigma'), 'orange'), # (0.451, 0.137, 0.459, 1)
        }

    def __init__(self, *args, **kw):
        super(CCPlotLine, self).__init__(*args, **kw)

    def _add_plot(self, pt_name, pt_index, pt_color):
        self.plot(
            pt_index, name=pt_name,
            type="line", index_sort="ascending",
            marker="dot", marker_size=3,
            color=pt_color, bgcolor="white")


class CCPlotLPLS(CCBasePlotScatter):
    """This is a specialization of the Plot class for convenience

    This have to be instantiated with an ArrayPlotData object.
    Where data key names is *pc_x* and *pc_y*.
    Other values to set:
    title
    [x|y]_axis.title

    The intended use of this plots is PC scatter plot.
    """
    meta_plots = {
        'x1': (('x1PC1', 'x1PC2'), (0.451, 0.137, 0.459, 1)),
        'x2': (('x2PC1', 'x2PC2'), (0.706, 0.345, 0.212, 1)),
        'x3': (('x3PC1', 'x3PC2'), (0.396, 0.631, 0.188, 1)),
        'y2': (('x2PC1scores', 'x2PC2scores'), 'black'),
        }

    def __init__(self, *args, **kw):
        super(CCPlotLPLS, self).__init__(*args, **kw)

    ## def addDataLabels(self, ds_id, labels):
    ##     if ds_id == 'x3':
    ##         self._addValueQCategory(ds_id, labels)
    ##     else:
    ##         super(CCPlotLPLS, self).addDataLabels(ds_id, labels)

    def _addValueQCategory(self, ds_id, labels):
        if len(labels) != 21:
            raise Exception('Wrong number of question i value question set', len(labels), 21)
        
        category_color = {
            'green': (0, 1, 0, 0.3),
            'blue': (0, 0, 1, 0.3),
            'yellow': (1, 1, 0, 0.3),
            'mangenta': (1, 0, 1, 0.3),
            }

        quest_cat = [
            # color, category_text, short_consept_text, full_consept_text
            ('green', 'Openness to change', 'Sdr', 'Self direction'),  # 1
            ('blue', 'Self enhancement', 'Pow', 'Power'),              # 2
            ('yellow', 'Selftranscendense', 'Univ', 'Universalism'),   # 3
            ('blue', 'Self enhancement', 'Pow', 'Power'),              # 4
            ('mangenta', 'Conservation', 'Sec', 'Security'),           # 5
            ('green', 'Openness to change', 'Stim', 'Self direction'), # 6
            ('mangenta', 'Conservation', 'Conf', 'Conformity'),        # 7
            ('yellow', 'Selftranscendense', 'Univ', 'Universalism'),   # 8
            ('yellow', 'Selftranscendense', 'Ben', 'Benevolence'),     # 9
            ('green', 'Openness to change', 'Hed', 'Hedonism'),        # 10
            ('green', 'Openness to change', 'Sdr', 'Self direction'),  # 11
            ('yellow', 'Selftranscendense', 'Ben', 'Benevolence'),     # 12
            ('blue', 'Self enhancement', 'Ach', 'Achievement'),        # 13
            ('mangenta', 'Conservation', 'Sec', 'Security'),           # 14
            ('green', 'Openness to change', 'Stim', 'Self direction'), # 15
            ('mangenta', 'Conservation', 'Conf', 'Conformity'),        # 16
            ('mangenta', 'Conservation', 'Conf', 'Conformity'),        # 17
            ('yellow', 'Selftranscendense', 'Ben', 'Benevolence'),     # 18
            ('yellow', 'Selftranscendense', 'Univ', 'Universalism'),   # 19
            ('mangenta', 'Conservation', 'Trad', 'Tradition'),         # 20
            ('green', 'Openness to change', 'Stim', 'Self direction'), # 21
            ]

        pt_index, pt_color = self.meta_plots[ds_id]
        xname, yname = pt_index
        ref = self.label_refs[ds_id] = []
        for i, quest in enumerate(quest_cat):
            # label attributes: text_color, border_visible, overlay_border,
            # marker_visible, invisible_layout, bgcolor
            labelObj = DataLabel(
                component = self,
                data_point = (self.data.get_data(xname)[i], self.data.get_data(yname)[i]),
                label_format = "{0}-{1}".format(i+1, quest[2]),
                tooltip = quest[3],
                text_color = 'black',
                border_visible = False,
                marker_visible = False,
                bgcolor = category_color[quest[0]]
                )
            ref.append(labelObj)
            self.overlays.append(labelObj)



if __name__ == '__main__':
    from enthought.chaco.api import ArrayPlotData
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
    plot.addDataLabels(labels1, 'x1')
    spw = SinglePlotWindow(plot=plot)
    spw.configure_traits()
