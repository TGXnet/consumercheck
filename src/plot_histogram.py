
# Std lib imports
import copy

# Scipy imports
import numpy as _np

# ETS imports
import traits.api as _traits
import chaco.api as _chaco

# Local imports
from dataset import DataSet
from utilities import hue_span

class HistPlot(_chaco.DataView):

    ds = _traits.Instance(DataSet)
    row_id = _traits.Any()
    ceiling = _traits.Int()
    head_space = _traits.Float(1.1)
    bars_renderer = _traits.Instance(_chaco.BarPlot)
    plot_data = _traits.Property()


    def __init__(self, ds, row_id):
        super(HistPlot, self).__init__(ds=ds, row_id=row_id)
        self.bars_renderer = self._create_render()
        self.add(self.bars_renderer)
        self._add_axis(self.bars_renderer)
        fraction = self._calc_percentage()
        self._add_data_labels(self.bars_renderer, fraction)


    def render_hist(self, row_id):
        self.row_id = row_id
        self.bars_renderer.value.set_data(self.ds.mat.ix[self.row_id].values)


    def _create_render(self):
        # Create our data sources
        idx = _chaco.ArrayDataSource(_np.arange(self.ds.n_vars))
        vals = _chaco.ArrayDataSource(self.ds.mat.ix[self.row_id].values)

        # Create the index range
        index_range = _chaco.DataRange1D(
            idx, tight_bounds=False, low_setting='auto', margin=0.15)
        index_mapper = _chaco.LinearMapper(range=index_range)

        # Create the value range
        value_range = _chaco.DataRange1D(vals, low_setting=0, high_setting=self.ceiling)
        value_mapper = _chaco.LinearMapper(range=value_range)

        # Create the plot
        bars = _chaco.BarPlot(index=idx, value=vals,
                              value_mapper=value_mapper,
                              index_mapper=index_mapper,
                              line_color='black',
                              fill_color='springgreen',
                              bar_width=0.8, antialias=False)

        return bars


    def _calc_percentage(self):
        hist = self.ds.mat.ix[self.row_id].values
        alt = hist.sum(axis=0)
        pec = hist*100/alt
        return pec


    def _add_data_labels(self, renderer, fraction):
        idx = renderer.index._data
        val = renderer.value._data
        for i, v in enumerate(fraction):
            label = _chaco.DataLabel(
                component = renderer,
                data_point = (idx[i], val[i]),
                label_text = "{}%".format(v),
                marker_visible = False,
                border_visible = False,
                show_label_coords = False,
                bgcolor = (0.5, 0.5, 0.5, 0.0),
                )
            renderer.overlays.append(label)


    def _add_axis(self, renderer):
        left_axis = _chaco.PlotAxis(renderer, orientation='left',
                                    title='Number of consumers')
        bottom_axis = _chaco.LabelAxis(renderer, orientation='bottom',
                                       title='Consumer rating',
                                       positions = range(self.ds.n_vars),
                                       labels = [str(vn) for vn in self.ds.var_n],
                                       tick_interval=1.0,
                                       )
        renderer.underlays.append(left_axis)
        renderer.underlays.append(bottom_axis)


    def _ceiling_default(self):
        top = self.ds.values.max()
        return int(top * self.head_space)


    def new_window(self, configure=False):
        """Convenience function that creates a window containing the Plot

        Don't call this if the plot is already displayed in a window.
        """
        from chaco.ui.plot_window import PlotWindow
        if configure:
            self._plot_ui_info = PlotWindow(plot=self).configure_traits()
        else:
            self._plot_ui_info = PlotWindow(plot=self).edit_traits()
        return self._plot_ui_info


    def _get_plot_data(self):
        nds = copy.deepcopy(self.ds)
        nds.mat = self.ds.mat.transpose()
        return nds


    def export_image(self, fname, size=(800,600)):
        """Save plot as png image."""
        # self.outer_bounds = list(size)
        # self.do_layout(force=True)
        gc = _chaco.PlotGraphicsContext(self.outer_bounds)
        gc.render_component(self)
        gc.save(fname, file_format=None)



