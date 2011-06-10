"""Prefmap module for ConsumerCheck application

Adds statistical methods, user inteface and plots for Prefmap

"""
# stdlib imports
import logging

# Enthought imports
from enthought.traits.api import HasTraits, Instance, Event, Str, List, on_trait_change, DelegatesTo, Dict, Any
from enthought.traits.ui.api import View, Item, UItem, Group, Handler, ModelView, CheckListEditor, TreeEditor, TreeNode
from enthought.chaco.api import ArrayPlotData

# Local imports
from plots import CCPlotScatter, CCPlotLine, CCPlotCorrLoad
from plot_windows import SinglePlotWindow, MultiPlotWindow
from mvr import plsr
from prefmap_selector import PrefmapSelectorController, prefmap_selector_view


class PrefmapModel(HasTraits):
    """Interface to Prefmap calculation class

    Might also implement caching of calculated results
    """
    # FIXME: Use Traits notification to update calculated values
    # FIXME: It is worth using a WeakRef trait for the father trait to avoid reference cycles.

    controller = Instance(Handler)

    # Access to datasets and parent window
    main_ui_ptr = Instance(HasTraits)
    dsl = DelegatesTo('main_ui_ptr')

    # Hold calculated prefmap results
    results = Dict(unicode, Any)

    # To notify dataset selector
    # datasetsAltered = Event

    name = Str( 'Options' )
    selector = Instance(PrefmapSelectorController)

    # List of selected (X, Y) tuples
    selectedXYlist = List([
        ('ost_forbruker', 'ost_sensorikk'),
        ('ost_sensorikk', 'ost_forbruker'),
        ('a_labels', 'a_labels'),
        ])

    ## @on_trait_change('mother:dsl:[dataDictContentChanged,datasetNameChanged]')
    ## def datasetsChanged(self, object, name, old, new):
    ##      self.datasetsAltered = True

    def get_res(self, xId, yId):
        resId = self._makeResId(xId, yId)
        try:
            return self.results[resId]
        except KeyError:
            res = self._run_prefmap(xId, yId)
            self.results[resId] = res
            return res

    def _run_prefmap(self, xId, yId):
        logging.info("Run plsr for: X: {0} ,Y: {1}".format(xId, yId))
        return plsr(
            self.dsl.retriveDatasetByName(xId).matrix,
            self.dsl.retriveDatasetByName(yId).matrix,
            centre="yes",
            fncomp=5,
            fmethod="oscorespls",
            fvalidation="LOO")

    def _makeResId(self, *inputIds):
        resId = ''
        for iid in inputIds:
            resId += iid
        return resId


