
# Scipy imports
import numpy as _np

# ETS imports
import traits.api as _traits
import chaco.api as _chaco
from enable.colors import color_table

# Local imports
from dataset import DataSet



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
        index_range = _chaco.DataRange1D(idx)
        index_mapper = _chaco.LinearMapper(range=index_range)

        # Create the value range
        value_range = _chaco.DataRange1D(vals, high=self.ceiling)
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
        left_axis = _chaco.PlotAxis(renderer, orientation='left')
        bottom_axis = _chaco.LabelAxis(renderer, orientation='bottom',
                                       title='Categories',
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
        return self.ds



class StackedHistPlot(_chaco.DataView):
    '''Plot histogram values for each row stacked on to of each other'''

    ds = _traits.Instance(DataSet)
    stair_ds = _traits.Instance(_chaco.MultiArrayDataSource)
    plot_data = _traits.Property()



    def __init__(self, ds):
        super(StackedHistPlot, self).__init__(ds=ds)
        last_renderer = self._render_data()
        self._add_axis(last_renderer)


    def _stair_ds_default(self):
        nums = self.ds.values
        stair = _np.cumsum(nums, axis=1)
        return _chaco.MultiArrayDataSource(stair)


    def _render_data(self):
        idx = _chaco.ArrayDataSource(_np.arange(self.ds.n_objs))
        mvals = self.stair_ds

        # Create the index range
        index_range = _chaco.DataRange1D(idx, tight_bounds=True)
        index_mapper = _chaco.LinearMapper(range=index_range)

        # Create the value range
        value_range = _chaco.DataRange1D(mvals, tight_bounds=True)
        value_mapper = _chaco.LinearMapper(range=value_range)

        colors = color_table.keys()

        for i in range(mvals.get_value_size()-1, 0, -1):
            vals = _chaco.ArrayDataSource(mvals.get_data(axes=i))
            bars = _chaco.BarPlot(index=idx, value=vals,
                                  value_mapper=value_mapper,
                                  index_mapper=index_mapper,
                                  line_color='black',
                                  fill_color=colors[i%len(colors)],
                                  bar_width=0.8, antialias=False)
            self.add(bars)
        return bars



    def _add_axis(self, renderer):
        left_axis = _chaco.PlotAxis(renderer, orientation='left')
        bottom_axis = _chaco.LabelAxis(renderer, orientation='bottom',
                                       title='Categories',
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
        return self.ds



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
        left_axis = _chaco.PlotAxis(renderer, orientation='left')
        bottom_axis = _chaco.LabelAxis(renderer, orientation='bottom',
                                       title='Categories',
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
        return self.ds



if __name__ == '__main__':
    from tests.conftest import hist_ds, boxplot_ds
    # plot = BoxPlot(boxplot_ds())
    # plot = StackedHistPlot(hist_ds())
    plot = HistPlot(hist_ds(), 'O3')
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
