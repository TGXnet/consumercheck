'''
PC plot module
--------------

.. moduleauthor:: Thomas Graff <graff.thomas@gmail.com>

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
import os
from os.path import join as pjoin
import numpy as np

# Enthought library imports
from chaco.api import ArrayPlotData, DataLabel, Legend, PlotGrid, PlotGraphicsContext
from chaco.tools.api import ZoomTool, PanTool
from traits.api import (Bool, Button, Int, Instance, List, Long, HasTraits, implements,
                        Property, Range, Str, Unicode, WeakRef, on_trait_change)
from traitsui.api import Item, Group, View, Label, Include, CheckListEditor
from enable.api import ColorTrait, ComponentEditor
from enable.savage.trait_defs.ui.svg_button import SVGButton

# Local imports
import cc_config as conf
from dataset import DataSet, SubSet, VisualStyle, Factor, Level
from plot_base import PlotBase, NoPlotControl
from plot_interface import IPCScatterPlot
from plot_sector import SectorMixin
from scatter_lasso import LassoMixin

#==============================================================================
# Attributes to use for the plot view.
bg_color = "white"
img_path = conf.graphics_path()
#==============================================================================


class PCDataSet(HasTraits):
    """Metadata for a PC plot set.

    * A list of labels for each datapoint
    """
    labels = List()
    # colors: chocolate, blue, brown, coral, darkblue, darkcyan, darkgoldenrod,
    # darkgreen, darkolivegreen, darkorange, darksalmon, darkseagreen
    # from: /usr/share/pyshared/enable/colors.py
    color = ColorTrait('darkviolet')
    expl_vars = List()
    selected = List()
    pc_ds = DataSet()


class PCPlotData(ArrayPlotData):
    """Container for Principal Component scatterplot type data set.

    This container will be able to hold several sets of PC type data sets:
     * The actual matrix with PC1 to PCn
     * A list of PCDataSet objects that holds metadata for each PC matrix
    """

    # Metadata for each PC set
    plot_data = List(PCDataSet)
    group_names = List([''])
    plot_group = Unicode('')
    coloring_factor = Instance(Factor)
    # Number of PC in the data sets
    # Lowest number if we have severals sets
    n_pc = Long()
    # The PC for X the axis
    x_no = Int()
    # The PC for the Y axis
    y_no = Int()


    def add_PC_set(self, pc_ds, expl_vars, factor=None):
        """Add a PC data set with metadata"""
        set_n = len(self.plot_data)

        if set_n == 0:
            self.n_pc = pc_ds.n_vars
        else:
            self.n_pc = min(self.n_pc, pc_ds.n_vars)

        values = pc_ds.values.transpose()
        for j, row in enumerate(values):
            dict_name = 's{}pc{}'.format(set_n+1, (j+1))
            self.arrays[dict_name] = row

        # if factor is not None:
        #     self.coloring_factor = factor

        if len(pc_ds.subs) > 0:
            # FIXME: replaced by update_color_level_data()
            for gn in pc_ds.get_subset_groups():
                self.group_names.append(gn)
                subsets = pc_ds.get_subsets(gn)
                for ss in subsets:
                    sarray = pc_ds.get_subset_rows(ss)
                    values = sarray.values.transpose()
                    for j, row in enumerate(values):
                        dict_name = 's{}pc{}g{}c{}'.format(set_n+1, (j+1), gn, ss.id)
                        self.arrays[dict_name] = row
                    pass
                pass
            pass

        labels = pc_ds.obj_n
        color = pc_ds.style.fg_color

        pcds = PCDataSet()
        if labels is not None:
            pcds.labels = labels
        if color is not None:
            pcds.color = color
        if expl_vars is not None:
            pcds.expl_vars = list(expl_vars.mat.xs('calibrated'))
        if pc_ds is not None:
            pcds.pc_ds = pc_ds
        self.plot_data.append(pcds)

        return set_n+1


    def update_color_level_data(self, set_id):
        '''To handle added level data to the active coloring_factor

        Will run throug the levels and create new datasources for each of the levels.
        Also hav to delet the old data source or check if it already exist

        Heuristics:
        Must indicate which dataset to copy values from. Can check if the size of
        the wanted axis index for the dataset is lager than the largest index in the Factor
        '''

        if self.coloring_factor is not None:
            self.coloring_factor.default_ds_axis = 'row'
            # Assumes rows with obj and col with PC
            pdata = self.plot_data[set_id-1]
            pcds = pdata.pc_ds
            facname = self.coloring_factor.name

            for lvn in self.coloring_factor.levels:
                # get the subset row data for this level
                submx = self.coloring_factor.get_values(pcds, lvn)
                selT = submx.T
                # enumerate values to get the various PC vectors (one row for each PC)
                for i, pcvec in enumerate(selT, 1):
                    # Create keynames for vectors
                    # 'ds{}fc{}lv{}pc{}' ds nummer, factor name, level name, PC nummer
                    kn = "ds{0}:fc{1}:lv{2}:pc{3}".format(set_id, facname, lvn, i)
                    # intert key-vector into plot data array or update if data already exist
                    self.arrays[kn] = pcvec
            # Create datasorce for the points not in a level
            submx = self.coloring_factor.get_rest_values(pcds)
            selT = submx.T
            for i, pcvec in enumerate(selT, 1):
                # Create keynames for vectors
                # 'ds{}fc{}lv{}pc{}' ds nummer, factor name, level name, PC nummer
                kn = "ds{0}:fc{1}:lv{2}:pc{3}".format(set_id, facname, 'not', i)
                # intert key-vector into plot data array or update if data already exist
                self.arrays[kn] = pcvec



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
    draw_correlation_circles = Bool(False)
    visible_datasets = Int(3)
    plot_data = Property()
    expl_y_vars = List()


    def __init__(self, pc_matrix=None,
                 expl_vars=None, expl_y_vars=None,
                 **kwargs):
        """Constructor signature.

        :param pc_matrix: Array with PC datapoints
        :type pc_matrix: array

        Args:
          1. pc_matrix: Array with PC datapoints
          2. lables: Labels for the PC datapoints
          3. color: Color used in plot for this PC set
          4. expl_vars: Map PC to explained variance contribution (%) for PC

        Returns:
          A new created plot object

        """
        data = PCPlotData()
        super(PCScatterPlot, self).__init__(data, **kwargs)
        self._adjust_range()

        # FIXME: This is a hack to show PC1 X(%), Y(%) for prefmap scores
        if expl_y_vars is not None:
            self.expl_y_vars = list(expl_y_vars.mat.xs('calibrated'))
        self.external_mapping = False
        if pc_matrix is not None:
            factor = kwargs.pop('factor', None)
            self.add_PC_set(pc_matrix, expl_vars, factor)

        self._add_zero_axis()
        self.tools.append(PanTool(self))
        self.overlays.append(ZoomTool(self, tool_mode="box", always_on=False))


    def add_PC_set(self, pc_matrix, expl_vars=None, factor=None):
        """Add a PC data set with metadata.

        Args:
          1. pc_matrix: DataSet with PC datapoints
          2. expl_vars: DataSet with explained variance
        """
        set_id = self.data.add_PC_set(pc_matrix, expl_vars, factor)
        self._plot_PC(set_id)


    def show_points(self):
        """Shows or hide datapoints for PC set."""

        if self.visible_datasets == 3:
            # self.plots['plot_1'][0].visible = False
            self._toggle_points(1, False)
            self.visible_datasets = 2
        elif self.visible_datasets == 2:
            # self.plots['plot_1'][0].visible = True
            # self.plots['plot_2'][0].visible = False
            self._toggle_points(1, True)
            self._toggle_points(2, False)
            self.visible_datasets = 1
        else:
            # self.plots['plot_2'][0].visible = True
            self._toggle_points(2, True)
            self.visible_datasets = 3

            # self.plots['plot_1'][0].request_redraw()
            # self.plots['plot_2'][0].request_redraw()


    def _toggle_points(self, set_id, visible):
        pnl = [pn for pn in self.plots.keys() if 'plot_{}'.format(set_id) in pn]
        for pn in pnl:
            self.plots[pn][0].visible = visible
            self.plots[pn][0].request_redraw()


    def show_labels(self, set_id=None, show=True):
        """Shows or hide datapoint labels for selected PC set."""
        self.visible_new_labels = show
        if set_id is None:
            for sid in range(1, len(self.data.plot_data)+1):
                self._show_set_labels(sid, show)
        else:
            self._show_set_labels(set_id, show)


    def _show_set_labels(self, set_id, show):
        pnl = [pn for pn in self.plots.keys() if 'plot_{}'.format(set_id) in pn]
        for pn in pnl:
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
        plot_ids = self.plots.keys()
        n_ds = len(self.data.plot_data)
        # plot_ids = ['plot_{}'.format(i+1) for i in range(n_ds)]
        self.delplot(*plot_ids)
        for i in range(n_ds):
            self._plot_PC(i+1, PCx=x, PCy=y)
        if self.draw_correlation_circles:
            self.plot_circle(True)
        self.request_redraw()


    def color_subsets_group(self, group=None):
        if group is None:
            self.data.plot_group = ''
        else:
            self.data.plot_group = group

        plot_ids = self.plots.keys()
        x, y, n = self.get_x_y_status()
        n_ds = len(self.data.plot_data)
        self.delplot(*plot_ids)
        for i in range(n_ds):
            self._plot_PC(i+1, PCx=x, PCy=y)
        self.request_redraw()


    def factor_colors(self, factor=None):
        # FIXME: Will replace color_subsets_group()
        pass


    @on_trait_change('data:coloring_factor:levels[]', post_init=False)
    def _update_plot_factor_coloring(self, obj, name, old, new):
        self.data.update_color_level_data(1)
        plot_ids = self.plots.keys()
        x, y, n = self.get_x_y_status()
        n_ds = len(self.data.plot_data)
        self.delplot(*plot_ids)
        ds = self.datasources.keys()
        for k in ds:
            del self.datasources[k]

        for i in range(n_ds):
            self._plot_PC(i+1, PCx=x, PCy=y)
        self.request_redraw()


    def _plot_PC(self, set_id, PCx=1, PCy=2):
        # Adds a PC plot rendrer to the plot object

        # FIXME: Value validation
        # sending to metadata for get_x_y_status
        if PCx < 1 or PCx > self.data.n_pc or PCy < 1 or PCy > self.data.n_pc:
            raise Exception(
                "PC x:{}, y:{} for plot axis is out of range:{}".format(
                    PCx, PCy, self.data.n_pc))

        self.data.x_no, self.data.y_no = PCx, PCy

        markers = ['dot',
                   'square',
                   'triangle',
                   'circle',
                   'inverted_triangle',
                   'cross']

        pdata = self.data.plot_data[set_id-1]
        plots = {}
        if self.data.plot_group:
            # FIXME: To be replace by next elif clause
            group = self.data.plot_group
            subsets = pdata.pc_ds.get_subsets(group)
            for ci, ss in enumerate(subsets):
                # 's{}pc{}g{}c{}'.format(set_n+1, (j+1), gn, ss.id)
                x_id = 's{}pc{}g{}c{}'.format(set_id, PCx, group, ss.id)
                y_id = 's{}pc{}g{}c{}'.format(set_id, PCy, group, ss.id)
                # plot definition
                pd = (x_id, y_id)
                # plot name
                pn = 'plot_{}_class_{}'.format(set_id, ss.id)
                # plot
                rl = self.plot(pd, type='scatter', name=pn,
                               marker=markers[set_id-1 % 5], marker_size=2,
                               color=ss.gr_style.fg_color
                               )
                labels = ss.row_selector
                color = ss.gr_style.fg_color
                self._add_plot_data_labels(rl[0], pd, labels, color)
                plots[ss.name] = rl[0]
            legend = Legend(component=self, plots=plots, padding=10, align="ur")
            self.overlays.append(legend)
        elif self.data.coloring_factor is not None:
            facname = self.data.coloring_factor.name
            for lvn, lv in self.data.coloring_factor.levels.iteritems():
                # "ds{0}:fc{1}:lv{2}:pc{3}".format(set_id, facname, lv.name, i)
                x_id = 'ds{0}:fc{1}:lv{2}:pc{3}'.format(set_id, facname, lvn, PCx)
                y_id = 'ds{0}:fc{1}:lv{2}:pc{3}'.format(set_id, facname, lvn, PCy)
                # plot definition
                pd = (x_id, y_id)
                # plot name
                pn = 'plot_{}_class_{}'.format(set_id, lvn)
                # plot
                rl = self.plot(pd, type='scatter', name=pn,
                               marker=markers[set_id-1 % 5], marker_size=2,
                               color=lv.color
                               )
                labels = lv.get_labels(pdata.pc_ds, axis=0)
                color = lv.color
                self._add_plot_data_labels(rl[0], pd, labels, color)
            # Plot the rest of the points as black
            # "ds{0}:fc{1}:lv{2}:pc{3}".format(set_id, facname, lv.name, i)
            x_id = 'ds{0}:fc{1}:lv{2}:pc{3}'.format(set_id, facname, 'not', PCx)
            y_id = 'ds{0}:fc{1}:lv{2}:pc{3}'.format(set_id, facname, 'not', PCy)
            # plot definition
            pd = (x_id, y_id)
            # plot name
            pn = 'plot_{}_class_{}'.format(set_id, 'not')
            # plot
            rl = self.plot(pd, type='scatter', name=pn,
                           marker=markers[set_id-1 % 5], marker_size=2,
                           color=pdata.color
                           )

            labels = self.data.coloring_factor.get_rest_labels(pdata.pc_ds)
            color = pdata.color
            self._add_plot_data_labels(rl[0], pd, labels, color)
        else:
            # Typical id: ('s1pc1', 's1pc2')
            x_id = 's{}pc{}'.format(set_id, PCx)
            y_id = 's{}pc{}'.format(set_id, PCy)

            # plot definition
            pd = (x_id, y_id)
            # plot name
            pn = 'plot_{}_class_0'.format(set_id)

            # plot
            rl = self.plot(pd, type='scatter', name=pn,
                           marker=markers[set_id-1 % 5], marker_size=2,
                           # color=self.data.plot_data[set_id-1].color
                           )
            # adding data labels
            labels = pdata.labels
            color = pdata.color
            self._add_plot_data_labels(rl[0], pd, labels, color)

        # Add Lasso selection if available
        # my_plot = self.plots["plot_1_class_0"][0]
        if hasattr(self, 'overlay_selection'):
            self.overlay_selection(rl[0])

        # Set axis title
        self._set_plot_axis_title()
        # return pn


    def _set_plot_axis_title(self):
        tx = ['PC{0}'.format(self.data.x_no)]
        ty = ['PC{0}'.format(self.data.y_no)]
        for pcds in self.data.plot_data:
            try:
                ev_x = pcds.expl_vars[self.data.x_no-1]
                ev_y = pcds.expl_vars[self.data.y_no-1]
                tx.append('({0:.0f}%)'.format(ev_x))
                ty.append('({0:.0f}%)'.format(ev_y))
            except IndexError:
                pass
        if self.expl_y_vars is not None:
            try:
                ev_x = self.expl_y_vars[self.data.x_no-1]
                ev_y = self.expl_y_vars[self.data.y_no-1]
                tx.append('({0:.0f}%)'.format(ev_x))
                ty.append('({0:.0f}%)'.format(ev_y))
            except IndexError:
                pass
        if len(tx) == 3:
            self.x_axis.title = tx[0]+' X'+tx[1]+', Y'+tx[2]
            self.y_axis.title = ty[0]+' X'+ty[1]+', Y'+ty[2]
        else:
            self.x_axis.title = ' '.join(tx)
            self.y_axis.title = ' '.join(ty)


    def _add_plot_data_labels(self, plot_render, point_data, labels, color):
        xname, yname = point_data
        x = self.data.get_data(xname)
        y = self.data.get_data(yname)
        for i, label in enumerate(labels):
            label_obj = DataLabel(
                component=plot_render,
                data_point=(x[i], y[i]),
                label_format=unicode(label),
                visible=self.visible_new_labels,
                ## marker_color = pt_color,
                # text_color = 'black',
                text_color=color,
                border_visible=False,
                marker_visible=False,
                # bgcolor = color,
                bgcolor=(0.5, 0.5, 0.5, 0.0),
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


    def export_image(self, fname, size=(800, 600)):
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
        index_bounds = self._calc_margin_bounds(*index_eq_bounds,
                                                margin_factor=margin_factor)
        value_bounds = self._calc_margin_bounds(*value_eq_bounds,
                                                margin_factor=margin_factor)
        self.index_range.set_bounds(*index_bounds)
        self.value_range.set_bounds(*value_bounds)


    def _set_axis_margin(self, margin_factor=0.15):
        self._reset_axis()
        index_tight_bounds = self.index_range.low, self.index_range.high
        value_tight_bounds = self.value_range.low, self.index_range.high
        index_bounds = self._calc_margin_bounds(*index_tight_bounds,
                                                margin_factor=margin_factor)
        value_bounds = self._calc_margin_bounds(*value_tight_bounds,
                                                margin_factor=margin_factor)
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


    def _get_plot_data(self):
        return self.data.plot_data[0].pc_ds


def calc_bounds(data_low, data_high, margin, tight_bounds):
    if tight_bounds:
        return data_low, data_high
    else:
        return data_low * (1 + margin), data_high * (1 + margin)


class ScatterSectorPlot(PCScatterPlot, SectorMixin):
    pass


class SelectionScatterPlot(PCScatterPlot, LassoMixin):
    pass


class IndDiffScatterPlot(PCScatterPlot):

    def _set_plot_axis_title(self):
        tx = ['Component {0}'.format(self.data.x_no)]
        ty = ['Component {0}'.format(self.data.y_no)]
        for pcds in self.data.plot_data:
            try:
                ev_x = pcds.expl_vars[self.data.x_no-1]
                ev_y = pcds.expl_vars[self.data.y_no-1]
                tx.append('({0:.0f}%)'.format(ev_x))
                ty.append('({0:.0f}%)'.format(ev_y))
            except IndexError:
                pass
        if self.expl_y_vars is not None:
            try:
                ev_x = self.expl_y_vars[self.data.x_no-1]
                ev_y = self.expl_y_vars[self.data.y_no-1]
                tx.append('({0:.0f}%)'.format(ev_x))
                ty.append('({0:.0f}%)'.format(ev_y))
            except IndexError:
                pass
        if len(tx) == 3:
            self.x_axis.title = tx[0]+' X'+tx[1]+', Y'+tx[2]
            self.y_axis.title = ty[0]+' X'+ty[1]+', Y'+ty[2]
        else:
            self.x_axis.title = ' '.join(tx)
            self.y_axis.title = ' '.join(ty)


class CLPlot(PCScatterPlot):

    def __init__(self, clx, evx, cly, evy, em, **kwargs):
        super(CLPlot, self).__init__(**kwargs)
        clx.style.fg_color = 'blue'
        self.add_PC_set(clx, evx)
        cly.style.fg_color = 'red'
        self.add_PC_set(cly, evy)
        self.plot_circle(True)
        self.draw_correlation_circles = True
        self.external_mapping = em


class IndDiffCLPlot(IndDiffScatterPlot):

    def __init__(self, clx, evx, cly, evy, em, **kwargs):
        super(IndDiffScatterPlot, self).__init__(**kwargs)
        clx.style.fg_color = 'blue'
        self.add_PC_set(clx, evx)
        cly.style.fg_color = 'red'
        self.add_PC_set(cly, evy)
        self.plot_circle(True)
        self.draw_correlation_circles = True
        self.external_mapping = em


class CLSectorPlot(CLPlot, SectorMixin):
    pass


class IndDiffCLSectorPlot(IndDiffCLPlot, SectorMixin):
    pass


class PCBaseControl(NoPlotControl):
    eq_axis = Bool(False)
    # vis_toggle = Button('Visibility')
    y_down = SVGButton(filename=pjoin(img_path, 'y_down.svg'),
                       width=32, height=32)
    y_up = SVGButton(filename=pjoin(img_path, 'y_up.svg'),
                     width=32, height=32)
    x_down = SVGButton(filename=pjoin(img_path, 'x_down.svg'),
                       width=32, height=32)
    x_up = SVGButton(filename=pjoin(img_path, 'x_up.svg'),
                     width=32, height=32)
    reset_xy = SVGButton(filename=pjoin(img_path, 'reset_xy.svg'),
                         width=32, height=32)
    subset_groups = List()

    traits_view = View(
        Group(
            Item('model', editor=ComponentEditor(bgcolor=bg_color),
                 show_label=False),
            Label('Scroll to zoom and drag to pan in plot.'),
            Include('plot_controllers'),
            orientation="vertical"
        )
    )

    # @on_trait_change('vis_toggle')
    # def switch_visibility(self, obj, name, new):
    #     obj.model.show_points()


    @on_trait_change('eq_axis')
    def switch_axis(self, obj, name, new):
        obj.model.toggle_eq_axis(new)


    @on_trait_change('reset_xy')
    def pc_axis_reset(self, obj, name, new):
        obj.model.set_x_y_pc(1, 2)


    @on_trait_change('x_up')
    def pc_axis_x_up(self, obj, name, new):
        x, y, n = obj.model.get_x_y_status()
        if x < n:
            x += 1
        else:
            x = 1
        obj.model.set_x_y_pc(x, y)


    @on_trait_change('x_down')
    def pc_axis_x_down(self, obj, name, new):
        x, y, n = obj.model.get_x_y_status()
        if x > 1:
            x -= 1
        else:
            x = n
        obj.model.set_x_y_pc(x, y)


    @on_trait_change('y_up')
    def pc_axis_y_up(self, obj, name, new):
        x, y, n = obj.model.get_x_y_status()
        if y < n:
            y += 1
        else:
            y = 1
        obj.model.set_x_y_pc(x, y)


    @on_trait_change('y_down')
    def pc_axis_y_down(self, obj, name, new):
        x, y, n = obj.model.get_x_y_status()
        if y > 1:
            y -= 1
        else:
            y = n
        obj.model.set_x_y_pc(x, y)


class PCPlotControl(PCBaseControl):
    show_labels = Bool(True)
    plot_controllers = Group(
        Item('x_down', show_label=False),
        Item('x_up', show_label=False),
        Item('reset_xy', show_label=False),
        Item('y_up', show_label=False),
        Item('y_down', show_label=False),
        Item('eq_axis', label="Equal scale axis"),
        Item('show_labels', label="Show labels"),
        Item('subset_groups', label="Color subset groups",
             editor=CheckListEditor(name='model.data.group_names')),
        orientation="horizontal",
    )


    @on_trait_change('subset_groups')
    def sel_subset(self, obj, name, new):
        if not new:
            obj.model.color_subsets_group()
        else:
            obj.model.color_subsets_group(new[0])


    @on_trait_change('show_labels')
    def switch_labels(self, obj, name, new):
        obj.model.show_labels(set_id=1, show=new)



class IndDiffPlotControl(PCBaseControl):
    show_labels = Bool(True)
    plot_controllers = Group(
        Item('x_down', show_label=False),
        Item('x_up', show_label=False),
        Item('reset_xy', show_label=False),
        Item('y_up', show_label=False),
        Item('y_down', show_label=False),
        Item('eq_axis', label="Equal scale axis"),
        Item('show_labels', label="Show labels"),
        orientation="horizontal",
    )


    @on_trait_change('show_labels')
    def switch_labels(self, obj, name, new):
        obj.model.show_labels(set_id=1, show=new)



class PCSectorPlotControl(PCBaseControl):
    show_labels = Bool(True)
    add_group = Bool(True)
    draw_sectors = Bool(False)
    plot_controllers = Group(
        Item('x_down', show_label=False),
        Item('x_up', show_label=False),
        Item('reset_xy', show_label=False),
        Item('y_up', show_label=False),
        Item('y_down', show_label=False),
        Item('eq_axis', label="Equal scale axis"),
        Item('show_labels', label="Show labels"),
        Item('draw_sectors', label="Draw segments"),
        Item('model.n_sectors',
             label="Number of segments",
             enabled_when='draw_sectors'),
        orientation="horizontal",
    )


    @on_trait_change('show_labels')
    def switch_labels(self, obj, name, new):
        obj.model.show_labels(set_id=1, show=new)


    @on_trait_change('draw_sectors')
    def switch_sectors(self, obj, name, new):
        obj.model.switch_sectors(new)


    @on_trait_change('model.n_sectors', post_init=True)
    def change_sectors(self, obj, name, new):
        # FIXME: During initialization new is of type ScatterSectorPlot
        if isinstance(new, int):
            obj.remove_sectors()
            obj.draw_sectors(new)


class CLPlotControl(PCBaseControl):
    show_x_labels = Bool(True)
    show_y_labels = Bool(True)
    plot_controllers = Group(
        Item('x_down', show_label=False),
        Item('x_up', show_label=False),
        Item('reset_xy', show_label=False),
        Item('y_up', show_label=False),
        Item('y_down', show_label=False),
        Item('eq_axis', label="Equal scale axis"),
        Item('show_x_labels', label="Show consumer labels"),
        Item('show_y_labels', label="Show sensory labels"),
        orientation="horizontal",
    )


    @on_trait_change('show_x_labels')
    def _switch_x_labels(self, obj, name, new):
        if obj.model.external_mapping:
            obj.model.show_labels(set_id=2, show=new)
        else:
            obj.model.show_labels(set_id=1, show=new)


    @on_trait_change('show_y_labels')
    def _switch_y_labels(self, obj, name, new):
        if obj.model.external_mapping:
            obj.model.show_labels(set_id=1, show=new)
        else:
            obj.model.show_labels(set_id=2, show=new)


class CLSectorPlotControl(PCBaseControl):
    show_x_labels = Bool(True)
    show_y_labels = Bool(True)
    draw_sectors = Bool(False)
    plot_controllers = Group(
        Item('x_down', show_label=False),
        Item('x_up', show_label=False),
        Item('reset_xy', show_label=False),
        Item('y_up', show_label=False),
        Item('y_down', show_label=False),
        Item('eq_axis', label="Equal scale axis"),
        Item('show_x_labels', label="Show consumer labels"),
        Item('show_y_labels', label="Show sensory labels"),
        Item('draw_sectors', label="Draw segments"),
        Item('model.n_sectors',
             label="Number of segments",
             enabled_when='draw_sectors'),
        orientation="horizontal",
    )


    @on_trait_change('show_x_labels')
    def _switch_x_labels(self, obj, name, new):
        if obj.model.external_mapping:
            obj.model.show_labels(set_id=2, show=new)
        else:
            obj.model.show_labels(set_id=1, show=new)


    @on_trait_change('show_y_labels')
    def _switch_y_labels(self, obj, name, new):
        if obj.model.external_mapping:
            obj.model.show_labels(set_id=1, show=new)
        else:
            obj.model.show_labels(set_id=2, show=new)


    @on_trait_change('draw_sectors')
    def switch_sectors(self, obj, name, new):
        obj.model.switch_sectors(new)


    @on_trait_change('model.n_sectors', post_init=True)
    def change_sectors(self, obj, name, new):
        # FIXME: During initialization new is of type ScatterSectorPlot
        if isinstance(new, int):
            obj.remove_sectors()
            obj.draw_sectors(new)


class PCSelectionControl(PCBaseControl):
    show_labels = Bool(True)
    add_segment = Button("Add segment")
    teller = Int(0)
    plot_controllers = Group(
        Item('x_down', show_label=False),
        Item('x_up', show_label=False),
        Item('reset_xy', show_label=False),
        Item('y_up', show_label=False),
        Item('y_down', show_label=False),
        Item('eq_axis', label="Equal scale axis"),
        Item('show_labels', label="Show labels"),
        Item('add_segment', label="Add group"),
        orientation="horizontal",
    )


    @on_trait_change('show_labels')
    def switch_labels(self, obj, name, new):
        obj.model.show_labels(set_id=1, show=new)


    @on_trait_change('add_segment')
    def _(self, obj, name, new):
        self.teller += 1
        lvn = "Segment {}".format(self.teller)
        mask = self.model.index_datasource.metadata['selection']
        ds = self.model.data.plot_data[0].pc_ds
        uidx = self.model.data.coloring_factor._get_nonleveled(ds, 0)
        # print("Lengde", len(mask), len(uidx))
        # lv = Level(np.where(mask)[0], lvn)
        lv = Level(np.array(uidx)[mask], lvn)
        self.model.data.coloring_factor.add_level(lv, check_idx="toss_overlaping")
