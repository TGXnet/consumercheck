
# stdlib imports
import sys

# Enthought imports
from traits.api import (HasTraits, Instance, Str, List, Button, DelegatesTo,
                        Property, on_trait_change)
from traitsui.api import View, Group, Item, ModelView, RangeEditor
from traitsui.menu import OKButton
import numpy as np

# Local imports
from pca import nipalsPCA as PCA
from dataset import DataSet
from plot_pc_scatter import PCScatterPlot
from plot_ev_line import EVLinePlot
from plot_windows import SinglePlotWindow, LinePlotWindow, MultiPlotWindow
from ds_slicer_view import ds_obj_slicer_view, ds_var_slicer_view
from ui_results_new import TableViewController
from plugin_tree_helper import WindowLauncher


class InComputeable(Exception):
    pass


class ErrorMessage(HasTraits):
    err_msg = Str()
    traits_view = View(Item('err_msg', style='readonly',
                            label='Zero variance variables'),
                       buttons=[OKButton], title='Warning')


class APCAModel(HasTraits):
    """Represent the PCA model of a dataset."""
    name = Str()
    plot_type = Str()
    nid = Str()
    # Shoud be Instance(PrefmapsContainer)
    # but who comes first?
    mother_ref = Instance(HasTraits)
    ds = DataSet()
    sub_ds = DataSet()
    # List of variable names with zero variance in the data vector
    zero_variance = List()
    # FIXME: To be replaced by groups
    sel_var = List()
    sel_obj = List()

    #checkbox bool for standardised results
    standardise = DelegatesTo('mother_ref')
    pc_to_calc = DelegatesTo('mother_ref')
    min_pc = 2
    max_pc = Property()

    # depends_on
    result = Property()

    def _get_max_pc(self):
        return (min(self.ds.n_rows, self.ds.n_cols)-2)


    def _check_std_dev(self):
        sv = self.sub_ds.matrix.std(0)
        std_limit = 0.001
        dm = sv < std_limit
        if np.any(dm):
            vv = np.array(self.sub_ds.variable_names)
            self.zero_variance = list(vv[np.nonzero(dm)])
        else:
            self.zero_variance = []


    def _get_result(self):
        self.sub_ds = self.ds.subset()
        std_ds = 'cent'
        if self.standardise:
            std_ds = 'stand'
        self._check_std_dev()
        if self.zero_variance and self.standardise:
            raise InComputeable('PCA: matrix have vectors with zero variance')
        return PCA(self.sub_ds.matrix,
                   numPC=self.pc_to_calc,
                   mode=std_ds,
                   cvType=["loo"])


