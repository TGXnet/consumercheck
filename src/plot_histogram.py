
# Scipy imports
import numpy as _np

# ETS imports
import traits.api as _traits
import chaco.api as _chaco
# from chaco.api import ArrayDataSource, DataRange1D, DataView, LinearMapper, BarPlot
from chaco.example_support import COLOR_PALETTE

# Local imports
from dataset_ng import DataSet



class HistPlot(_chaco.DataView):

    ds = _traits.Instance(DataSet)
    row_id = _traits.Str()
    ceiling = _traits.Int()
    head_space = _traits.Float(1.1)
    bars_renderer = _traits.Instance(_chaco.BarPlot)


    def __init__(self, ds, row_id):
        super(HistPlot, self).__init__(ds=ds, row_id=row_id)
        self.bars_renderer = self._create_render()
        self.add(self.bars_renderer)
        self._add_axis(self.bars_renderer)


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
                              fill_color=tuple(COLOR_PALETTE[6]),
                              bar_width=0.8, antialias=False)

        return bars


    def _add_axis(self, renderer):
        left_axis = _chaco.PlotAxis(renderer, orientation='left')
        bottom_axis = _chaco.LabelAxis(renderer, orientation='bottom',
                                       title='Categories',
                                       positions = range(self.ds.n_vars),
                                       labels = [str(vn) for vn in self.ds.var_n],
                                       small_haxis_style=True)
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





if __name__ == '__main__':
    from tests.conftest import hist_ds
    ds = hist_ds()
    print(ds.mat)
    plot = HistPlot(ds, 'O6')
    plot.new_window(True)

    ## plot.render_hist(row_id)

    ## plot = StackedHistPlot(ds)

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
