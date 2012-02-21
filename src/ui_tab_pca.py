"""PCA module for ConsumerCheck application

Adds statistical methods, user inteface and plots for PCA

"""
# stdlib imports
import sys
import logging

# SciPy imports
import numpy as np

# Enthought imports
from traits.api import HasTraits, Instance, Str, List, DelegatesTo, Dict, Any, Enum, Bool, on_trait_change
from traitsui.api import View, Item, UItem, Handler, ModelView, TreeEditor, TreeNode, InstanceEditor, Group
from enable.api import BaseTool

# Local imports
from plot_pc_scatter import PCScatterPlot
from plot_ev_line import EVLinePlot
from plot_windows import SinglePlotWindow, LinePlotWindow, MultiPlotWindow
from nipals import PCA
from dsl_check_list import CheckListController, check_view


class PcaModel(HasTraits):
    """Interface to PCA calculation class

    Might also implement caching of calculated results
    """
    # FIXME: Use Traits notification to update calculated values
    # FIXME: It is worth using a WeakRef trait for the father trait to avoid reference cycles.

    controller = Instance(Handler)

    # Access to datasets and parent window
    main_ui_ptr = Instance(HasTraits)
    dsl = DelegatesTo('main_ui_ptr')

    st_ds = Bool(True)

    max_n_pc = Enum(2,3,4,5,6)

    # Hold calculated pca results
    results = Dict(unicode, Any)

    # To notify dataset selector
    # datasetsAltered = Event

    name = Str( 'Options' )
    list_control = Instance(CheckListController)

    ## @on_trait_change('mother:dsl:[datasets_event,ds_name_event]')
    ## def datasetsChanged(self, obj, name, old, new):
    ##      self.datasetsAltered = True

    def get_res(self, ds_id):
        # FIXME: I hawe to figur out if i should cache
        # the different calculated results, or if it should
        # rerunn the calculation each time. Or if i can find som
        # kind of middle ground
        # Optimize memory usage versus cpu time.

        ## resId = self._makeResId(ds_id, self.max_n_pc)
        ## try:
        ##     return self.results[resId]
        ## except KeyError:
        ##     res = self._run_pca(ds_id)
        ##     self.results[resId] = res
        ##     return res
        return self._run_pca(ds_id)


    def _run_pca(self, ds_id):
        ds = self.dsl.get_by_id(ds_id)
        sds = ds.subset()
        if self.st_ds:
            st_ds = 2
        else:
            st_ds = 0
        return PCA(sds.matrix, numPC=self.max_n_pc, mode=st_ds)

    def _makeResId(self, *inputIds):
        resId = ''
        for iid in inputIds:
            resId += str(iid)
        return resId


class PcaModelViewHandler(ModelView):
    """UI code that will react to UI events for PCA tab"""
    main_ui_ptr = Instance(HasTraits)
    plot_uis = List()

    def init(self, info):
        # info.ui.context: model, handler, object
        # info.ui.control: wx._windows.Frame
        self.model.main_ui_ptr = self.main_ui_ptr
        self.model.list_control = CheckListController( model=self.model.dsl )
        check_view.handler = self.model.list_control

    def closed(self, info, is_ok):
        while self.plot_uis:
            plot_ui = self.plot_uis.pop()
            plot_ui.dispose()

    def _model_changed(self, old, new):
        if old is not None:
            old.controller = None
        if new is not None:
            new.controller = self

    def plot_overview(self):
        """Make PCA overview plot.

        Plot an array of plots where we plot scores, loadings, corr. load and expl. var
        for each of the datasets.
        """
        for ds_id in self.model.list_control.selected:
            ds_plots = [[self._make_scores_plot(ds_id), self._make_loadings_plot(ds_id)],
                        [self._make_corr_load_plot(ds_id), self._make_expl_var_plot(ds_id)]]
            for plots in ds_plots:
                for plot in plots:
                    plot.tools.append(DClickTool(plot,ref = self))
            mpw = MultiPlotWindow(title_text=self._wind_title(ds_id))
            mpw.plots.component_grid = ds_plots
            mpw.plots.shape = (2, 2)
            self._show_plot_window(mpw)

    def plot_scores(self):
        for ds_id in self.model.list_control.selected:
            s_plot = self._make_scores_plot(ds_id)
            spw = SinglePlotWindow(
                plot=s_plot,
                title_text=self._wind_title(ds_id)
                )
            self._show_plot_window(spw)

    def _make_scores_plot(self, ds_id):
        res = self.model.get_res(ds_id)
        pc_tab = res.getScores()
        ds = self.model.dsl.get_by_id(ds_id)
        sds = ds.subset()
        labels = sds.object_names
        plot = self._make_plot(pc_tab, ds_id, "Scores", labels)
        return plot

    def plot_loadings(self):
        for ds_id in self.model.list_control.selected:
            l_plot = self._make_loadings_plot(ds_id)
            spw = SinglePlotWindow(
                plot=l_plot,
                title_text=self._wind_title(ds_id)
                )
            self._show_plot_window(spw)

    def _make_loadings_plot(self, ds_id):
        res = self.model.get_res(ds_id)
        pc_tab = res.getLoadings()
        ds = self.model.dsl.get_by_id(ds_id)
        sds = ds.subset()
        labels = sds.variable_names
        plot = self._make_plot(pc_tab, ds_id, "Loadings", labels)
        return plot

    def _make_plot(self, pc_tab, ds_id, plot_title, labels=None):
        expl_vars = self.model.get_res(ds_id).getCalExplVar()
        ps = PCScatterPlot(pc_tab, labels, expl_vars=expl_vars, title=plot_title)
        return ps

    def plot_corr_loading(self):
        for ds_id in self.model.list_control.selected:
            cl_plot = self._make_corr_load_plot(ds_id)
            spw = SinglePlotWindow(
                plot=cl_plot,
                title_text=self._wind_title(ds_id)
                )
            self._show_plot_window(spw)

    def _make_corr_load_plot(self, ds_id):
        res = self.model.get_res(ds_id)
        pc_tab = res.getCorrLoadings()
        expl_vars = res.getCalExplVar()
        ds = self.model.dsl.get_by_id(ds_id)
        sds = ds.subset()
        labels = sds.variable_names
        pcl = PCScatterPlot(pc_tab, labels, expl_vars=expl_vars, title="Correlation Loadings")
        pcl.plot_circle(True)
        return pcl

    def plot_expl_var(self):
        for ds_id in self.model.list_control.selected:
            ev_plot = self._make_expl_var_plot(ds_id)
            spw = LinePlotWindow(
                plot=ev_plot,
                title_text=self._wind_title(ds_id)
                )
            self._show_plot_window(spw)

    def _make_expl_var_plot(self, ds_id):
        res = self.model.get_res(ds_id)
        expl_vars = res.getCalExplVar()
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

    def _wind_title(self, ds_id):
        ds_name = self.model.dsl.get_by_id(ds_id)._ds_name
        return "ConsumerCheck PCA - {0}".format(ds_name)
    

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