class APCAHandler(ModelView):
    plot_uis = List()
    name = DelegatesTo('model')
    nid = DelegatesTo('model')

    show_sel_obj = Button('Objects')
    show_sel_var = Button('Variables')

    window_launchers = List(Instance(WindowLauncher))


    def __init__(self, *args, **kwargs):
        super(APCAHandler, self).__init__(*args, **kwargs)
        self._populate_window_launchers()


    @on_trait_change('show_sel_obj')
    def _act_show_sel_obj(self, obj, name, new):
        obj.model.ds.edit_traits(view=ds_obj_slicer_view, kind='livemodal')


    @on_trait_change('show_sel_var')
    def _act_show_sel_var(self, obj, name, new):
        obj.model.ds.edit_traits(view=ds_var_slicer_view, kind='livemodal')


    def __eq__(self, other):
        return self.nid == other


    def __ne__(self, other):
        return self.nid != other


    def _populate_window_launchers(self):
        try:
            adv_enable = self.model.mother_ref.mother_ref.en_advanced
        except AttributeError:
            adv_enable = False

        std_launchers = [
            ("Overview", "plot_overview"),
            ("Scores", "plot_scores"),
            ("Loadings", "plot_loadings"),
            ("Correlation loadings", "plot_corr_loading"),
            ("Explained variance", "plot_expl_var"),
            ]

        adv_launchers = [
            # ("Show residuals (subtree)", "show_residuals"),
            # ("Predicated X cal", "show_pred_x_cal"),
            # ("Predicated X val", "show_pred_x_val"),
            ("MSEE total (explained variance", "show_msee_tot"),
            ("MSEE individual", "show_msee_ind"),
            ("MSECV total", "show_msecv_tot"),
            ("MSECV individual", "show_msecv_ind"),
            ]

        if adv_enable:
            std_launchers.extend(adv_launchers)
        self.window_launchers = [WindowLauncher(node_name=nn, func_name=fn, owner_ref=self) for nn, fn in std_launchers]


    def _show_zero_var_warning(self):
        dlg = ErrorMessage()
        for vn in self.model.zero_variance:
            dlg.err_msg += vn + ', '
        dlg.edit_traits()


    def plot_overview(self):
        """Make PCA overview plot.

        Plot an array of plots where we plot scores, loadings, corr. load and expl. var
        for each of the datasets.
        """
        self.model.plot_type = 'Overview Plot'

        try:
            ds_plots = [[self._make_scores_plot(True), self._make_loadings_plot(True)],
                        [self._make_corr_load_plot(True), self._make_expl_var_plot(True)]]
        except InComputeable:
            self._show_zero_var_warning()
            return

        mpw = MultiPlotWindow(title_text=self._wind_title())
        mpw.plots.component_grid = ds_plots
        mpw.plots.shape = (2, 2)
        self._show_plot_window(mpw)


    def plot_scores(self):
        self.model.plot_type = 'Scores Plot'
        try:
            s_plot = self._make_scores_plot()
        except InComputeable:
            self._show_zero_var_warning()
            return

        spw = SinglePlotWindow(
            plot=s_plot,
            title_text=self._wind_title(),
            vistog=False
            )
        self._show_plot_window(spw)


    def _make_scores_plot(self, is_subplot=False):
        res = self.model.result
        pc_tab = res.scores()
        labels = self.model.sub_ds.object_names

        # Make table view dataset
        score_ds = DataSet()
        score_ds._ds_name = self.model.sub_ds._ds_name
        score_ds.matrix = pc_tab
        score_ds.object_names = labels
        score_ds.variable_names = ["PC-{0}".format(i+1) for i in range(score_ds.n_cols)]

        plot = PCScatterPlot(pc_tab, labels, view_data=score_ds, title="Scores", id='scores')
        if is_subplot:
            plot.add_left_down_action(self.plot_scores)
        return plot



    def plot_loadings(self):
        self.model.plot_type = 'Loadings Plot'
        try:
            l_plot = self._make_loadings_plot()
        except InComputeable:
            self._show_zero_var_warning()
            return

        spw = SinglePlotWindow(
            plot=l_plot,
            title_text=self._wind_title(),
            vistog=False
            )
        self._show_plot_window(spw)


    def _make_loadings_plot(self, is_subplot=False):
        res = self.model.result
        pc_tab = res.loadings()
        labels = self.model.sub_ds.variable_names

        # Make table view dataset
        loadings_ds = DataSet()
        loadings_ds._ds_name = self.model.sub_ds._ds_name
        loadings_ds.matrix = pc_tab
        loadings_ds.object_names = labels
        loadings_ds.variable_names = ["PC-{0}".format(i+1) for i in range(loadings_ds.n_cols)]

        plot = PCScatterPlot(pc_tab, labels, view_data=loadings_ds, title="Loadings", id="loadings")
        if is_subplot:
            plot.add_left_down_action(self.plot_loadings)
        return plot


    def plot_corr_loading(self):
        self.model.plot_type = 'Correlation Loadings Plot'
        try:
            cl_plot = self._make_corr_load_plot()
        except InComputeable:
            self._show_zero_var_warning()
            return

        spw = SinglePlotWindow(
            plot=cl_plot,
            title_text=self._wind_title(),
            vistog=False
            )
        self._show_plot_window(spw)


    def _make_corr_load_plot(self, is_subplot=False):
        res = self.model.result
        pc_tab = res.corrLoadings()
        expl_vars = res.calExplVar()
        labels = self.model.sub_ds.variable_names

        # Make table view dataset
        corr_loadings_ds = DataSet()
        corr_loadings_ds._ds_name = self.model.sub_ds._ds_name
        corr_loadings_ds.matrix = pc_tab
        corr_loadings_ds.object_names = labels
        corr_loadings_ds.variable_names = ["PC-{0}".format(i+1) for i in range(corr_loadings_ds.n_cols)]

        pcl = PCScatterPlot(pc_tab, labels, expl_vars=expl_vars, view_data=corr_loadings_ds, title="Correlation Loadings", id="corr_loading")
        pcl.plot_circle(True)
        if is_subplot:
            pcl.add_left_down_action(self.plot_corr_loading)
        return pcl


    def plot_expl_var(self):
        self.model.plot_type = 'Explained Variance Plot'
        try:
            ev_plot = self._make_expl_var_plot()
        except InComputeable:
            self._show_zero_var_warning()
            return

        ev_plot.legend.visible = True
        spw = LinePlotWindow(
            plot=ev_plot,
            title_text=self._wind_title(),
            vistog=False
            )
        self._show_plot_window(spw)


    def _make_expl_var_plot(self, is_subplot=False):
        res = self.model.result
        sumCal = res.cumCalExplVar()
        sumVal = res.cumValExplVar()

        # Make table view dataset
        ev_ds = DataSet()
        ev_ds._ds_name = self.model.sub_ds._ds_name

        pc_tab = np.array([sumCal, sumVal])
        ev_ds.matrix = pc_tab.T
        ev_ds.object_names = ["PC-{0}".format(i) for i in range(ev_ds.n_rows)]
        ev_ds.variable_names = ["calibrated", "validated"]

        pl = EVLinePlot(sumCal, 'darkviolet', 'Calibrated', view_data=ev_ds, title="Explained Variance", id="expl_var")
        pl.add_EV_set(sumVal, 'darkgoldenrod', 'Validated')
        if is_subplot:
            pl.add_left_down_action(self.plot_expl_var)
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


    def show_residuals(self):
        resids = self.model.result.residuals()
        print(resids)


    def show_pred_x_cal(self):
        cal_pred_x = self.model.result.calPredX()
        print(cal_pred_x)


    def show_pred_x_val(self):
        val_pred_x = self.model.result.valPredX()
        print(val_pred_x)


    def show_msee_tot(self):
        print("MSEE total")
        msee = self.model.result.MSEE()
        tv = TableViewController(title="MSEE total")
        tv.set_col_names([str(i) for i in range(msee.shape[0])])
        tv.add_row(msee, 'MSEE')
        tv.edit_traits()


    def show_msee_ind(self):
        print("MSEE for each variable")
        ind_var_msee = self.model.result.MSEE_indVar()
        tv = TableViewController(title="MSEE individual variables")
        tv.set_col_names([str(i) for i in range(ind_var_msee.shape[1])])
        for i in range(ind_var_msee.shape[0]):
            tv.add_row(ind_var_msee[i,:], 'MSEE')
        tv.edit_traits()


    def show_msecv_tot(self):
        print("MSECV total")
        msecv = self.model.result.MSECV()
        tv = TableViewController(title="MSECV total")
        tv.set_col_names([str(i) for i in range(msecv.shape[0])])
        tv.add_row(msecv, 'MSECV')
        tv.edit_traits()


    def show_msecv_ind(self):
        print("MSECV for each variable")
        ind_var_msecv = self.model.result.MSECV_indVar()
        tv = TableViewController(title="MSECV individual variables")
        tv.set_col_names([str(i) for i in range(ind_var_msecv.shape[1])])
        for i in range(ind_var_msecv.shape[0]):
            tv.add_row(ind_var_msecv[i,:], 'MSECV')
        tv.edit_traits()
    
    
    def show_next_plot(self, window):
            if 'scores' == window.plot.id:
                window.plot = self._make_loadings_plot()
            elif 'loadings' == window.plot.id:
                window.plot = self._make_corr_load_plot()
            elif 'corr_loading' == window.plot.id:
                window.plot = self._make_expl_var_plot()
            elif 'expl_var' == window.plot.id:
                window.plot = self._make_scores_plot()


    def show_previous_plot(self, window):
            if 'corr_loading' == window.plot.id:
                window.plot = self._make_loadings_plot()
            elif 'expl_var' == window.plot.id:
                window.plot = self._make_corr_load_plot()
            elif 'scores' == window.plot.id:
                window.plot = self._make_expl_var_plot()
            elif 'loadings' == window.plot.id:
                window.plot = self._make_scores_plot()
                
                
    def _show_plot_window(self, plot_window):
        # FIXME: Setting parent forcing main ui to stay behind plot windows
        plot_window.mother_ref = self
        if sys.platform == 'linux2':
            self.plot_uis.append(
                plot_window.edit_traits(parent=self.model.mother_ref.win_handle, kind='live')
                )
        elif sys.platform == 'win32':
            # FIXME: Investigate more here
            self.plot_uis.append(
                plot_window.edit_traits(parent=self.model.mother_ref.win_handle, kind='live')
                # plot_window.edit_traits(kind='live')
                )
        else:
            raise Exception("Not implemented for this platform: ".format(sys.platform))


    def _wind_title(self):
        ds_name = self.model.ds._ds_name
        dstype = self.model.plot_type
        return "{0} | PCA - {1} - ConsumerCheck".format(ds_name, dstype)


