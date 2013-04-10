
# Scipy imports
import numpy as _np
import pandas as _pd

# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui

# Local imports
from dataset import DataSet
from pca_model import Pca, InComputeable
from ui_results import TableViewController
from plot_ev_line import EVLinePlot
from plot_pc_scatter import PCScatterPlot
from plot_windows import SinglePlotWindow, LinePlotWindow, MultiPlotWindow
from plugin_tree_helper import (WindowLauncher, dclk_activator, ModelController,
                                CalcContainer, PluginController, dummy_view,
                                TestOneNode, make_plugin_view)



class ErrorMessage(_traits.HasTraits):
    err_msg = _traits.Str()
    traits_view = _traitsui.View(_traitsui.Item('err_msg', style='readonly',
                            label='Zero variance variables'),
                       buttons=[_traitsui.OKButton], title='Warning')



class PcaController(ModelController):
    '''Controller for one PCA object'''
    window_launchers = _traits.List(_traits.Instance(WindowLauncher))

    def _name_default(self):
        return self.model.ds.display_name


    def _window_launchers_default(self):
        return self._populate_window_launchers()


    def _populate_window_launchers(self):
        adv_enable = False

        std_launchers = [
            # ("Overview", "plot_overview"),
            ("Scores", scores_plot),
            ("Loadings", loadings_plot),
            ("Correlation loadings", corr_load_plot),
            ("Explained variance", expl_var_plot),
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
        return [WindowLauncher(node_name=nn, view_creator=fn, owner_ref=self) for nn, fn in std_launchers]


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


    def open_window(self, view):
        win = SinglePlotWindow(
            plot=view,
            res=self.model.res,
            view_loop=self.window_launchers,
            title_text=self._wind_title(),
            vistog=False
            )
        self._show_plot_window(win)



    def plot_scores(self):
        # FIXME: Test plot navigation
        self.model.plot_type = 'Scores Plot'
        try:
            s_plot = self._make_scores_plot()
        except InComputeable:
            self._show_zero_var_warning()
            return

        spw = SinglePlotWindow(
            plot=s_plot,
            res=self.model.res,
            title_text=self._wind_title(),
            vistog=False
            )
        spw.plot_navigator.view_loop = vl
        self._show_plot_window(spw)


    def _make_scores_plot(self, is_subplot=False):
        res = self.model.res
        plot = PCScatterPlot(res.scores, res.expl_var)
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
        res = self.model.res
        plot = PCScatterPlot(res.loadings, res.expl_var)
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
        res = self.model.res
        pcl = PCScatterPlot(res.corr_loadings, res.expl_var)
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
        res = self.model.res
        pl = EVLinePlot(res.expl_var)
        if is_subplot:
            pl.add_left_down_action(self.plot_expl_var)
        return pl


    def show_residuals(self):
        resids = self.model.res.residuals()
        print(resids)


    def show_pred_x_cal(self):
        cal_pred_x = self.model.res.calPredX()
        print(cal_pred_x)


    def show_pred_x_val(self):
        val_pred_x = self.model.res.valPredX()
        print(val_pred_x)


    def show_msee_tot(self):
        print("MSEE total")
        msee = self.model.res.MSEE()
        tv = TableViewController(title="MSEE total")
        tv.set_col_names([str(i) for i in range(msee.shape[0])])
        tv.add_row(msee, 'MSEE')
        tv.edit_traits()


    def show_msee_ind(self):
        print("MSEE for each variable")
        ind_var_msee = self.model.res.MSEE_indVar()
        tv = TableViewController(title="MSEE individual variables")
        tv.set_col_names([str(i) for i in range(ind_var_msee.shape[1])])
        for i in range(ind_var_msee.shape[0]):
            tv.add_row(ind_var_msee[i,:], 'MSEE')
        tv.edit_traits()


    def show_msecv_tot(self):
        print("MSECV total")
        msecv = self.model.res.MSECV()
        tv = TableViewController(title="MSECV total")
        tv.set_col_names([str(i) for i in range(msecv.shape[0])])
        tv.add_row(msecv, 'MSECV')
        tv.edit_traits()


    def show_msecv_ind(self):
        print("MSECV for each variable")
        ind_var_msecv = self.model.res.MSECV_indVar()
        tv = TableViewController(title="MSECV individual variables")
        tv.set_col_names([str(i) for i in range(ind_var_msecv.shape[1])])
        for i in range(ind_var_msecv.shape[0]):
            tv.add_row(ind_var_msecv[i,:], 'MSECV')
        tv.edit_traits()


    def _wind_title(self):
        ds_name = self.model.ds.display_name
        # dstype = self.model.plot_type
        dstype = "FIXME plot type"
        return "{0} | PCA - {1} - ConsumerCheck".format(ds_name, dstype)


# Plots creators

def scores_plot(res):
    plot = PCScatterPlot(res.scores, res.expl_var)
    return plot


def loadings_plot(res):
    plot = PCScatterPlot(res.loadings, res.expl_var)
    return plot


def corr_load_plot(res):
    plot = PCScatterPlot(res.corr_loadings, res.expl_var)
    plot.plot_circle(True)
    return plot


def expl_var_plot(res):
    plot = EVLinePlot(res.expl_var)
    return plot



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


class PcaPluginController(PluginController):
    available_ds = _traits.List()
    selected_ds = _traits.List()

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
            self._make_calculation(list(added)[0])

        self.update_tree = True


    def _make_calculation(self, ds_id):
        calc_model = Pca(id=ds_id, ds=self.model.dsc[ds_id])
        calculation = PcaController(calc_model)
        self.model.add(calculation)



selection_view = _traitsui.Group(
    _traitsui.Item('controller.selected_ds',
                   editor=_traitsui.CheckListEditor(name='controller.available_ds'),
                   style='custom',
                   show_label=False,
                   width=200,
                   height=200,
                   ),
    label='Select dataset',
    show_border=True,
    )


pca_plugin_view = make_plugin_view('Pca', pca_nodes, selection_view, pca_view)



if __name__ == '__main__':
    print("PCA GUI test start")
    from tests.conftest import iris_ds, synth_dsc
    one_branch = True

    if one_branch:
        iris = iris_ds()
        pca = Pca(ds=iris)
        pc = PcaController(pca)
        test = TestOneNode(one_model=pc)
        test.configure_traits(view=dummy_view(pca_nodes))
    else:
        pcap = CalcContainer(dsc=synth_dsc())
        ppc = PcaPluginController(pcap)
        ppc.configure_traits(view=pca_plugin_view)
