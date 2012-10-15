
# stdlib imports
import sys
import logging

# Enthought imports
from traits.api import (HasTraits, Instance, Str, List, Button, DelegatesTo,
                        Property, on_trait_change)
from traitsui.api import View, Group, Item, ModelView, RangeEditor

# Local imports
from plsr import nipalsPLS2 as pls
from dataset import DataSet
from plot_pc_scatter import PCScatterPlot
from plot_ev_line import EVLinePlot
from plot_windows import SinglePlotWindow, LinePlotWindow, MultiPlotWindow
from ds_slicer_view import ds_obj_slicer_view, ds_var_slicer_view
from plugin_tree_helper import WindowLauncher


class APrefmapModel(HasTraits):
    """Represent the Prefmap model between one X and Y dataset."""
    name = Str()
    plot_type = Str()
    nid = Str()
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

    #checkbox bool for standardised results
    standardise = DelegatesTo('mother_ref')
    pc_to_calc = DelegatesTo('mother_ref')
    min_pc = 2
    max_pc = Property()
    
    # depends_on
    result = Property()

    def _get_max_pc(self):
        return (min(self.dsX.n_rows,self.dsX.n_cols))

    def _get_result(self):
        logging.info("Run pls for: X: {0} ,Y: {1}".format(self.dsX._ds_id, self.dsY._ds_id))
        self.dsY.active_objects = self.dsX.active_objects
        self.sub_dsX = self.dsX.subset()
        self.sub_dsY = self.dsY.subset()
        if self.mother_ref.radio == 'Internal mapping':
            return pls(
                       self.sub_dsX.matrix,
                       self.sub_dsY.matrix,
                       numPC=self.pc_to_calc,
                       cvType=["loo"],
                       Xstand=self.standardise,
                       Ystand=self.standardise)
        else:
            return pls(
                       self.sub_dsY.matrix,
                       self.sub_dsX.matrix,
                       numPC=self.pc_to_calc,
                       cvType=["loo"],
                       Ystand=self.standardise,
                       Xstand=self.standardise,)

