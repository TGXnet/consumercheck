

# stdlib imports
import sys

# Enthought imports
from traits.api import (HasTraits, Instance, Str, List, Button, DelegatesTo,
                        PrototypedFrom, Property, on_trait_change)
from traitsui.api import View, Group, Item, ModelView
from enable.api import BaseTool
import numpy as np

# Local imports
from nipals import PCA
from dataset import DataSet
from plot_pc_scatter import PCScatterPlot
from plot_ev_line import EVLinePlot
from plot_windows import SinglePlotWindow, LinePlotWindow, MultiPlotWindow
from ds_slicer_view import ds_obj_slicer_view, ds_var_slicer_view


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
    nid = Str()
    # Shoud be Instance(PrefmapsContainer)
    # but who comes first?
    mother_ref = Instance(HasTraits)
    ds = DataSet()
    sub_ds = DataSet()
    # FIXME: To be replaced by groups
    sel_var = List()
    sel_obj = List()

    #checkbox bool for standardized results
    standardize = PrototypedFrom('mother_ref')
    max_n_pc = PrototypedFrom('mother_ref')

    # depends_on
    result = Property()


    def _get_result(self):
        self.sub_ds = self.ds.subset()
        return PCA(
            self.sub_ds.matrix,
            numPC=self.max_n_pc,
            mode=self.standardize)


class APCAHandler(ModelView):
    plot_uis = List()
    name = DelegatesTo('model')
    nid = DelegatesTo('model')

    show_sel_obj = Button('Objects')
    show_sel_var = Button('Variables')

    @on_trait_change('show_sel_obj')
    def _act_show_sel_obj(self, object, name, new):
        object.model.ds.edit_traits(view=ds_obj_slicer_view, kind='livemodal')

    @on_trait_change('show_sel_var')
    def _act_show_sel_var(self, object, name, new):
        object.model.ds.edit_traits(view=ds_var_slicer_view, kind='livemodal')

    def __eq__(self, other):
        return self.nid == other

    def __ne__(self, other):
        return self.nid != other


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
        labels = self.model.sub_ds.object_names
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
        labels = self.model.sub_ds.variable_names
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
        labels = self.model.sub_ds.variable_names
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
        elif sys.platform == 'win32':
            # FIXME: Investigate more here
            self.plot_uis.append(
                # plot_window.edit_traits(parent=self.info.ui.control, kind='nonmodal')
                plot_window.edit_traits(kind='live')
                )
        else:
            raise Exception("Not implemented for this platform: ".format(sys.platform))


    def _wind_title(self):
        ds_name = self.model.ds._ds_name
        return "{0} | PCA - ConsumerCheck".format(ds_name)


a_pca_view = View(
    Group(
        Group(
            Item('model.name'),
            Item('model.standardize'),
            Item('model.max_n_pc'),
            Item('show_sel_obj',
                 show_label=False),
            Item('show_sel_var',
                 show_label=False),
            orientation='vertical',
            ),
        Item('', springy=True),
        orientation='horizontal',
        ),
    )


if __name__ == '__main__':
    # Things to fix for testing
    # mother_ref: standardize, max_n_pc
    from traits.api import Bool, Enum
    from tests.conftest import make_ds_mock
    ds = make_ds_mock()

    class MocMother(HasTraits):
        standardize = Bool(False)
        max_n_pc = Enum(2,3,4,5,6)

    moc_mother = MocMother()
    
    model = APCAModel(
        name='Tore test',
        ds=ds,
        mother_ref=moc_mother)

    controller = APCAHandler(
        model=model)
    controller.configure_traits(view=a_pca_view)
