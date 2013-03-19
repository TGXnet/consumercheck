
# Scipy lib imports
import numpy as _np
import pandas as _pd

# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui

# Local imports
from dataset import DataSet
from prefmap_model import Prefmap
from plot_ev_line import EVLinePlot
from plot_pc_scatter import PCScatterPlot
from combination_table import CombinationTable
from dataset_container import DatasetContainer
from plot_windows import SinglePlotWindow, LinePlotWindow, MultiPlotWindow
from plugin_tree_helper import (WindowLauncher, dclk_activator, ModelController,
                                CalcContainer, PluginController, dummy_view,
                                TestOneNode, make_plugin_view)



class PrefmapController(ModelController):

    window_launchers = _traits.List(_traits.Instance(WindowLauncher))


    def _name_default(self):
        return "{0} - {1}".format(
            self.model.ds_C.display_name, self.model.ds_S.display_name)


    def _window_launchers_default(self):
        return self._populate_window_launchers()


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

        return [WindowLauncher(node_name=nn, func_name=fn, owner_ref=self)
                for nn, fn in std_launchers]


    def plot_overview(self):
        """Make Prefmap overview plot.

        Plot an array of plots where we plot:
         * scores
         * loadings
         * corr. load
         * expl. var
        for each of the datasets.
        """
        self.model.plot_type = 'Overview Plot'
        ds_plots = [
            [self._make_scores_plot(True), self._make_corr_load_plot(True)],
            [self._make_expl_var_plot_c(True), self._make_expl_var_plot_s(True)]
            ]

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
        res = self.model.res
        pc_tab = res.X_scores()
        labels = self.model.ds_C.obj_n
        expl_vars_x = res.X_calExplVar()

        # Make table view dataset
        pc_df = _pd.DataFrame(
            pc_tab,
            index=labels,
            columns=["PC-{0}".format(i+1) for i in range(pc_tab.shape[1])])
        score_ds = DataSet(
            mat=pc_df,
            display_name=self.model.ds_C.display_name)

        plot = PCScatterPlot(pc_tab, labels, expl_vars=expl_vars_x,
                             view_data=score_ds, title="Scores", id="scores")
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
        res = self.model.res
        xLP = res.X_loadings()
        expl_vars = res.X_calExplVar()

        # Make table view dataset
        pc_df = _pd.DataFrame(xLP)

        if self.model.mother_ref.radio == 'Internal mapping':
            labels = self.model.ds_C.var_n
            display_name = self.model.ds_C.display_name
        else:
            labels = self.model.ds_S.var_n
            display_name = self.model.ds_S.display_name

        pc_df.index = labels
        pc_df.columns = ["PC-{0}".format(i+1) for i in range(xLP.shape[1])]
        loadings_ds = DataSet(
            values=pc_df,
            display_name=display_name)

        plot = PCScatterPlot(xLP, labels, expl_vars=expl_vars,
                             view_data=loadings_ds, title="X Loadings",
                             id="loadings_x")
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
        res = self.model.res
        yLP = res.Y_loadings()
        expl_vars = res.Y_calExplVar()
        # labels = self.model.ds_S.var_n

        # Make table view dataset
        col_names = ["PC-{0}".format(i+1) for i in range(yLP.shape[1])]

        if self.model.mother_ref.radio == 'Internal mapping':
            labels = self.model.ds_S.var_n
            display_name = self.model.ds_S.display_name
        else:
            labels = self.model.ds_C.var_n
            display_name = self.model.ds_C.display_name

        pc_df = _pd.DataFrame(
            yLP,
            index=labels,
            columns=col_names)
        loadings_ds = DataSet(
            mat=pc_df,
            display_name=display_name)

        plot = PCScatterPlot(yLP, labels, expl_vars=expl_vars,
                             view_data=loadings_ds, title="Y Loadings",
                             id="loadings_y")
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
        res = self.model.res
        clx = res.X_corrLoadings()
        cly = res.Y_corrLoadings()
        # calExplVarX
        cevx = res.X_calExplVar()
        cevy = res.Y_calExplVar()
        if self.model.mother_ref.radio == 'Internal mapping':
            vnx = self.model.ds_C.var_n
            vny = self.model.ds_S.var_n
        else:
            vnx = self.model.ds_S.var_n
            vny = self.model.ds_C.var_n
        pcl = PCScatterPlot(clx, vnx, 'darkviolet', cevx,
                            title="X & Y correlation loadings",
                            id="corr_loading")
        pcl.add_PC_set(cly, vny, 'darkgoldenrod', cevy)
        if is_subplot:
            pcl.add_left_down_action(self.plot_corr_loading)
        pcl.plot_circle(True)
        return pcl


    def plot_expl_var_x(self):
        self.model.plot_type = 'Explained Variance X Plot'
        ev_plot = self._make_expl_var_plot_c()
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


    def _make_expl_var_plot_c(self, is_subplot=False):
        res = self.model.res
        sumCalX = res.X_cumCalExplVar()
        sumValX = res.X_cumValExplVar()

        # Make table view dataset
        pc_tab = _np.array([sumCalX, sumValX]).T
        pc_df = _pd.DataFrame(
            pc_tab,
            index=["PC-{0}".format(i) for i in range(pc_tab.shape[0])],
            columns=["calibrated", "validated"])
        ev_ds = DataSet(
            mat=pc_df,
            display_name=self.model.ds_C.display_name)

        pl = EVLinePlot(sumCalX, 'darkviolet', 'Calibrated X', view_data=ev_ds,
                        title = "Explained Variance X", id="expl_var_x")
        pl.add_EV_set(sumValX, 'darkgoldenrod', 'Validated X')
        if is_subplot:
            pl.add_left_down_action(self.plot_expl_var_x)
        return pl


    def plot_expl_var_y(self):
        self.model.plot_type = 'Explained Variance Y Plot'
        ev_plot = self._make_expl_var_plot_s()
        ev_plot.legend.visible = True
        spw = LinePlotWindow(
            plot=ev_plot,
            title_text=self._wind_title(),
            vistog=False
            )
        self._show_plot_window(spw)


    def _make_expl_var_plot_s(self, is_subplot=False):
        res = self.model.res
        sumCalY = res.Y_cumCalExplVar()
        sumValY = res.Y_cumValExplVar()

        # Make table view dataset
        pc_tab = _np.array([sumCalY, sumValY]).T
        pc_df = _pd.DataFrame(
            pc_tab,
            index=["PC-{0}".format(i) for i in range(pc_tab.shape[0])],
            columns=["calibrated", "validated"])
        ev_ds = DataSet(
            mat=pc_df,
            display_name=self.model.ds_S.display_name)

        pl = EVLinePlot(sumCalY, 'darkviolet', 'Calibrated Y', view_data=ev_ds,
                        title = "Explained Variance Y", id="expl_var_y")
        pl.add_EV_set(sumValY, 'darkgoldenrod', 'Validated Y')
        if is_subplot:
            pl.add_left_down_action(self.plot_expl_var_y)
        return pl