# Double click handlers
def clkOverview(obj):
    logging.info("Overview plot activated")
    obj.controller.plot_overview()

def clkScores(obj):
    logging.info("Scoreplot activated")
    obj.controller.plot_scores()

def clkLoadings(obj):
    logging.info("Loadingplot activated")
    obj.controller.plot_loadings()

def clkCorrLoad(obj):
    logging.info("Loadingplot activated")
    obj.controller.plot_corr_loading()

def clkExplResVar(obj):
    logging.info("Explained variance plot activated")
    obj.controller.plot_expl_var()


# Views
no_view = View()

pca_view = View(
    Group(
        Group(
            Item('max_n_pc', show_label=False),
            show_border=True,
            label='Max PC to calculate',
            ),
        Group(
            Item('dsl', editor=InstanceEditor(view=check_view),
                 style='custom', show_label=False),
            show_border=True,
            label='Select dataset(s) to analyze',
            ),
        Group(
            Item('st_ds', show_label=False),
            show_border=True,
            label='Standarized',
            ),
        )
    )

options_tree = TreeEditor(
    nodes = [
        TreeNode( node_for = [ PcaModel ],
                  children = '',
                  label = 'name',
                  tooltip = 'Oversikt',
                  view = no_view,
                  rename = False,
                  rename_me = False,
                  copy = False,
                  delete = False,
                  delete_me = False,
                  insert = False,
                  ),
        TreeNode( node_for = [ PcaModel ],
                  label = '=Overview',
                  on_dclick = clkOverview,
                  view = pca_view,
                  ),
        TreeNode( node_for = [ PcaModel ],
                  label = '=Scores',
                  on_dclick = clkScores,
                  view = pca_view,
                  ),
        TreeNode( node_for = [ PcaModel ],
                  label = '=Loadings',
                  on_dclick = clkLoadings,
                  view = pca_view,
                  ),
        TreeNode( node_for = [ PcaModel ],
                  label = '=Correlation loadings',
                  on_dclick = clkCorrLoad,
                  view = pca_view,
                  ),
        TreeNode( node_for = [ PcaModel ],
                  label = '=Explained variance',
                  on_dclick = clkExplResVar,
                  view = pca_view,
                  ),
        ],
    hide_root = False,
    editable = True
    )


pca_tree_view = View(
    UItem('model',
         editor=options_tree,
         resizable=True,
         ),
    title='Options tree',
    resizable=True,
    width=.4,
    height=.3,
    )


if __name__ == '__main__':
    print("Interactive start")

    from dataset_collection import DatasetCollection
    from importer_main import ImporterMain

    class FakeMain(HasTraits):
        dsl = DatasetCollection()
        pca = Instance(PcaModelViewHandler)

        def _pca_changed(self, old, new):
            logging.info("Setting pca mother")
            if old is not None:
                old.main_ui_ptr = None
            if new is not None:
                new.main_ui_ptr = self

    main = FakeMain(pca = PcaModelViewHandler(PcaModel()))
    fi = ImporterMain()
    main.dsl.add_dataset(fi.import_data('datasets/Cheese/ConsumerLiking.txt'))
    main.dsl.add_dataset(fi.import_data('datasets/test.txt', False, False))
    with np.errstate(invalid='ignore'):
        main.pca.configure_traits(view=pca_tree_view)