class PrefmapModelViewHandler(ModelView):
    """UI code that vil react to UI events for Prefmap tab"""
    # Disable UI when unittesting
    show = True
    main_ui_ptr = Instance(HasTraits)
    plot_uis = List()

    def init(self, info):
        # info.ui.context: model, handler, object
        # info.ui.control: wx._windows.Frame
        self.model.main_ui_ptr = self.main_ui_ptr
        # FIXME: Replace with Prefmap controller
        self.model.selector = PrefmapSelectorController( model=self.model.dsl )
        prefmap_selector_view.handler = self.model.selector

    def closed(self, info, is_ok):
        while self.plot_uis:
            plot_ui = self.plot_uis.pop()
            plot_ui.dispose()

    def _model_changed(self, old, new):
        if old is not None:
            old.controller = None
        if new is not None:
            new.controller = self

    def plot_overview(self, show = True):
        """Make Prefmap overview plot.

        Plot an array of plots where we plot scores, loadings, corr. load and expl. var
        for each of the datasets.
        """
        # self.show = show
        for xId, yId in self.model.selector.xyMappings:
            ds_plots = [[self._make_scores_plot(xId, yId), self._make_corr_load_plot(xId, yId)],
                        [self._make_expl_var_plot_x(xId, yId), self._make_expl_var_plot_y(xId, yId)]]
            mpw = MultiPlotWindow()
            mpw.plots.component_grid = ds_plots
            mpw.plots.shape = (2, 2)
            self._show_plot_window(mpw)

    def plot_scores(self, show = True):
        # self.show = show
        for xId, yId in self.model.selector.xyMappings:
            s_plot = self._make_scores_plot(xId, yId)
            spw = SinglePlotWindow( plot=s_plot )
            self._show_plot_window(spw)

    def _make_scores_plot(self, xId, yId):
        res = self.model.get_res(xId, yId)
        pc_tab = res['Scores T']
        labels = self.model.dsl.retriveDatasetByName(xId).objectNames
        plot = self._make_plot(pc_tab, xId, yId, labels, "Prefmap Scores plot\n{0}".format(xId))
        return plot

    def plot_loadings_x(self, show = True):
        # self.show = show
        for xId, yId in self.model.selector.xyMappings:
            l_plot = self._make_loadings_plot_x(xId, yId)
            spw = SinglePlotWindow( plot=l_plot )
            self._show_plot_window(spw)

    def _make_loadings_plot_x(self, xId, yId):
        res = self.model.get_res(xId, yId)
        xLP = res['Xloadings P']
        labels = self.model.dsl.retriveDatasetByName(xId).variableNames
        plot = self._make_plot(xLP, xId, yId, labels, "Prefmap Loadings plot X")
        return plot

    def plot_loadings_y(self, show = True):
        # self.show = show
        for xId, yId in self.model.selector.xyMappings:
            l_plot = self._make_loadings_plot_y(xId, yId)
            spw = SinglePlotWindow( plot=l_plot )
            self._show_plot_window(spw)

    def _make_loadings_plot_y(self, xId, yId):
        res = self.model.get_res(xId, yId)
        yLP = res['Yloadings Q']
        labels = self.model.dsl.retriveDatasetByName(yId).variableNames
        plot = self._make_plot(yLP, xId, yId, labels, "Prefmap Loadings plot Y")
        return plot

    def _make_plot(self, pc_tab, xId, yId, labels, plot_title):
        expl_vars = self.model.get_res(xId, yId)['calExplVarX']
        pd = ArrayPlotData()
        pd.set_data('pc1', pc_tab[:,0])
        pd.set_data('pc2', pc_tab[:,1])
        ps = CCPlotScatter(pd)
        ps.title = plot_title
        ps.x_axis.title = "PC1 ({0:.0f}%)".format(expl_vars[1])
        ps.y_axis.title = "PC2 ({0:.0f}%)".format(expl_vars[2])
        ps.addDataLabels(labels)
        return ps

    def plot_corr_loading(self, show = True):
        # self.show = show
        for xId, yId in self.model.selector.xyMappings:
            cl_plot = self._make_corr_load_plot(xId, yId)
            spw = SinglePlotWindow( plot=cl_plot )
            self._show_plot_window(spw)

    def _make_corr_load_plot(self, xId, yId):
        # VarNameX, CorrLoadX
        # labels
        vnx = self.model.dsl.retriveDatasetByName(xId).variableNames
        vny = self.model.dsl.retriveDatasetByName(yId).variableNames
        res = self.model.get_res(xId, yId)
        # pc_tab = res.getCorrLoadings()
        clx = res['corrLoadX']
        cly = res['corrLoadY']
        # calExplVarX
        cevx = res['calExplVarX']
        cevy = res['calExplVarY']
        pd = ArrayPlotData()
        pd.set_data('pc1', clx[:,0])
        pd.set_data('pc2', clx[:,1])
        pcl = CCPlotCorrLoad(pd)
        pcl.title = "Prefmap Correlation Loadings plot"
        pcl.x_axis.title = "PC1 ({0:.0f}%, {1:.0f}%)".format(cevx[0], cevy[0])
        pcl.y_axis.title = "PC2 ({0:.0f}%, {1:.0f}%)".format(cevx[1], cevy[1])
#        pcl.addDataLabels(labels)
        return pcl

    def plot_expl_var_x(self, show = True):
        # self.show = show
        for xId, yId in self.model.selector.xyMappings:
            ev_plot = self._make_expl_var_plot_x(xId, yId)
            spw = SinglePlotWindow( plot=ev_plot )
            self._show_plot_window(spw)

    def _make_expl_var_plot_x(self, xId, yId):
        res = self.model.get_res(xId, yId)
        sumCalX = res['cumCalExplVarX']
        expl_index = range(len(sumCalX))
        pd = ArrayPlotData(index=expl_index, pc_sigma=sumCalX)
        pl = CCPlotLine(pd)
        pl.title = "Prefmap explained variance plot"
        pl.x_axis.title = "# f principal components"
        pl.y_axis.title = "Explained variance [%]"
        pl.y_mapper.range.set_bounds(0, 100)
        return pl

    def plot_expl_var_y(self, show = True):
        # self.show = show
        for xId, yId in self.model.selector.xyMappings:
            ev_plot = self._make_expl_var_plot_y(xId, yId)
            spw = SinglePlotWindow( plot=ev_plot )
            self._show_plot_window(spw)

    def _make_expl_var_plot_y(self, xId, yId):
        res = self.model.get_res(xId, yId)
        sumCalY = res['cumCalExplVarY']
        sumValY = res['cumValExplVarY']
        expl_index = range(len(sumCalY))
        pd = ArrayPlotData(index=expl_index, pc_sigma=sumCalY)
        pl = CCPlotLine(pd)
        pl.title = "Prefmap explained variance plot"
        pl.x_axis.title = "# f principal components"
        pl.y_axis.title = "Explained variance [%]"
        pl.y_mapper.range.set_bounds(0, 100)
        return pl

    def _show_plot_window(self, plot_window):
        if self.show:
            # FIXME: Setting parent forcing main ui to stay behind plot windows
            # self.plot_uis.append( plot_window.edit_traits(parent=self.info.ui.control, kind='live') )
            self.plot_uis.append( plot_window.edit_traits(kind='live') )


