"""Prefmap module for ConsumerCheck application

Adds statistical methods, user inteface and plots for Prefmap

FIXME: Idea: Make this control the creation of prefmap plot_config
model object's that specify the plot setings for each prefmap plotting.
Separate out the plot generation function for each of the plot models.
One model will typicaly hold the result or a result property of prefma and setting
for internal or external ploting and other plot settings.
"""
# stdlib imports
import sys
import logging

# Enthought imports
from traits.api import HasTraits, Instance, Str, List, DelegatesTo, Dict, Any, Bool, Property
from traitsui.api import View, UItem, Handler, ModelView, TreeEditor, TreeNode
# from chaco.api import ArrayPlotData

# Local imports
from dataset import DataSet
from plot_pc_scatter import PCScatterPlot
from plot_ev_line import EVLinePlot
from plot_windows import SinglePlotWindow, LinePlotWindow, MultiPlotWindow
# from mvr import plsr
from plsr import nipalsPLS2 as pls
from prefmap_ui import PrefmapUIController, prefmap_ui_controller, prefmap_ui_view






class APrefmapModel(HasTraits):
    """Represent the Prefmap model between one X and Y dataset."""
    name = Str()
    # Shoud be Instance(PrefmapsContainer)
    # but who comes first?
    mother_ref = Instance(HasTraits)
    dsX = DataSet()
    dsY = DataSet()
    # FIXME: To be replaced by groups
    sel_var_X = List()
    sel_var_Y = List()
    sel_obj = List()
    # depends_on
    result = Property()



class PrefmapsContainer(HasTraits):
    """Prefmap plugin container."""
    name = Str()
    # Instance(MainUi)?
    # WeakRef?
    mother_ref = Instance(HasTraits)
    dsl = DelegatesTo('mother_ref')
    mappings = List(APrefmapModel)



    def add_mapping(self, id_x, id_y):
        set_x = self.dsl.get_by_id(id_x)
        set_y = self.dsl.get_by_id(id_y)
        the_mapping = APrefmapModel(mother_ref=self, dsX=set_x, dsY=set_y)
        self.mappings.append(the_mapping)





class PrefmapModel(HasTraits):
    """Interface to Prefmap calculation class

    Might also implement caching of calculated results
    """
    # FIXME: Use Traits notification to update calculated values
    # FIXME: It is worth using a WeakRef trait for the father trait to avoid reference cycles.

    controller = Instance(Handler)

    # Access to datasets and parent window
    mother_ref = Instance(HasTraits)
    dsl = DelegatesTo('mother_ref')
    
    #checkbox bool for standarized results
    st_ds = Bool(False)
       
    
    # Hold calculated prefmap results
    results = Dict(unicode, Any)

    name = Str( 'Options' )
    selector = Instance(PrefmapUIController)

    def get_res(self, xId, yId):
        # FIXME: Disabled caching
        ## resId = self._makeResId(xId, yId)
        ## try:
        ##     return self.results[resId]
        ## except KeyError:
        ##     res = self._run_prefmap(xId, yId)
        ##     self.results[resId] = res
        ##     return res
        return self._run_prefmap(xId, yId)

    def _run_prefmap(self, xId, yId):
        logging.info("Run pls for: X: {0} ,Y: {1}".format(xId, yId))
        return pls(
            self.dsl.get_by_id(xId).matrix,
            self.dsl.get_by_id(yId).matrix,
            numPC=8,
            cvType=["loo"],
            Xstand=self.st_ds,
            Ystand=self.st_ds)

    def _makeResId(self, *inputIds):
        resId = ''
        for iid in inputIds:
            resId += iid
        return resId