class APrefmapHandler(ModelView):
    plot_uis = List()
    name = DelegatesTo('model')
    nid = DelegatesTo('model')

    show_sel_obj = Button('Objects')
    show_sel_x_var = Button('X Variables')
    show_sel_y_var = Button('Y Variables')

    window_launchers = List(Instance(WindowLauncher))
    
    
    def __init__(self, *args, **kwargs):
        super(APrefmapHandler, self).__init__(*args, **kwargs)
        self._populate_window_launchers()

    
    @on_trait_change('show_sel_obj')
    def _act_show_sel_obj(self, obj, name, new):
        obj.model.dsX.edit_traits(view=ds_obj_slicer_view, kind='livemodal')

    @on_trait_change('show_sel_x_var')
    def _act_show_sel_x_var(self, obj, name, new):
        obj.model.dsX.edit_traits(view=ds_var_slicer_view, kind='livemodal')

    @on_trait_change('show_sel_y_var')
    def _act_show_sel_y_var(self, obj, name, new):
        obj.model.dsY.edit_traits(view=ds_var_slicer_view, kind='livemodal')

    def __eq__(self, other):
        return self.nid == other

    def __ne__(self, other):
        return self.nid != other


    def _populate_window_launchers(self):

        std_launchers = [
            ("Overview", "plot_overview"),
            ("Scores", "plot_scores"),
            ("X ~ Y correlation loadings", "plot_corr_loading"),
            ("Explained var X", "plot_expl_var_x"),
            ("Explained var Y", "plot_expl_var_y"),
            ("X loadings", "plot_loadings_x"),
            ("Y loadings", "plot_loadings_y"),
            ]

        self.window_launchers = [WindowLauncher(node_name=nn, func_name=fn, owner_ref=self) for nn, fn in std_launchers]


    def plot_overview(self):
        """Make Prefmap overview plot.

        Plot an array of plots where we plot scores, loadings, corr. load and expl. var
        for each of the datasets.
        """
        
        self.model.plot_type = 'Overview Plot'
        
        ds_plots = [[self._make_scores_plot(True), self._make_corr_load_plot(True)],
                    [self._make_expl_var_plot_x(True), self._make_expl_var_plot_y(True)]]

        mpw = MultiPlotWindow(title_text=self._wind_title())
        mpw.plots.component_grid = ds_plots
        mpw.plots.shape = (2, 2)
        self._show_plot_window(mpw)



    def plot_scores(self):
        self.model.plot_type = 'Scores Plot'
        s_plot = self._make_scores_plot()
        spw = SinglePlotWindow(
            plot=s_plot,
            title_text=self._wind_title(),
            vistog=False
            )
        self._show_plot_window(spw)


    def _make_scores_plot(self, is_subplot=False):
        res = self.model.result
        pc_tab = res.X_scores()
        labels = self.model.sub_dsX.object_names
        expl_vars_x = res.X_calExplVar()
        plot = PCScatterPlot(pc_tab, labels, expl_vars=expl_vars_x, title="Scores")
        if is_subplot:
            plot.add_left_down_action(self.plot_scores)
        return plot


    def _ev_list_dict_adapter(self, ev_list):
        return dict([kv for kv in enumerate(ev_list, 1)])


    def plot_loadings_x(self):
        self.model.plot_type = 'Loadings X Plot'
        l_plot = self._make_loadings_plot_x()
        spw = SinglePlotWindow(
            plot=l_plot,
            title_text=self._wind_title(),
            vistog=False
            )
        self._show_plot_window(spw)


    def _make_loadings_plot_x(self, is_subplot=False):
        res = self.model.result
        xLP = res.X_loadings()
        expl_vars = res.X_calExplVar()
        if self.model.mother_ref.radio == 'Internal mapping':
            labels = self.model.sub_dsX.variable_names
        else:
            labels = self.model.sub_dsY.variable_names
        plot = PCScatterPlot(xLP, labels, expl_vars=expl_vars, title="X Loadings")
        if is_subplot:
            plot.add_left_down_action(self.plot_loadings_x)
        return plot


    def plot_loadings_y(self):
        self.model.plot_type = 'Loadings Y Plot'
        l_plot = self._make_loadings_plot_y()
        spw = SinglePlotWindow(
            plot=l_plot,
            title_text=self._wind_title(),
            vistog=False
            )
        self._show_plot_window(spw)


    def _make_loadings_plot_y(self, is_subplot=False):
        res = self.model.result
        yLP = res.Y_loadings()
        expl_vars = res.Y_calExplVar()
        labels = self.model.sub_dsY.variable_names
        plot = PCScatterPlot(yLP, labels, expl_vars=expl_vars, title="Y Loadings")
        if is_subplot:
            plot.add_left_down_action(self.plot_loadings_y)
        return plot


    def plot_corr_loading(self):
        self.model.plot_type = 'Correlation Loadings Plot'
        cl_plot = self._make_corr_load_plot()
        spw = SinglePlotWindow(
            plot=cl_plot,
            title_text=self._wind_title(),
            vistog=True
            )
        self._show_plot_window(spw)


    def _make_corr_load_plot(self, is_subplot=False):
        # VarNameX, CorrLoadX
        # labels
        res = self.model.result
        clx = res.X_corrLoadings()
        cly = res.Y_corrLoadings()
        # calExplVarX
        cevx = res.X_calExplVar()
        cevy = res.Y_calExplVar()
        if self.model.mother_ref.radio == 'Internal mapping':
            vnx = self.model.sub_dsX.variable_names
            vny = self.model.sub_dsY.variable_names
        else:
            vnx = self.model.sub_dsY.variable_names
            vny = self.model.sub_dsX.variable_names
        
        pcl = PCScatterPlot(clx, vnx, 'darkviolet', cevx, title="X & Y correlation loadings")
        pcl.add_PC_set(cly, vny, 'darkgoldenrod', cevy)
        
        if is_subplot:
            pcl.add_left_down_action(self.plot_corr_loading)
        pcl.plot_circle(True)
        return pcl


    def plot_expl_var_x(self):
        self.model.plot_type = 'Explained Variance X Plot'
        ev_plot = self._make_expl_var_plot_x()
        ev_plot.legend.visible = True
        spw = LinePlotWindow(
            plot=ev_plot,
            title_text=self._wind_title(),
            vistog=False
            )
        self._show_plot_window(spw)


    def _ev_rem_zero_adapter(self, ev_list):
        ev_list.pop(0)
        return ev_list


    def _make_expl_var_plot_x(self, is_subplot=False):
        res = self.model.result
        sumCalX = res.X_cumCalExplVar()
        sumValX = res.X_cumValExplVar()
        pl = EVLinePlot(sumCalX, 'darkviolet', 'Calibrated X', title = "Explained Variance X")
        pl.add_EV_set(sumValX, 'darkgoldenrod', 'Validated X')
        print 'x plot function running'
        if is_subplot:
            pl.add_left_down_action(self.plot_expl_var_x)
        return pl


    def plot_expl_var_y(self):
        self.model.plot_type = 'Explained Variance Y Plot'
        ev_plot = self._make_expl_var_plot_y()
        ev_plot.legend.visible = True
        spw = LinePlotWindow(
            plot=ev_plot,
            title_text=self._wind_title(),
            vistog=False
            )
        self._show_plot_window(spw)


    def _make_expl_var_plot_y(self, is_subplot=False):
        res = self.model.result
        sumCalY = res.Y_cumCalExplVar()
        sumValY = res.Y_cumValExplVar()
        pl = EVLinePlot(sumCalY, 'darkviolet', 'Calibrated Y', title = "Explained Variance Y")
        pl.add_EV_set(sumValY, 'darkgoldenrod', 'Validated Y')
        if is_subplot:
            pl.add_left_down_action(self.plot_expl_var_y)
        return pl


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



    ## def closed(self, info, is_ok):
    ##     while self.plot_uis:
    ##         plot_ui = self.plot_uis.pop()
    ##         plot_ui.dispose()


    def _wind_title(self):
        dsx_name = self.model.dsX._ds_name
        dsy_name = self.model.dsY._ds_name
        dstype = self.model.plot_type
        return "({0}) X ~ Y ({1}) | Prefmap - {2} - ConsumerCheck".format(dsx_name, dsy_name, dstype)


