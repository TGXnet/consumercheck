
# Std lib imports
import sys

# Scipy imports
import numpy as _np
import pandas as _pd

# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui

# Local imports
from dataset import DataSet
from pca_model import PcaPlugin, InComputeable
from plot_ev_line import EVLinePlot
from plot_pc_scatter import PCScatterPlot
from plot_windows import SinglePlotWindow, LinePlotWindow, MultiPlotWindow
from plugin_tree_helper import WindowLauncher, dclk_activator
from ui_results import TableViewController


class ErrorMessage(_traits.HasTraits):
    err_msg = _traits.Str()
    traits_view = _traitsui.View(_traitsui.Item('err_msg', style='readonly',
                            label='Zero variance variables'),
                       buttons=[_traitsui.OKButton], title='Warning')


class PcaController(_traitsui.Controller):
    '''Controller for one PCA object'''
    id = _traits.DelegatesTo('model')
    name = _traits.Str()
    window_launchers = _traits.List(_traits.Instance(WindowLauncher))
    plot_uis = _traits.List()


    def _name_default(self):
        return self.model.ds.display_name


    def _window_launchers_default(self):
        return self._populate_window_launchers()


    def __eq__(self, other):
        return self.id == other


    def __ne__(self, other):
        return self.id != other


    def _populate_window_launchers(self):
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
        return [WindowLauncher(node_name=nn, func_name=fn, owner_ref=self) for nn, fn in std_launchers]


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
        res = self.model.pca_res
        pc_tab = res.scores.values
        labels = self.model.ds.obj_n

        # Make table view dataset
        pc_df = _pd.DataFrame(
            pc_tab,
            index=labels,
            columns=["PC-{0}".format(i+1) for i in range(pc_tab.shape[1])])
        score_ds = DataSet(
            mat=pc_df,
            display_name=self.model.ds.display_name)

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
        res = self.model.pca_res
        pc_tab = res.loadings.values
        labels = self.model.ds.var_n

        # Make table view dataset
        pc_df = _pd.DataFrame(
            pc_tab,
            index=labels,
            columns=["PC-{0}".format(i+1) for i in range(pc_tab.shape[1])])
        loadings_ds = DataSet(
            mat=pc_df,
            display_name=self.model.ds.display_name)

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
        res = self.model.pca_res
        pc_tab = res.corr_loadings.values
        expl_vars = list(res.expl_var.values[0])
        labels = self.model.ds.var_n

        # Make table view dataset
        pc_df = _pd.DataFrame(
            pc_tab,
            index=labels,
            columns=["PC-{0}".format(i+1) for i in range(pc_tab.shape[1])])
        corr_loadings_ds = DataSet(
            mat=pc_df,
            display_name=self.model.ds.display_name)

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
        res = self.model.pca_res
        cum_expl_v = _np.cumsum(_np.insert(res.expl_var.values, 0, 0, axis=1), axis=1)
        sumCal = cum_expl_v[0]
        sumVal = cum_expl_v[1]

        # Make table view dataset
        pc_tab = _np.array([sumCal, sumVal]).T
        pc_df = _pd.DataFrame(
            pc_tab,
            index=["PC-{0}".format(i) for i in range(pc_tab.shape[0])],
            columns=["calibrated", "validated"])
        ev_ds = DataSet(
            mat=pc_df,
            display_name=self.model.ds.display_name)

        pl = EVLinePlot(sumCal, 'darkviolet', 'Calibrated', view_data=ev_ds, title="Explained Variance", id="expl_var")
        pl.add_EV_set(sumVal, 'darkgoldenrod', 'Validated')
        if is_subplot:
            pl.add_left_down_action(self.plot_expl_var)
        return pl


    def show_residuals(self):
        resids = self.model.pca_res.residuals()
        print(resids)


    def show_pred_x_cal(self):
        cal_pred_x = self.model.pca_res.calPredX()
        print(cal_pred_x)


    def show_pred_x_val(self):
        val_pred_x = self.model.pca_res.valPredX()
        print(val_pred_x)


    def show_msee_tot(self):
        print("MSEE total")
        msee = self.model.pca_res.MSEE()
        tv = TableViewController(title="MSEE total")
        tv.set_col_names([str(i) for i in range(msee.shape[0])])
        tv.add_row(msee, 'MSEE')
        tv.edit_traits()


    def show_msee_ind(self):
        print("MSEE for each variable")
        ind_var_msee = self.model.pca_res.MSEE_indVar()
        tv = TableViewController(title="MSEE individual variables")
        tv.set_col_names([str(i) for i in range(ind_var_msee.shape[1])])
        for i in range(ind_var_msee.shape[0]):
            tv.add_row(ind_var_msee[i,:], 'MSEE')
        tv.edit_traits()


    def show_msecv_tot(self):
        print("MSECV total")
        msecv = self.model.pca_res.MSECV()
        tv = TableViewController(title="MSECV total")
        tv.set_col_names([str(i) for i in range(msecv.shape[0])])
        tv.add_row(msecv, 'MSECV')
        tv.edit_traits()


    def show_msecv_ind(self):
        print("MSECV for each variable")
        ind_var_msecv = self.model.pca_res.MSECV_indVar()
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
                # plot_window.edit_traits(parent=self.model.mother_ref.win_handle, kind='live')
                plot_window.edit_traits(kind='live')
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
        ds_name = self.model.ds.display_name
        dstype = self.model.plot_type
        return "{0} | PCA - {1} - ConsumerCheck".format(ds_name, dstype)



