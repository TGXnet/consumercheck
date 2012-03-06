

# stdlib imports
import sys
import logging

# Enthought imports
from traits.api import (HasTraits, Instance, Str, List, Button, DelegatesTo,
                        PrototypedFrom, Property, on_trait_change)
from traitsui.api import View, Item, ModelView
from enable.api import BaseTool

# Local imports
from plsr import nipalsPLS2 as pls
from dataset import DataSet
from plot_pc_scatter import PCScatterPlot
from plot_ev_line import EVLinePlot
from plot_windows import SinglePlotWindow, LinePlotWindow, MultiPlotWindow
from ds_slicer_view import ds_obj_slicer_view, ds_var_slicer_view


#Double click tool
class DClickTool(BaseTool):
    plot_dict = {}
    #List that holds the function names
    func_list = ['plot_scores','plot_corr_loading', 'plot_expl_var_x', 'plot_expl_var_y']
    #Triggered on double click
    def normal_left_dclick(self,event):
        self._build_plot_list()
        call_function = getattr(self.ref, self.plot_dict[self.component.title])()
    #Builds a dictionary that holds the function names, based on func_list, with the window title as key
    def _build_plot_list(self):
        for e,i in enumerate(self.component.container.plot_components):
            self.plot_dict[i.title] = self.func_list[e]


class APrefmapModel(HasTraits):
    """Represent the Prefmap model between one X and Y dataset."""
    name = Str()
    # Shoud be Instance(PrefmapsContainer)
    # but who comes first?
    mother_ref = Instance(HasTraits)
    dsX = DataSet()
    dsY = DataSet()
    sub_dsX = DataSet()
    sub_dsY = DataSet()
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
        self.dsY.active_objects = self.dsX.active_objects
        self.sub_dsX = self.dsX.subset()
        self.sub_dsY = self.dsY.subset()
        return pls(
            self.sub_dsX.matrix,
            self.sub_dsY.matrix,
            numPC=self.max_n_pc,
            cvType=["loo"],
            Xstand=self.standardize,
            Ystand=self.standardize)




class APrefmapHandler(ModelView):
    plot_uis = List()
    name = DelegatesTo('model')

    show_sel_obj = Button('Objects')
    show_sel_x_var = Button('X Variables')
    show_sel_y_var = Button('Y Variables')
    
    @on_trait_change('show_sel_obj')
    def _act_show_sel_obj(self, object, name, new):
        object.model.dsX.edit_traits(view=ds_obj_slicer_view, kind='livemodal')

    @on_trait_change('show_sel_x_var')
    def _act_show_sel_x_var(self, object, name, new):
        object.model.dsX.edit_traits(view=ds_var_slicer_view, kind='livemodal')

    @on_trait_change('show_sel_y_var')
    def _act_show_sel_y_var(self, object, name, new):
        object.model.dsY.edit_traits(view=ds_var_slicer_view, kind='livemodal')

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
        for plots in ds_plots:
            for plot in plots:
                plot.tools.append(DClickTool(plot, ref = self))

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
        labels = self.model.sub_dsX.object_names
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
        labels = self.model.sub_dsX.variable_names
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
        labels = self.model.sub_dsY.variable_names
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
        vnx = self.model.sub_dsX.variable_names
        vny = self.model.sub_dsY.variable_names
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
        pl = EVLinePlot(sumCalX, title = "Explained Variance X")
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
        pl = EVLinePlot(sumCalY, 'red', 'calibrated Y', title = "Explained Variance Y")
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
    Item('model.max_n_pc'),
    Item('show_sel_obj'),
    Item('show_sel_x_var'),
    Item('show_sel_y_var'),
    )


if __name__ == '__main__':
    from traits.api import Bool, Enum
    from tests.conftest import make_ds_mock
    dsx = make_ds_mock()
    dsy = make_ds_mock()

    class MocMother(HasTraits):
        standardize = Bool(False)
        max_n_pc = Enum(2,3,4,5,6)

    moc_mother = MocMother()

    model = APrefmapModel(
        name='Tore tes',
        dsX=dsx,
        dsY=dsy,
        mother_ref=moc_mother)

    controller = APrefmapHandler(
        model=model)
    controller.configure_traits(view=a_prefmap_view)
