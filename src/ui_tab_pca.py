"""PCA module for ConsumerCheck application

Adds statistical methods, user inteface and plots for PCA

"""
# stdlib imports
import sys
import logging

# Enthought imports
from traits.api import HasTraits, Instance, Str, List, DelegatesTo, Dict, Any, Enum
from traitsui.api import View, Item, UItem, Handler, ModelView, TreeEditor, TreeNode, InstanceEditor, Group
from chaco.api import ArrayPlotData

# Local imports
from plots import CCPlotScatter, CCPlotLine, CCPlotCorrLoad
from new_plots import CCScatterPCPlot
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
        return PCA(sds.matrix, numPC=self.max_n_pc)

    def _makeResId(self, *inputIds):
        resId = ''
        for iid in inputIds:
            resId += str(iid)
        return resId


class PcaModelViewHandler(ModelView):
    """UI code that vil react to UI events for PCA tab"""
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
            ds_plots = [[self._make_scores_plot(ds_id, True), self._make_loadings_plot(ds_id, True)],
                        [self._make_corr_load_plot(ds_id, True), self._make_expl_var_plot(ds_id)]]
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

    def _make_scores_plot(self, ds_id, add_labels = True):
        res = self.model.get_res(ds_id)
        pc_tab = res.getScores()
        if add_labels:
            ds = self.model.dsl.get_by_id(ds_id)
            sds = ds.subset()
            labels = sds.object_names
            plot = self._make_plot(pc_tab, ds_id, "Scores", labels)
        else:
            plot = self._make_plot(pc_tab, ds_id, "Scores")
        return plot

    def plot_loadings(self):
        for ds_id in self.model.list_control.selected:
            l_plot = self._make_loadings_plot(ds_id)
            spw = SinglePlotWindow(
                plot=l_plot,
                title_text=self._wind_title(ds_id)
                )
            self._show_plot_window(spw)

    def _make_loadings_plot(self, ds_id, add_labels=True):
        res = self.model.get_res(ds_id)
        pc_tab = res.getLoadings()
        if add_labels:
            ds = self.model.dsl.get_by_id(ds_id)
            sds = ds.subset()
            labels = sds.variable_names
            plot = self._make_plot(pc_tab, ds_id, "Loadings", labels)
        else:
            plot = self._make_plot(pc_tab, ds_id, "Loadings")
        return plot

    def _make_plot(self, pc_tab, ds_id, plot_title, labels=None):
        expl_vars = self.model.get_res(ds_id).getCalExplVar()

        ps = CCScatterPCPlot()
        ps.title = plot_title
        ps.add_PC_set(pc_tab, labels=labels)
        ps.x_axis.title = "PC1 ({0:.0f}%)".format(expl_vars[1])
        ps.y_axis.title = "PC2 ({0:.0f}%)".format(expl_vars[2])
        return ps

    def plot_corr_loading(self):
        for ds_id in self.model.list_control.selected:
            cl_plot = self._make_corr_load_plot(ds_id)
            spw = SinglePlotWindow(
                plot=cl_plot,
                title_text=self._wind_title(ds_id)
                )
            self._show_plot_window(spw)

    def _make_corr_load_plot(self, ds_id, add_labels=True):
        res = self.model.get_res(ds_id)
        pc_tab = res.getCorrLoadings()
        expl_vars = res.getCalExplVar()
        pd = ArrayPlotData()
        pd.set_data('pc1', pc_tab[:,0])
        pd.set_data('pc2', pc_tab[:,1])
        pcl = CCPlotCorrLoad(pd)
        pcl.title = "Correlation Loadings"
        pcl.x_axis.title = "PC1 ({0:.0f}%)".format(expl_vars[1])
        pcl.y_axis.title = "PC2 ({0:.0f}%)".format(expl_vars[2])
        if add_labels:
            ds = self.model.dsl.get_by_id(ds_id)
            sds = ds.subset()
            labels = sds.variable_names
            pcl.add_data_labels(labels)
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
        expl_index = [0]
        expl_val = [0]
        for index, value in expl_vars.iteritems():
            expl_index.append(index)
            expl_val.append(expl_val[index-1] + value)
        pd = ArrayPlotData(index=expl_index, pc_sigma=expl_val)
        pl = CCPlotLine(pd)
        pl.title = "Explained variance"
        pl.x_axis.title = "# f principal components"
        pl.y_axis.title = "Explained variance [%]"
        pl.y_mapper.range.set_bounds(0, 100)
        return pl

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
    main.dsl.add_dataset(fi.import_data('datasets/Cheese/SensoryData.txt'))
    main.pca.configure_traits(view=pca_tree_view)