no_view = _traitsui.View()


pca_view = _traitsui.View(
    _traitsui.Item('controller.name', style='readonly'),
    # _traitsui.Label('Standardise:'),
    _traitsui.Item('standardise', style='custom', show_label=True),
    _traitsui.Item('calc_n_pc',
                   editor=_traitsui.RangeEditor(low_name='min_pc', high_name='max_pc', mode='auto'),
                   style='simple',
                   label='PC to calc:'),
    )


pca_nodes = [
    _traitsui.TreeNode(
        node_for=[PcaController],
        label='name',
        children='',
        view=pca_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[PcaController],
        label='=Base plots',
        children='window_launchers',
        view=pca_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[WindowLauncher],
        label='node_name',
        view=no_view,
        menu=[],
        on_dclick=dclk_activator)
    ]


pca_tree = _traitsui.TreeEditor(
    nodes=pca_nodes,
    )


class PcaPluginController(_traitsui.Controller):
    available_ds = _traits.List()
    selected_ds = _traits.List()

    update_tree = _traits.Event()
    selected_object = _traits.Any()
    edit_node = _traits.Instance(PcaController)


    @_traits.on_trait_change('selected_object')
    def _tree_selection_made(self, obj, name, new):
        if isinstance(new, PcaController):
            self.edit_node = new
        elif isinstance(new, WindowLauncher):
            self.edit_node = new.owner_ref
        else:
            self.edit_node = None


    # FIXME: I dont know why the initial populating is not handled by
    # _update_selection_list()
    def _available_ds_default(self):
        return self._get_selectable()


    @_traits.on_trait_change('model:dsc:[dsl_changed,ds_changed]', post_init=False)
    def _update_selection_list(self, obj, name, new):
        self.available_ds = self._get_selectable()


    def _get_selectable(self):
        return self.model.dsc.get_id_name_map()


    @_traits.on_trait_change('selected_ds')
    def _selection_made(self, obj, name, old_value, new_value):
        last = set(old_value)
        new = set(new_value)
        removed = last.difference(new)
        added = new.difference(last)
        if removed:
            self.model.remove(list(removed)[0])
        elif added:
            self._make_task(list(added)[0])

        self.update_tree = True


    def _make_task(self, ds_id):
        tsk = self.model.make_model(ds_id)
        task = PcaController(tsk)
        self.model.add(task)


plugin_nodes=[
    _traitsui.TreeNode(
        node_for=[PcaPlugin],
        label='=Pca',
        children='',
        auto_open=True,
        menu=[],
        ),
    _traitsui.TreeNode(
        node_for=[PcaPlugin],
        label='=Pca',
        children='tasks',
        auto_open=True,
        menu=[],
        ),
    ]


pca_plugin_tree = _traitsui.TreeEditor(
    nodes=plugin_nodes+pca_nodes,
    # refresh='controller.update_tree',
    selected='controller.selected_object',
    editable=False,
    hide_root=True,
    )


pca_plugin_view = _traitsui.View(
    _traitsui.Group(
        _traitsui.Item('controller.model', editor=pca_plugin_tree, show_label=False),
        _traitsui.Group(
            _traitsui.Group(
                _traitsui.Item('controller.selected_ds',
                               editor=_traitsui.CheckListEditor(name='controller.available_ds'),
                               style='custom',
                               show_label=False,
                               width=200,
                               height=200,
                               ),
                label='Select dataset',
                show_border=True,
                ),
            _traitsui.Group(
                _traitsui.Item('controller.edit_node',
                               editor=_traitsui.InstanceEditor(view=pca_view),
                               style='custom',
                               show_label=False),
                show_border=True,
                ),
            orientation='vertical',
            ),
        _traitsui.Spring(width=230),
        orientation='horizontal',
        ),
    resizable=True,
    buttons=['OK'],
    )


class TestOnePcaTree(_traits.HasTraits):
    one_pca = _traits.Instance(PcaController)

    traits_view = _traitsui.View(
        _traitsui.Item('one_pca', editor=pca_tree, show_label=False),
        resizable=True,
        buttons=['OK'],
        )


if __name__ == '__main__':
    print("PCA GUI test start")
    from tests.conftest import simple_ds, synth_dsc
    one_branch=False

    if one_branch:
        ds = simple_ds()
        pca = Pca(ds=ds)
        pc = PcaController(pca)
        test = TestOnePcaTree(one_pca=pc)
        test.configure_traits()
    else:
        dsc = synth_dsc()
        pcap = PcaPlugin(dsc=dsc)
        ppc = PcaPluginController(pcap)
        ppc.configure_traits(view=pca_plugin_view)
