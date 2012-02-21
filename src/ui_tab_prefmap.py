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
from traits.api import HasTraits, Instance, Enum, Str, List, Button, DelegatesTo, PrototypedFrom, Dict, Any, Bool, Property, Set
from traitsui.api import View, Item, UItem, Handler, ModelView, TreeEditor, TreeNode, CheckListEditor


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

    #checkbox bool for standardized results
    standardize = PrototypedFrom('mother_ref')
    max_n_pc = PrototypedFrom('mother_ref')

    # depends_on
    result = Property()


    def _get_result(self):
        logging.info("Run pls for: X: {0} ,Y: {1}".format(self.dsX._ds_id, self.dsY._ds_id))
        return pls(
            self.dsX.matrix,
            self.dsY.matrix,
            numPC=8,
            cvType=["loo"],
            Xstand=self.standardize,
            Ystand=self.standardize)




class APrefmapHandler(ModelView):
    plot_uis = List()
    name = DelegatesTo('model')

    def __eq__(self, other):
        return self.name == other

    def __ne__(self, other):
        return self.name != other


    def plot_overview(self):
        """Make Prefmap overview plot.

        Plot an array of plots where we plot scores, loadings, corr. load and expl. var
        for each of the datasets.
        """
        ds_plots = [[self._make_scores_plot(), self._make_corr_load_plot()],
                    [self._make_expl_var_plot_x(), self._make_expl_var_plot_y()]]
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
        pc_tab = res.Xscores()
        labels = self.model.dsX.object_names
        expl_vars_x = self._ev_list_dict_adapter(res.XcalExplVar_tot_list())
        # expl_vars_y = self._ev_list_dict_adapter(res.YcalExplVar_tot_list())
        plot = PCScatterPlot(pc_tab, labels, expl_vars=expl_vars_x, title="Scores")
        return plot


    def _ev_list_dict_adapter(self, ev_list):
        return dict([kv for kv in enumerate(ev_list, 1)])


    def plot_loadings_x(self):
        l_plot = self._make_loadings_plot_x()
        spw = SinglePlotWindow(
            plot=l_plot,
            title_text=self._wind_title()
            )
        self._show_plot_window(spw)


    def _make_loadings_plot_x(self):
        res = self.model.result
        xLP = res.Xloadings()
        expl_vars = self._ev_list_dict_adapter(res.XcalExplVar_tot_list())
        labels = self.model.dsX.variable_names
        plot = PCScatterPlot(xLP, labels, expl_vars=expl_vars, title="X Loadings")
        return plot


    def plot_loadings_y(self):
        l_plot = self._make_loadings_plot_y()
        spw = SinglePlotWindow(
            plot=l_plot,
            title_text=self._wind_title()
            )
        self._show_plot_window(spw)


    def _make_loadings_plot_y(self):
        res = self.model.result
        yLP = res.Yloadings()
        expl_vars = self._ev_list_dict_adapter(res.YcalExplVar_tot_list())
        labels = self.model.dsY.variable_names
        plot = PCScatterPlot(yLP, labels, expl_vars=expl_vars, title="Y Loadings")
        return plot


    def plot_corr_loading(self):
        cl_plot = self._make_corr_load_plot()
        spw = SinglePlotWindow(
            plot=cl_plot,
            title_text=self._wind_title()
            )
        self._show_plot_window(spw)


    def _make_corr_load_plot(self):
        # VarNameX, CorrLoadX
        # labels
        res = self.model.result
        clx = res.XcorrLoadings()
        cly = res.YcorrLoadings()
        # calExplVarX
        cevx = self._ev_list_dict_adapter(res.XcalExplVar_tot_list())
        cevy = self._ev_list_dict_adapter(res.YcalExplVar_tot_list())
        vnx = self.model.dsX.variable_names
        vny = self.model.dsY.variable_names
        pcl = PCScatterPlot(clx, vnx, 'red', cevx, title="X & Y correlation loadings")
        pcl.add_PC_set(cly, vny, 'blue', cevy)
        pcl.plot_circle(True)
        return pcl


    def plot_expl_var_x(self):
        ev_plot = self._make_expl_var_plot_x()
        spw = LinePlotWindow(
            plot=ev_plot,
            title_text=self._wind_title()
            )
        self._show_plot_window(spw)


    def _ev_rem_zero_adapter(self, ev_list):
        ev_list.pop(0)
        return ev_list


    def _make_expl_var_plot_x(self):
        res = self.model.result
        sumCalX = self._ev_rem_zero_adapter(res.XcumCalExplVar_tot_list())
        pl = EVLinePlot(sumCalX)
        return pl


    def plot_expl_var_y(self):
        ev_plot = self._make_expl_var_plot_y()
        spw = LinePlotWindow(
            plot=ev_plot,
            title_text=self._wind_title()
            )
        self._show_plot_window(spw)


    def _make_expl_var_plot_y(self):
        res = self.model.result
        sumCalY = self._ev_rem_zero_adapter(res.YcumCalExplVar_tot_list())
        sumValY = self._ev_rem_zero_adapter(res.YcumValExplVar_tot_list())
        pl = EVLinePlot(sumCalY, 'red', 'calibrated Y')
        pl.add_EV_set(sumValY, 'blue', 'validated Y')
        return pl


    def _show_plot_window(self, plot_window):
            # FIXME: Setting parent forcing main ui to stay behind plot windows
            if sys.platform == 'linux2':
                self.plot_uis.append( plot_window.edit_traits(kind='live') )
            else:
                self.plot_uis.append(
                    plot_window.edit_traits(parent=self.info.ui.control, kind='live')
                    )


    ## def closed(self, info, is_ok):
    ##     while self.plot_uis:
    ##         plot_ui = self.plot_uis.pop()
    ##         plot_ui.dispose()


    def _wind_title(self):
        dsx_name = self.model.dsX._ds_name
        dsy_name = self.model.dsY._ds_name
        return "ConsumerCheck Prefmap - ({0}) X ~ Y ({1})".format(dsx_name, dsy_name)