a_prefmap_view = View(
    Group(
        Group(
            Item('model.name'),
            Item('model.standardise'),
            Item('model.pc_to_calc',
                 editor=RangeEditor(
                     low_name='model.min_pc',
                     high_name='model.max_pc',
                     mode='spinner')),
            Item('show_sel_obj'),
            Item('show_sel_x_var'),
            Item('show_sel_y_var'),
            ),
        Item('', springy=True),
        orientation='horizontal',
        ),
    )


if __name__ == '__main__':
    import numpy as np
    from traits.api import Bool, Int
    from tests.conftest import make_dsl_mock
    dsl = make_dsl_mock()
    dsx = dsl.get_by_id('consumerliking')
    dsy = dsl.get_by_id('sensorydata')

    class MocMother(HasTraits):
        standardise = Bool(False)
        pc_to_calc = Int(2)

    moc_mother = MocMother()

    model = APrefmapModel(
        name='Tore tes',
        dsX=dsx,
        dsY=dsy,
        mother_ref=moc_mother)

    class APrefmapTestHandler(APrefmapHandler):
        bt_plot_overview = Button('Plot overview')
        bt_plot_scores = Button('Plot scores')
        bt_plot_loadings_x = Button('Plot loadings X')
        bt_plot_loadings_y = Button('Plot loadings Y')
        bt_plot_corr_loadings = Button('Plot corr loadings')
        bt_plot_expl_var_x = Button('Plot explainded variance X')
        bt_plot_expl_var_y = Button('Plot explainded variance Y')

        @on_trait_change('bt_plot_overview')
        def _on_bpo(self, obj, name, new):
            self.plot_overview()

        @on_trait_change('bt_plot_scores')
        def _on_bps(self, obj, name, new):
            self.plot_scores()

        @on_trait_change('bt_plot_loadings_x')
        def _on_bplx(self, obj, name, new):
            self.plot_loadings_x()

        @on_trait_change('bt_plot_loadings_y')
        def _on_bply(self, obj, name, new):
            self.plot_loadings_y()

        @on_trait_change('bt_plot_corr_loadings')
        def _on_bpcl(self, obj, name, new):
            self.plot_corr_loading()

        @on_trait_change('bt_plot_expl_var_x')
        def _on_bpevx(self, obj, name, new):
            self.plot_expl_var_x()

        @on_trait_change('bt_plot_expl_var_y')
        def _on_bpevy(self, obj, name, new):
            self.plot_expl_var_y()

        traits_view = View(
            Group(
                Group(
                    Item('model.name'),
                    Item('model.standardise'),
                    Item('model.pc_to_calc',
                         editor=RangeEditor(
                             low_name='model.min_pc',
                             high_name='model.max_pc',
                             mode='spinner')),
                    Item('show_sel_obj'),
                    Item('show_sel_x_var'),
                    Item('show_sel_y_var'),
                    orientation='vertical',
                    ),
                Item('', springy=True),
                Group(
                    Item('bt_plot_overview'),
                    Item('bt_plot_scores'),
                    Item('bt_plot_loadings_x'),
                    Item('bt_plot_loadings_y'),
                    Item('bt_plot_corr_loadings'),
                    Item('bt_plot_expl_var_x'),
                    Item('bt_plot_expl_var_y'),
                    ),
                orientation='horizontal',
                ),
            resizable=True,
            )


    controller = APrefmapTestHandler(
        model=model)
    with np.errstate(invalid='ignore'):
        controller.configure_traits()