# Double click handlers
def clkOverview(obj):
    logging.info("Overview plot activated")
    obj.controller.plot_overview()

def clkScores(obj):
    logging.info("Scores plot activated")
    obj.controller.plot_scores()

def clkCorrLoad(obj):
    logging.info("X & Y correlation loadings plot activated")
    obj.controller.plot_corr_loading()

def clkExplResVarX(obj):
    logging.info("Explained variance X plot activated")
    obj.controller.plot_expl_var_x()

def clkExplResVarY(obj):
    logging.info("Explained variance Y plot activated")
    obj.controller.plot_expl_var_y()

def clkLoadingsX(obj):
    logging.info("X loadings plot activated")
    obj.controller.plot_loadings_x()

def clkLoadingsY(obj):
    logging.info("Y loadings plot activated")
    obj.controller.plot_loadings_y()


# Views
no_view = View()

options_tree = TreeEditor(
    nodes = [
        TreeNode( node_for = [ PrefmapModel ],
                  children = '',
                  label = 'name',
                  tooltip = 'Overview',
                  view = prefmap_selector_view,
                  rename = False,
                  rename_me = False,
                  copy = False,
                  delete = False,
                  delete_me = False,
                  insert = False,
                  ),
        TreeNode( node_for = [ PrefmapModel ],
                  label = '=Overview plot',
                  on_dclick = clkOverview,
                  view = prefmap_selector_view,
                  ),
        TreeNode( node_for = [ PrefmapModel ],
                  label = '=Scores',
                  on_dclick = clkScores,
                  view = prefmap_selector_view,
                  ),
        TreeNode( node_for = [ PrefmapModel ],
                  label = '=X & Y correlation loadings',
                  on_dclick = clkCorrLoad,
                  view = prefmap_selector_view,
                  ),
        TreeNode( node_for = [ PrefmapModel ],
                  label = '=Explained variance X',
                  on_dclick = clkExplResVarX,
                  view = prefmap_selector_view,
                  ),
        TreeNode( node_for = [ PrefmapModel ],
                  label = '=Explained variance Y',
                  on_dclick = clkExplResVarY,
                  view = prefmap_selector_view,
                  ),
        TreeNode( node_for = [ PrefmapModel ],
                  label = '=X loadings',
                  on_dclick = clkLoadingsX,
                  view = prefmap_selector_view,
                  ),
        TreeNode( node_for = [ PrefmapModel ],
                  label = '=Y loadings',
                  on_dclick = clkLoadingsY,
                  view = prefmap_selector_view,
                  ),
        ],
    hide_root = False,
    editable = True
    )


prefmap_tree_view = View(
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
    """Test run the View"""
    print("Interactive start")
    from dataset_collection import DatasetCollection
    from file_importer import FileImporter
    
    class FakeMain(HasTraits):
        dsl = DatasetCollection()
        prefmap = Instance(PrefmapModelViewHandler)

        def _prefmap_changed(self, old, new):
            logging.info("Setting prefmap mother")
            if old is not None:
                old.main_ui_ptr = None
            if new is not None:
                new.main_ui_ptr = self

    main = FakeMain(prefmap = PrefmapModelViewHandler(PrefmapModel()))
    fi = FileImporter()
    main.dsl.addDataset(fi.noninteractiveImport('datasets/A_labels.txt'))
    main.dsl.addDataset(fi.noninteractiveImport('datasets/C_labels.txt'))
    main.dsl.addDataset(fi.noninteractiveImport('datasets/Ost_forbruker.txt'))
    main.dsl.addDataset(fi.noninteractiveImport('datasets/Ost_sensorikk.txt'))
    main.prefmap.configure_traits(view=prefmap_tree_view)