a_prefmap_view = View(
    Item('model.name'),
    Item('model.standardize'),
    Item('model.max_n_pc')
    )




class PrefmapsContainer(HasTraits):
    """Prefmap plugin container."""
    name = Str('Define preference mapping')
    # Instance(MainUi)?
    # WeakRef?
    mother_ref = Instance(HasTraits)
    dsl = DelegatesTo('mother_ref')
    mappings = List(APrefmapHandler)

    # Fitting parameters
    standardize = Bool(False)
    max_n_pc = Enum(2,3,4,5,6)

    def add_mapping(self, id_x, id_y):
        set_x = self.dsl.get_by_id(id_x)
        set_y = self.dsl.get_by_id(id_y)
        map_name = id_x + id_y
        mapping_model = APrefmapModel(mother_ref=self, name=map_name,  dsX=set_x, dsY=set_y)
        mapping_handler = APrefmapHandler(mapping_model)
        self.mappings.append(mapping_handler)
        return map_name


    def remove_mapping(self, mapping_id):
        del(self.mappings[self.mappings.index(mapping_id)])



class PrefmapsHandler(ModelView):
    name = DelegatesTo('model')
    mappings = DelegatesTo('model')
    test = List()
    # [('a_labels','c_labels'),('sensorydata','consumerliking')]
    last_selection = Set()


    def handler_test_changed(self, info):
        if not info.initialized:
            return

        selection = set(info.ui.context['handler'].test)
        if selection.difference(self.last_selection):
            added = selection.difference(self.last_selection)
            self.last_selection = selection
            print("Added", added)
            if 'a_labels' in added:
                info.ui.context['model'].add_mapping('a_labels','c_labels')
            elif 'sensorydata' in added:
                info.ui.context['model'].add_mapping('sensorydata','consumerliking')
        else:
            removed = self.last_selection.difference(selection)
            print("Removed", removed)
            self.last_selection = selection
            if 'a_labels' in removed:
                info.ui.context['model'].remove_mapping('a_labelsc_labels')
            elif 'sensorydata' in removed:
                info.ui.context['model'].remove_mapping('sensorydataconsumerliking')





prefmaps_view = View(
    Item('test', editor=CheckListEditor(values=['a_labels', 'sensorydata'],),
         style='custom'),
    Item('model.standardize'),
    Item('model.max_n_pc'),
    )


def dclk_overview(obj):
    obj.plot_overview()

def dclk_scores(obj):
    obj.plot_scores()

def dclk_corr_load(obj):
    obj.plot_corr_loading()

def dclk_expl_var_x(obj):
    obj.plot_expl_var_x()

def dclk_expl_var_y(obj):
    obj.plot_expl_var_y()

def dclk_loadings_x(obj):
    obj.plot_loadings_x()

def dclk_loadings_y(obj):
    obj.plot_loadings_y()

    

new_prefmap_tree = TreeEditor(
    nodes = [
        TreeNode(
            node_for = [PrefmapsHandler],
            children = '',
            label = 'name',
            view = prefmaps_view,
            ),
        TreeNode(
            node_for = [PrefmapsHandler],
            children = 'mappings',
            label = 'name',
            view = prefmaps_view,
            rename = False,
            rename_me = False,
            copy = False,
            delete = False,
            delete_me = False,
            insert = False,
            auto_open = True,
            
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            children = '',
            label = 'name',
            view = a_prefmap_view,
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            label = '=Overview plot',
            on_dclick = dclk_overview,
            view = a_prefmap_view,
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            label = '=Scores plot',
            on_dclick = dclk_scores,
            view = a_prefmap_view,
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            label = '=X ~ Y correlation loadings plot',
            on_dclick = dclk_corr_load,
            view = a_prefmap_view,
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            label = '=Explained var X plot',
            on_dclick = dclk_expl_var_x,
            view = a_prefmap_view,
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            label = '=Explained var Y plot',
            on_dclick = dclk_expl_var_y,
            view = a_prefmap_view,
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            label = '=X loadings plot',
            on_dclick = dclk_loadings_x,
            view = a_prefmap_view,
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            label = '=Y loadings plot',
            on_dclick = dclk_loadings_y,
            view = a_prefmap_view,
            ),
        ],
    hide_root = True,
    # editable = False,
    auto_open = 2,
    )



class PrefmapPlugin(HasTraits):
    model_view = PrefmapsHandler()

    test_view = View(
        Item(name='model_view',
             editor=new_prefmap_tree,
             show_label=False),
        resizable=True,
        height=400,
        width=600,
        )


## Old version #################################################################


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
    
    #checkbox bool for standardized results
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

    with np.errstate(invalid='ignore'):
        td = PrefmapPlugin(model_view=PrefmapsHandler(PrefmapsContainer()))
        container = TestContainer(test_subject = td.model_view.model)
        td.configure_traits()