class StackedHistPlot(_chaco.DataView):
    '''Plot histogram values for each row stacked on to of each other'''

    ds = _traits.Instance(DataSet)
    stair_ds = _traits.Instance(_chaco.MultiArrayDataSource)
    plot_data = _traits.Property()


    def __init__(self, ds):
        super(StackedHistPlot, self).__init__(ds=ds)
        pec = self._calc_percentage()
        last_renderer = self._render_data(pec)
        self._add_axis(last_renderer)


    def _stair_ds_default(self):
        nums = self.ds.values
        stair = _np.cumsum(nums, axis=1)
        return _chaco.MultiArrayDataSource(stair)


    def _calc_percentage(self):
        hist = self.ds.mat.values
        alt = _np.max(hist.sum(axis=1))
        pec = hist*100/alt
        return pec


    def _render_data(self, pec):
        idx = _chaco.ArrayDataSource(_np.arange(self.ds.n_objs))
        mvals = self.stair_ds

        # Create the index range
        index_range = _chaco.DataRange1D(
            idx, tight_bounds=False, low_setting='auto', margin=0.15)
        index_mapper = _chaco.LinearMapper(range=index_range)

        # Create the value range
        value_range = _chaco.DataRange1D(mvals, tight_bounds=True)
        value_mapper = _chaco.LinearMapper(range=value_range)

        colors = hue_span(mvals.get_value_size())
        bar_names = {}
        for i in range(mvals.get_value_size()-1, -1, -1):
            vals = _chaco.ArrayDataSource(mvals.get_data(axes=i))
            bars = _chaco.BarPlot(index=idx, value=vals,
                                  value_mapper=value_mapper,
                                  index_mapper=index_mapper,
                                  line_color='black',
                                  fill_color=colors[i],
                                  bar_width=0.8, antialias=False)
            name = str(self.ds.var_n[i])
            bar_names[name] = bars
            num = self.ds.mat.values[:,i]
            pecl = pec[:,i]
            self._add_data_labels(bars, num, pecl)
            self.add(bars)
        rvn = bar_names.keys()
        rvn.sort(reverse=True)
        legend = _chaco.Legend(component=self, padding=2, align="ur", labels=rvn)
        legend.plots = bar_names
        self.overlays.append(legend)
        return bars


    def _add_data_labels(self, renderer, fraction, pec):
        idx = renderer.index._data
        val = renderer.value._data
        for i, v in enumerate(fraction):
            if not v:
                continue
            p = pec[i]
            label = _chaco.DataLabel(
                component = renderer,
                data_point = (idx[i], val[i]),
                label_text = "{0}%({1})".format(p, v),
                label_position = 'bottom',
                arrow_visible = False,
                marker_visible = False,
                border_visible = False,
                show_label_coords = False,
                bgcolor = (0.5, 0.5, 0.5, 0.0),
                )
            renderer.overlays.append(label)



    def _add_axis(self, renderer):
        left_axis = _chaco.PlotAxis(renderer, orientation='left',
                                    title='Number of consumers')
        bottom_axis = _chaco.LabelAxis(renderer, orientation='bottom',
                                       title='Consumer preference for samples',
                                       positions = range(self.ds.n_objs),
                                       labels = [str(vn) for vn in self.ds.obj_n],
                                       tick_interval=1.0,
                                       )
        renderer.underlays.append(left_axis)
        renderer.underlays.append(bottom_axis)



    def new_window(self, configure=False):
        """Convenience function that creates a window containing the Plot

        Don't call this if the plot is already displayed in a window.
        """
        from chaco.ui.plot_window import PlotWindow
        if configure:
            self._plot_ui_info = PlotWindow(plot=self).configure_traits()
        else:
            self._plot_ui_info = PlotWindow(plot=self).edit_traits()
        return self._plot_ui_info


    def _get_plot_data(self):
        nds = copy.deepcopy(self.ds)
        nds.mat = self.ds.mat.transpose()
        return nds


    def export_image(self, fname, size=(800,600)):
        """Save plot as png image."""
        # self.outer_bounds = list(size)
        # self.do_layout(force=True)
        gc = _chaco.PlotGraphicsContext(self.outer_bounds)
        gc.render_component(self)
        gc.save(fname, file_format=None)