class PrefmapModelViewHandler(ModelView):
    """UI code that vil react to UI events for Prefmap tab"""
    # Disable UI when unittesting
    mother_ref = Instance(HasTraits)
    plot_uis = List()

    def init(self, info):
        # info.ui.context: model, handler, object
        # info.ui.control: wx._windows.Frame
        self.model.mother_ref = self.mother_ref
        prefmap_ui_controller.model = self.model.dsl
        self.model.selector = prefmap_ui_controller

    def closed(self, info, is_ok):
        while self.plot_uis:
            plot_ui = self.plot_uis.pop()
            plot_ui.dispose()

    def _model_changed(self, old, new):
        if old is not None:
            old.controller = None
            ## new.mother_ref = None
        if new is not None:
            new.controller = self
            ## new.mother_ref = self.mother_ref

    def get_mappings(self):
        return self.model.selector.get_cross_mappings()


    def plot_overview(self):
        """Make Prefmap overview plot.

        Plot an array of plots where we plot scores, loadings, corr. load and expl. var
        for each of the datasets.
        """
        for xId, yId in self.get_mappings():
            ds_plots = [[self._make_scores_plot(xId, yId), self._make_corr_load_plot(xId, yId)],
                        [self._make_expl_var_plot_x(xId, yId), self._make_expl_var_plot_y(xId, yId)]]
            mpw = MultiPlotWindow(title_text=self._wind_title(xId, yId))
            mpw.plots.component_grid = ds_plots
            mpw.plots.shape = (2, 2)
            self._show_plot_window(mpw)

    def plot_scores(self):
        for xId, yId in self.get_mappings():
            s_plot = self._make_scores_plot(xId, yId)
            spw = SinglePlotWindow(
                plot=s_plot,
                title_text=self._wind_title(xId, yId)
                )
            self._show_plot_window(spw)


    def _make_scores_plot(self, xId, yId):
        res = self.model.get_res(xId, yId)
        pc_tab = res.Xscores()
        labels = self.model.dsl.get_by_id(xId).object_names
        expl_vars_x = self._ev_list_dict_adapter(res.XcalExplVar_tot_list())
        # expl_vars_y = self._ev_list_dict_adapter(res.YcalExplVar_tot_list())
        plot = PCScatterPlot(pc_tab, labels, expl_vars=expl_vars_x, title="Scores")
        ## pd = ArrayPlotData()
        ## pd.set_data('pc1', pc_tab[:,0])
        ## pd.set_data('pc2', pc_tab[:,1])
        ## plot = CCPlotScatter(pd)
        ## plot.title = "Scores"
        ## plot.x_axis.title = "PC1 ({0:.0f}%, {1:.0f}%)".format(expl_vars_x[0], expl_vars_y[0])
        ## plot.y_axis.title = "PC2 ({0:.0f}%, {1:.0f}%)".format(expl_vars_x[1], expl_vars_y[1])
        ## labels = self.model.dsl.get_by_id(xId).object_names
        ## plot.add_data_labels(labels)
        return plot


    def _ev_list_dict_adapter(self, ev_list):
        return dict([kv for kv in enumerate(ev_list, 1)])


    def plot_loadings_x(self):
        for xId, yId in self.get_mappings():
            l_plot = self._make_loadings_plot_x(xId, yId)
            spw = SinglePlotWindow(
                plot=l_plot,
                title_text=self._wind_title(xId, yId)
                )
            self._show_plot_window(spw)

    def _make_loadings_plot_x(self, xId, yId):
        res = self.model.get_res(xId, yId)
        xLP = res.Xloadings()
        expl_vars = self._ev_list_dict_adapter(res.XcalExplVar_tot_list())
        labels = self.model.dsl.get_by_id(xId).variable_names
        plot = PCScatterPlot(xLP, labels, expl_vars=expl_vars, title="X Loadings")
        ## pd = ArrayPlotData()
        ## pd.set_data('pc1', xLP[:,0])
        ## pd.set_data('pc2', xLP[:,1])
        ## plot = CCPlotScatter(pd)
        ## plot.title = "X Loadings"
        ## plot.x_axis.title = "PC1 ({0:.0f}%)".format(expl_vars[0])
        ## plot.y_axis.title = "PC2 ({0:.0f}%)".format(expl_vars[1])
        ## plot.add_data_labels(labels)
        return plot

    def plot_loadings_y(self):
        for xId, yId in self.get_mappings():
            l_plot = self._make_loadings_plot_y(xId, yId)
            spw = SinglePlotWindow(
                plot=l_plot,
                title_text=self._wind_title(xId, yId)
                )
            self._show_plot_window(spw)

    def _make_loadings_plot_y(self, xId, yId):
        res = self.model.get_res(xId, yId)
        yLP = res.Yloadings()
        expl_vars = self._ev_list_dict_adapter(res.YcalExplVar_tot_list())
        labels = self.model.dsl.get_by_id(yId).variable_names
        plot = PCScatterPlot(yLP, labels, expl_vars=expl_vars, title="Y Loadings")
        ## pd = ArrayPlotData()
        ## pd.set_data('pc1', yLP[:,0])
        ## pd.set_data('pc2', yLP[:,1])
        ## plot = CCPlotScatter(pd)
        ## plot.title = "Y Loadings"
        ## plot.x_axis.title = "PC1 ({0:.0f}%)".format(expl_vars[0])
        ## plot.y_axis.title = "PC2 ({0:.0f}%)".format(expl_vars[1])
        ## plot.add_data_labels(labels)
        return plot

    def plot_corr_loading(self):
        for xId, yId in self.get_mappings():
            cl_plot = self._make_corr_load_plot(xId, yId)
            spw = SinglePlotWindow(
                plot=cl_plot,
                title_text=self._wind_title(xId, yId)
                )
            self._show_plot_window(spw)

    def _make_corr_load_plot(self, xId, yId):
        # VarNameX, CorrLoadX
        # labels
        res = self.model.get_res(xId, yId)
        # pc_tab = res.getCorrLoadings()
        clx = res.XcorrLoadings()
        cly = res.YcorrLoadings()
        # calExplVarX
        cevx = self._ev_list_dict_adapter(res.XcalExplVar_tot_list())
        cevy = self._ev_list_dict_adapter(res.YcalExplVar_tot_list())
        vnx = self.model.dsl.get_by_id(xId).variable_names
        vny = self.model.dsl.get_by_id(yId).variable_names
        pcl = PCScatterPlot(clx, vnx, 'red', cevx, title="X & Y correlation loadings")
        pcl.add_PC_set(cly, vny, 'blue', cevy)
        pcl.plot_circle(True)
        ## pd = ArrayPlotData()
        ## pd.set_data('pc1', clx[:,0])
        ## pd.set_data('pc2', clx[:,1])
        ## pd.set_data('pcy1', cly[:,0])
        ## pd.set_data('pcy2', cly[:,1])
        ## pcl = CCPlotXYCorrLoad(pd)
        ## pcl.title = "X & Y correlation loadings"
        ## pcl.x_axis.title = "PC1 ({0:.0f}%, {1:.0f}%)".format(cevx[0], cevy[0])
        ## pcl.y_axis.title = "PC2 ({0:.0f}%, {1:.0f}%)".format(cevx[1], cevy[1])
        ## pcl.add_data_labels(vnx, 'x1')
        ## pcl.add_data_labels(vny, 'y1')
        return pcl

    def plot_expl_var_x(self):
        for xId, yId in self.get_mappings():
            ev_plot = self._make_expl_var_plot_x(xId, yId)
            spw = LinePlotWindow(
                plot=ev_plot,
                title_text=self._wind_title(xId, yId)
                )
            self._show_plot_window(spw)


    def _ev_rem_zero_adapter(self, ev_list):
        ev_list.pop(0)
        return ev_list


    def _make_expl_var_plot_x(self, xId, yId):
        res = self.model.get_res(xId, yId)
        sumCalX = self._ev_rem_zero_adapter(res.XcumCalExplVar_tot_list())
        pl = EVLinePlot(sumCalX)
        ## expl_index = range(len(sumCalX))
        ## pd = ArrayPlotData(index=expl_index, pc_sigma=sumCalX)
        ## pl = CCPlotLine(pd)
        ## pl.title = "Explained variance X"
        ## pl.x_axis.title = "# f principal components"
        ## pl.y_axis.title = "Explained variance [%]"
        ## pl.y_mapper.range.set_bounds(0, 100)
        return pl

    def plot_expl_var_y(self):
        for xId, yId in self.get_mappings():
            ev_plot = self._make_expl_var_plot_y(xId, yId)
            spw = LinePlotWindow(
                plot=ev_plot,
                title_text=self._wind_title(xId, yId)
                )
            self._show_plot_window(spw)

    def _make_expl_var_plot_y(self, xId, yId):
        res = self.model.get_res(xId, yId)
        sumCalY = self._ev_rem_zero_adapter(res.YcumCalExplVar_tot_list())
        sumValY = self._ev_rem_zero_adapter(res.YcumValExplVar_tot_list())
        pl = EVLinePlot(sumCalY, 'red', 'calibrated Y')
        pl.add_EV_set(sumValY, 'blue', 'validated Y')
        ## expl_index = range(len(sumCalY))
        ## pd = ArrayPlotData()
        ## pd.set_data('index', expl_index)
        ## pd.set_data('pc_cal_sigma', sumCalY)
        ## pd.set_data('pc_val_sigma', sumValY)
        ## pl = CCPlotCalValExplVariance(pd)
        ## pl.title = "Explained variance Y"
        ## pl.x_axis.title = "# f principal components"
        ## pl.y_axis.title = "Explained variance [%]"
        ## pl.y_mapper.range.set_bounds(-50, 100)
        return pl

    def _show_plot_window(self, plot_window):
            # FIXME: Setting parent forcing main ui to stay behind plot windows
            if sys.platform == 'linux2':
                self.plot_uis.append( plot_window.edit_traits(kind='live') )
            else:
                self.plot_uis.append(
                    plot_window.edit_traits(parent=self.info.ui.control, kind='live')
                    )

    def _wind_title(self, dsx_id, dsy_id):
        dsx_name = self.model.dsl.get_by_id(dsx_id)._ds_name
        dsy_name = self.model.dsl.get_by_id(dsy_id)._ds_name
        return "ConsumerCheck Prefmap - ({0}) X ~ Y ({1})".format(dsx_name, dsy_name)


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
                  view = no_view,
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
                  view = prefmap_ui_view,
                  ),
        TreeNode( node_for = [ PrefmapModel ],
                  label = '=Scores',
                  on_dclick = clkScores,
                  view = prefmap_ui_view,
                  ),
        TreeNode( node_for = [ PrefmapModel ],
                  label = '=X & Y correlation loadings',
                  on_dclick = clkCorrLoad,
                  view = prefmap_ui_view,
                  ),
        TreeNode( node_for = [ PrefmapModel ],
                  label = '=Explained variance X',
                  on_dclick = clkExplResVarX,
                  view = prefmap_ui_view,
                  ),
        TreeNode( node_for = [ PrefmapModel ],
                  label = '=Explained variance Y',
                  on_dclick = clkExplResVarY,
                  view = prefmap_ui_view,
                  ),
        TreeNode( node_for = [ PrefmapModel ],
                  label = '=X loadings',
                  on_dclick = clkLoadingsX,
                  view = prefmap_ui_view,
                  ),
        TreeNode( node_for = [ PrefmapModel ],
                  label = '=Y loadings',
                  on_dclick = clkLoadingsY,
                  view = prefmap_ui_view,
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
    print("Interactive start")
    import numpy as np
    from tests.conftest import TestContainer
    # FIXME: How can i make the object instansiating
    # ordering more robust
    container = TestContainer(test_subject = PrefmapsContainer())
    ## with np.errstate(invalid='ignore'):
    ##     container.test_subject.configure_traits(view=prefmap_tree_view)