a_pca_view = View(
    Group(
        Group(
            Item('model.name'),
            Item('model.standardise'),
            Item('model.pc_to_calc',editor=RangeEditor(low_name='model.min_pc',high_name='model.max_pc',mode='spinner')),
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
    # mother_ref: standardise, pc_to_calc
    from traits.api import Bool, Int
    from tests.conftest import simple_ds, imp_ds

    ds_meta = ('Vine', 'A_labels.txt', 'Vine set A', 'Consumer liking')
    ds = imp_ds(ds_meta)


    class MocMother(HasTraits):
        standardise = Bool(False)
        pc_to_calc = Int(2)
        win_handle = None

    moc_mother = MocMother()

    model = APCAModel(
        name='Tore test',
        ds=ds,
        mother_ref=moc_mother)


    class APCATestHandler(APCAHandler):
        bt_plot_overview = Button('Plot overview')
        bt_plot_scores = Button('Plot scores')
        bt_plot_loadings = Button('Plot loadings')
        bt_plot_corr_loadings = Button('Plot corr loadings')
        bt_plot_expl_var = Button('Plot explainded variance')

        @on_trait_change('bt_plot_overview')
        def _on_bpo(self, obj, name, new):
            self.plot_overview()

        @on_trait_change('bt_plot_scores')
        def _on_bps(self, obj, name, new):
            self.plot_scores()

        @on_trait_change('bt_plot_loadings')
        def _on_bpl(self, obj, name, new):
            self.plot_loadings()

        @on_trait_change('bt_plot_corr_loadings')
        def _on_bpcl(self, obj, name, new):
            self.plot_corr_loading()

        @on_trait_change('bt_plot_expl_var')
        def _on_bpev(self, obj, name, new):
            self.plot_expl_var()

        traits_view = View(
            Group(
                Group(
                    Item('model.name'),
                    Item('model.standardise'),
                    Item('model.pc_to_calc'),
                    Item('show_sel_obj',
                         show_label=False),
                    Item('show_sel_var',
                         show_label=False),
                    orientation='vertical',
                    ),
                Item('', springy=True),
                Group(
                    Item('bt_plot_overview'),
                    Item('bt_plot_scores'),
                    Item('bt_plot_loadings'),
                    Item('bt_plot_corr_loadings'),
                    Item('bt_plot_expl_var'),
                    ),
                orientation='horizontal',
                ),
            resizable=True,
            )


    controller = APCATestHandler(
        model=model)
    with np.errstate(invalid='ignore'):
        controller.configure_traits()