class BoxPlot(_chaco.DataView):
    '''A box plot

    This plot takes one DataSet as parameter:
    The DataFrame columns must be on the form:
    mean, std, max, min
    '''
    ds = _traits.Instance(DataSet)
    plot_data = _traits.Property()


    def __init__(self, ds):
        super(BoxPlot, self).__init__(ds=ds)
        boxes_renderer = self._create_renderer()
        self.add(boxes_renderer)
        self._add_axis(boxes_renderer)


    def _create_renderer(self):
        # Create our data sources
        bmin = _chaco.ArrayDataSource(self.ds.mat['perc25'].values)
        bmax = _chaco.ArrayDataSource(self.ds.mat['perc75'].values)
        med = _chaco.ArrayDataSource(self.ds.mat['med'].values)
        minv = _chaco.ArrayDataSource(self.ds.mat['min'].values)
        maxv = _chaco.ArrayDataSource(self.ds.mat['max'].values)
        idx = _chaco.ArrayDataSource(_np.arange(self.ds.n_objs))

        # Create the index range
        index_range = _chaco.DataRange1D(idx, tight_bounds=False)
        index_mapper = _chaco.LinearMapper(range=index_range)

        # Create the value range
        value_range = _chaco.DataRange1D(minv, maxv, tight_bounds=False)
        value_mapper = _chaco.LinearMapper(range=value_range)


        # Color defined in enable.colors.color_table
        boxes = _chaco.CandlePlot(index=idx, center_values=med,
                                  bar_min=bmin, bar_max=bmax,
                                  min_values=minv, max_values=maxv,
                                  index_mapper=index_mapper,
                                  value_mapper=value_mapper,
                                  bar_color='springgreen', bar_line_color='black',
                                  center_color='forestgreen', stem_color='black',
                                  line_width=1.0, center_width=5, stem_width=1,
                                  end_cap=False)
        return boxes



    def _add_axis(self, renderer):
        left_axis = _chaco.PlotAxis(renderer, orientation='left',
                                    title='Number of consumers')
        bottom_axis = _chaco.LabelAxis(renderer, orientation='bottom',
                                       title='Samples',
                                       positions = range(self.ds.n_objs),
                                       labels = [str(vn) for vn in self.ds.obj_n],
                                       tick_interval=1.0,
                                       )
        renderer.underlays.append(left_axis)
        renderer.underlays.append(bottom_axis)



    def new_window(self, configure=False):
        """Convenience function that creates a window containing the Plot

        Don't call this if the plot is already displayed in a window.
        """
        from chaco.ui.plot_window import PlotWindow
        if configure:
            self._plot_ui_info = PlotWindow(plot=self).configure_traits()
        else:
            self._plot_ui_info = PlotWindow(plot=self).edit_traits()
        return self._plot_ui_info


    def _get_plot_data(self):
        nds = copy.deepcopy(self.ds)
        nds.mat = self.ds.mat.transpose()
        return nds


    def export_image(self, fname, size=(800,600)):
        """Save plot as png image."""
        # self.outer_bounds = list(size)
        # self.do_layout(force=True)
        gc = _chaco.PlotGraphicsContext(self.outer_bounds)
        gc.render_component(self)
        gc.save(fname, file_format=None)



if __name__ == '__main__':
    from tests.conftest import hist_ds
    from tests.conftest import boxplot_ds
    plot = BoxPlot(boxplot_ds())
    # hd = hist_ds()
    # plot = StackedHistPlot(hd)
    # plot = HistPlot(hist_ds(), 'O3')
    plot.new_window(True)

    ## plot.render_hist(row_id)

    

    ## plot_stacked_hist(res):
    ##     ds = extract_hist(res)
    ##     plot = StackedHistPlot(ds)
    ##     win = PlotWindow(res, plot)
    ##     win.open_plot_window(parent_win)
    ##     return win


    ## plot_hist(res, row_id):
    ##     ds = extract_hist(res)
    ##     plot = HistogramPlot(ds)
    ##     win = PlotWindow(res, plot)
    ##     win.edit_traits(parent=parent_win)
    ##     return win



    ## update_histogram(win, row_id):
    ##     win.plot.render_hist(row_id)


    ## replace_plot(win, plot_id):
    ##     plot = exec(plot_id)
    ##     win.plot = plot


    ## win.replace_plot(plot_creating_func, *args)


    ## def replace_plot(self, pcf):
    ##     self.plot = pcf(self.res, *args)


    ## def create_hist_plot(res):
    ##     ds = extract_hist(res)
    ##     plot = HistPlot(ds)
    ##     return plot