no_view = _traitsui.View()


prefmap_view = _traitsui.View(
    _traitsui.Item('controller.name', style='readonly'),
    _traitsui.Item('int_ext_mapping', style='custom', label='Mapping'),
    # _traitsui.Label('Standardise:'),
    _traitsui.Item('standardise', style='custom', show_label=True),
    _traitsui.Item('calc_n_pc',
                   editor=_traitsui.RangeEditor(
                       low_name='min_pc', high_name='max_pc', mode='auto'),
                   style='simple',
                   label='PC to calc:'),
    )


prefmap_nodes = [
    _traitsui.TreeNode(
        node_for=[PrefmapController],
        label='name',
        children='',
        view=prefmap_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[PrefmapController],
        label='=Base plots',
        children='window_launchers',
        view=prefmap_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[WindowLauncher],
        label='node_name',
        view=no_view,
        menu=[],
        on_dclick=dclk_activator)
    ]



class PrefmapPluginController(PluginController):

    comb = _traits.Instance(CombinationTable, CombinationTable())
    last_selection = _traits.Set()


    def init(self, info):
        self._update_comb()


    @_traits.on_trait_change('model:dsc:[dsl_changed,ds_changed]',
                             post_init=False)
    def _update_selection_list(self, obj, name, new):
        self._update_comb()


    def _update_comb(self):
        dsc = self.model.dsc
        self.comb.col_set = dsc.get_id_name_map('Sensory profiling')
        self.comb.row_set = dsc.get_id_name_map('Consumer liking')
        self.comb._generate_combinations()


    @_traits.on_trait_change('comb:combination_updated', post_init=True)
    def _handle_selection(self, obj, name, old, new):
        print("handle_selection")
        ## if not self.info:
        ##     return

        selection = set(self.comb.get_selected_combinations())
        if selection.difference(self.last_selection):
            added = selection.difference(self.last_selection)
            self.last_selection = selection
            added = list(added)[0]
            self._make_calculation(added[0], added[1])
        elif self.last_selection.difference(selection):
            removed = self.last_selection.difference(selection)
            removed = list(removed)[0]
            rem_id = '{0}{1}'.format(removed[0], removed[1])
            self.last_selection = selection
            self.model.remove(rem_id)


    def _make_calculation(self, id_c, id_s):
        calc_model = Prefmap(id=id_c+id_s,
                             ds_C=self.model.dsc[id_c],
                             ds_S=self.model.dsc[id_s])
        calculation = PrefmapController(calc_model)
        self.model.add(calculation)


selection_view = _traitsui.Group(
    _traitsui.Item('controller.comb',
                   editor=_traitsui.InstanceEditor(),
                   style='custom',
                   show_label=False,
                   width=100,
                   height=150,
                   ),
    label='Select dataset',
    show_border=True,
    )



if __name__ == '__main__':
    print("Prefmap GUI test start")
    from tests.conftest import imp_ds
    one_branch = False

    # Folder, File name, Display name, DS type
    ds_C_meta = ('Cheese', 'ConsumerLiking.txt',
                 'Cheese liking', 'Consumer liking')
    ds_S_meta = ('Cheese', 'SensoryData.txt',
                 'Cheese profiling', 'Sensory profiling')
    C = imp_ds(ds_C_meta)
    S = imp_ds(ds_S_meta)

    if one_branch:
        prefmap = Prefmap(ds_C=C, ds_S=S)
        pc = PrefmapController(prefmap)
        test = TestOneNode(one_model=pc)
        test.configure_traits(view=dummy_view(prefmap_nodes))
    else:
        dsc = DatasetContainer()
        dsc.add(C)
        dsc.add(S)
        prefmap = CalcContainer(dsc=dsc)
        ppc = PrefmapPluginController(prefmap)
        ppc.configure_traits(
            view=make_plugin_view('Prefmap', prefmap_nodes,
                                  selection_view, prefmap_view))
