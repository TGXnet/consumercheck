

# stdlib imports
import sys
import logging

# Enthought imports
from traits.api import HasTraits, Instance, Str, List, DelegatesTo, PrototypedFrom, Property
from traitsui.api import View, Item, ModelView
from enable.api import BaseTool

# Local imports
from nipals import PCA
from dataset import DataSet
from plot_pc_scatter import PCScatterPlot
from plot_ev_line import EVLinePlot
from plot_windows import SinglePlotWindow, LinePlotWindow, MultiPlotWindow



#Double click tool
class DClickTool(BaseTool):
    plot_dict = {}
    #List that holds the function names
    func_list = ['plot_scores','plot_loadings', 'plot_corr_loading', 'plot_expl_var']
    #Triggered on double click
    def normal_left_dclick(self,event):
        self._build_plot_list()
        call_function = getattr(self.ref, self.plot_dict[self.component.title])()
    #Builds a dictionary that holds the function names, based on func_list, with the window title as key
    def _build_plot_list(self):
        for e,i in enumerate(self.component.container.plot_components):
            self.plot_dict[i.title] = self.func_list[e]

class APCAModel(HasTraits):
    """Represent the PCA model of a dataset."""
    name = Str()
    # Shoud be Instance(PrefmapsContainer)
    # but who comes first?
    mother_ref = Instance(HasTraits)
    ds = DataSet()
    # FIXME: To be replaced by groups
    sel_var = List()
    sel_obj = List()

    #checkbox bool for standardized results
    standardize = PrototypedFrom('mother_ref')
    max_n_pc = PrototypedFrom('mother_ref')

    # depends_on
    result = Property()


    def _get_result(self):
#        logging.info("Run pls for: X: {0} ,Y: {1}".format(self.dsX._ds_id, self.dsY._ds_id))
        return PCA(
            self.ds.matrix,
            numPC=self.max_n_pc,
            mode=self.standardize)




class APCAHandler(ModelView):
    plot_uis = List()
    name = DelegatesTo('model')

    def __eq__(self, other):
        return self.name == other

    def __ne__(self, other):
        return self.name != other


    def plot_overview(self):
        """Make PCA overview plot.

        Plot an array of plots where we plot scores, loadings, corr. load and expl. var
        for each of the datasets.
        """
        
        ds_plots = [[self._make_scores_plot(), self._make_loadings_plot()],
                    [self._make_corr_load_plot(), self._make_expl_var_plot()]]
        for plots in ds_plots:
            for plot in plots:
                plot.tools.append(DClickTool(plot,ref = self))
                
        mpw = MultiPlotWindow(title_text=self._wind_title())
        mpw.plots.component_grid = ds_plots
        mpw.plots.shape = (2, 2)
        self._show_plot_window(mpw)

    def plot_scores(self):
        s_plot = self._make_scores_plot()
        spw = SinglePlotWindow(
            plot=s_plot,
            title_text=self._wind_title()
            )
        self._show_plot_window(spw)

    def _make_scores_plot(self):
        res = self.model.result
        pc_tab = res.scores
        labels = self.model.ds.object_names
        plot = PCScatterPlot(pc_tab, labels, title="Scores")
        return plot

    def plot_loadings(self):
        l_plot = self._make_loadings_plot()
        spw = SinglePlotWindow(
            plot=l_plot,
            title_text=self._wind_title()
            )
        self._show_plot_window(spw)

    def _make_loadings_plot(self):
        res = self.model.result
        pc_tab = res.loadings
        labels = self.model.ds.object_names
        plot = PCScatterPlot(pc_tab, labels, title="Loadings")
        return plot

    def plot_corr_loading(self):
        cl_plot = self._make_corr_load_plot()
        spw = SinglePlotWindow(
            plot=cl_plot,
            title_text=self._wind_title()
            )
        self._show_plot_window(spw)

    def _make_corr_load_plot(self):
        res = self.model.result
        pc_tab = res.getCorrLoadings()
        expl_vars = res.explainedVariances
        labels = res.variable_names
        pcl = PCScatterPlot(pc_tab, labels, expl_vars=expl_vars, title="Correlation Loadings")
        pcl.plot_circle(True)
        return pcl

    def plot_expl_var(self):
        ev_plot = self._make_expl_var_plot()
        spw = LinePlotWindow(
            plot=ev_plot,
            title_text=self._wind_title()
            )
        self._show_plot_window(spw)

    def _make_expl_var_plot(self):
        res = self.model.result
        expl_vars = res.explainedVariances
        ev = self._accumulate_expl_var_adapter(expl_vars)
        pl = EVLinePlot(ev, title="Explained Variance")
        return pl


    def _accumulate_expl_var_adapter(self, nipals_ev_dict):
        indexes = nipals_ev_dict.keys()
        indexes.sort()
        values = [0]
        for i in indexes:
            val = nipals_ev_dict[i]
            values.append(values[i-1] + val)
        values.pop(0)
        return np.array(values)


    def _show_plot_window(self, plot_window):
        # FIXME: Setting parent forcing main ui to stay behind plot windows
        if sys.platform == 'linux2':
            self.plot_uis.append( plot_window.edit_traits(kind='live') )
        else:
            self.plot_uis.append(
                plot_window.edit_traits(parent=self.info.ui.control, kind='live')
                )

    def _wind_title(self):
        ds_name = self.model.ds._ds_name
        return "ConsumerCheck PCA - {0}".format(ds_name)
    

a_pca_view = View(
    Item('model.name'),
    Item('model.standardize'),
    Item('model.max_n_pc')
    )
