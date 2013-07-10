
# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui

# Local imports
from dataset import DataSet
from prefmap_model import Prefmap, InComputeable
from plot_ev_line import EVLinePlot
from plot_pc_scatter import PCScatterPlot
# from combination_table import CombinationTable
from prefmap_picker import PrefmapPicker
from dataset_container import DatasetContainer
from plot_windows import MultiPlotWindow
from window_helper import multiplot_factory
from plugin_tree_helper import (WindowLauncher, dclk_activator, overview_activator)
from plugin_base import (ModelController, CalcContainer, PluginController,
                         dummy_view, TestOneNode, make_plugin_view)


class ErrorMessage(_traits.HasTraits):
    err_msg = _traits.Str()
    traits_view = _traitsui.View(_traitsui.Item('err_msg', style='readonly',
                            label='Zero variance variables'),
                       buttons=[_traitsui.OKButton], title='Warning')


class PrefmapController(ModelController):

    window_launchers = _traits.List(_traits.Instance(WindowLauncher))


    def _name_default(self):
        return "{0} - {1}".format(
            self.model.ds_C.display_name, self.model.ds_S.display_name)


    def _window_launchers_default(self):
        return self._populate_window_launchers()


    def _populate_window_launchers(self):

        std_launchers = [
            # ("Overview", plot_overview),
            ("Scores", scores_plot),
            ("X ~ Y correlation loadings", corr_loadings_plot),
            ("X loadings", loadings_x_plot),
            ("Y loadings", loadings_y_plot),
            ("Explained var X", expl_var_x_plot),
            ("Explained var Y", expl_var_y_plot),
            ]

        return [WindowLauncher(node_name=nn, view_creator=fn,
                               owner_ref=self,
                               loop_name='window_launchers',
                               )
                for nn, fn in std_launchers]


    def _show_zero_var_warning(self):
        dlg = ErrorMessage()
        dlg.err_msg = ', '.join(self.model.C_zero_std+self.model.S_zero_std)
        dlg.edit_traits(parent=self.win_handle, kind='modal')


    def get_result(self):
        try:
            res = self.model.res
        except InComputeable:
            self._show_zero_var_warning()
            if self.model.C_zero_std:
                df = self.model.ds_C.mat.drop(self.model.C_zero_std, axis=1)
                olds = self.model.ds_C
                self.model.ds_C = DataSet(mat=df,
                                          display_name=olds.display_name,
                                          kind=olds.kind)
            if self.model.S_zero_std:
                df = self.model.ds_S.mat.drop(self.model.S_zero_std, axis=1)
                olds = self.model.ds_S
                self.model.ds_S = DataSet(mat=df,
                                          display_name=olds.display_name,
                                          kind=olds.kind)
            res = self.model.res

        return res


    def open_overview(self):
        """Make Prefmap overview plot.

        Plot an array of plots where we plot:
         * scores
         * loadings
         * corr. load
         * expl. var
        for each of the datasets.
        """
        res = self.get_result()
        wl = self.window_launchers
        title = self._wind_title(res)

        mpw = MultiPlotWindow(title_text=title)

        sp = multiplot_factory(scores_plot, res, wl, title, mpw)
        clp = multiplot_factory(corr_loadings_plot, res, wl, title, mpw)
        evc = multiplot_factory(expl_var_x_plot, res, wl, title, mpw)
        evs = multiplot_factory(expl_var_y_plot, res, wl, title, mpw)

        ds_plots = [
            [sp, clp],
            [evc, evs]
            ]

        mpw.plots.component_grid = ds_plots
        mpw.plots.shape = (2, 2)
        self._show_plot_window(mpw)


    def _wind_title(self, res):
        dsx_name = self.model.ds_C.display_name
        dsy_name = self.model.ds_S.display_name
        mn = res.method_name
        return "({0}) X ~ Y ({1}) | {2} - ConsumerCheck".format(dsx_name, dsy_name, mn)


# Plot creators
def scores_plot(res):
    plot = PCScatterPlot(res.scores_x, res.expl_var_x, title='Scores')
    return plot


def loadings_x_plot(res):
    plot = PCScatterPlot(res.loadings_x, res.expl_var_x, title='Loadings X')
    return plot


def loadings_y_plot(res):
    plot = PCScatterPlot(res.loadings_y, res.expl_var_y, title='Loadings Y')
    return plot


def corr_loadings_plot(res):
    plot = PCScatterPlot(title='Correlation loadings')
    clx = res.corr_loadings_x
    clx.style.fg_color = 'blue'
    cly = res.corr_loadings_y
    cly.style.fg_color = 'red'
    plot.add_PC_set(clx, res.expl_var_x)
    plot.add_PC_set(cly, res.expl_var_y)
    plot.plot_circle(True)
    return plot


def expl_var_x_plot(res):
    plot = EVLinePlot(res.expl_var_x, title='Explained variance X')
    return plot


def expl_var_y_plot(res):
    plot = EVLinePlot(res.expl_var_y, title='Explained variance Y')
    return plot


no_view = _traitsui.View()


prefmap_view = _traitsui.View(
    # _traitsui.Item('controller.name', style='readonly'),
    _traitsui.Item('int_ext_mapping', style='custom', label='Mapping'),
    _traitsui.Item('prefmap_method', style='custom', label='Method'),
    _traitsui.Item('standardise_x', label='Standardise X',
                   style='custom', show_label=True),
    _traitsui.Item('standardise_y', label='Standardise Y',
                   style='custom', show_label=True),
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
        label='=Overview',
        children='window_launchers',
        view=prefmap_view,
        menu=[],
        on_dclick=overview_activator),
    _traitsui.TreeNode(
        node_for=[WindowLauncher],
        label='node_name',
        view=no_view,
        menu=[],
        on_dclick=dclk_activator)
    ]



class PrefmapPluginController(PluginController):

    comb = _traits.Instance(PrefmapPicker, PrefmapPicker())
    last_selection = _traits.Set()

    dummy_model_controller = _traits.Instance(PrefmapController, PrefmapController(Prefmap()))

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
        # self.comb._generate_combinations()


    @_traits.on_trait_change('comb:combination_updated', post_init=True)
    def _handle_selection(self, obj, name, old, new):
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
                   width=250,
                   height=150,
                   ),
    label='Select dataset',
    show_border=True,
    )


prefmap_plugin_view =  make_plugin_view(
    'Prefmap', prefmap_nodes, selection_view, prefmap_view)


if __name__ == '__main__':
    print("Prefmap GUI test start")
    from tests.conftest import imp_ds
    one_branch = False

    # Folder, File name, Display name, DS type
    ds_C_meta = ('Cheese', 'ConsumerLike_mod.txt',
                 'Cheese liking', 'Consumer liking')
    ds_S_meta = ('Cheese', 'SensoryData_mod.txt',
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
            view=prefmap_plugin_view)
