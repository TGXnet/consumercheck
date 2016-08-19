'''ConsumerCheck
'''
#-----------------------------------------------------------------------------
#  Copyright (C) 2014 Thomas Graff <thomas.graff@tgxnet.no>
#
#  This file is part of ConsumerCheck.
#
#  ConsumerCheck is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  ConsumerCheck is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ConsumerCheck.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------

# SciPy libs import
import pandas as _pd

# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui

# Local imports
from dataset import DataSet
from prefmap_model import Prefmap, InComputeable
from plot_ev_line import EVLinePlot
from plot_pc_scatter import (PCScatterPlot,
                             ScatterSectorPlot, PCSectorPlotControl,
                             CLSectorPlot, CLSectorPlotControl)
from dialogs import ErrorMessage
# from combination_table import CombinationTable
from prefmap_picker import PrefmapPicker
from dataset_container import DatasetContainer
from plot_windows import OverviewPlotWindow, SinglePlotWindow
from window_helper import multiplot_factory
from plugin_tree_helper import (WindowLauncher, dclk_activator, overview_activator)
from plugin_base import (ModelController, CalcContainer, PluginController,
                         dummy_view, TestOneNode, make_plugin_view)


class PrefmapController(ModelController):

    window_launchers = _traits.List(_traits.Instance(WindowLauncher))
    pred_y_cal_launch = _traits.List(_traits.Instance(WindowLauncher))
    pred_y_val_launch = _traits.List(_traits.Instance(WindowLauncher))


    def _name_default(self):
        return "{0} - {1}".format(
            self.model.ds_C.display_name, self.model.ds_S.display_name)


    def _window_launchers_default(self):
        return self._populate_window_launchers()


    def _populate_window_launchers(self):

        std_launchers = [
            # ("Overview", plot_overview),
            ("X Scores", scores_plot),
            ("X&Y correlation loadings", corr_loadings_plot),
            ("X loadings", loadings_x_plot),
            ("Y loadings", loadings_y_plot),
            ("Explained var in X", expl_var_x_plot),
            ("Explained var in Y", expl_var_y_plot),
            ]

        return [WindowLauncher(node_name=nn, view_creator=fn,
                               owner_ref=self,
                               loop_name='window_launchers',
                               )
                for nn, fn in std_launchers]


    def _pred_y_cal_launch_default(self):
        res = self.get_result()
        pyc = res.pred_cal_y

        return [WindowLauncher(node_name="After PC{}".format(i),
                               view_creator=pred_y_cal_table,
                               func_parms=tuple([i]),
                               owner_ref=self,
                               loop_name='pred_y_cal_launch',
                               )
                for i, v in enumerate(pyc, 1)]


    def _pred_y_val_launch_default(self):
        res = self.get_result()
        pyv = res.pred_val_y

        return [WindowLauncher(node_name="After PC{}".format(i),
                               view_creator=pred_y_val_table,
                               func_parms=tuple([i]),
                               owner_ref=self,
                               loop_name='pred_y_val_launch',
                               )
                for i, v in enumerate(pyv, 1)]


    def _show_zero_var_warning(self):
        dlg = ErrorMessage()
        dlg.err_msg = 'Removed zero variance variables'
        dlg.err_val = ', '.join(self.model.C_zero_std+self.model.S_zero_std)
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
        for each of the data sets.
        """
        res = self.get_result()
        wl = self.window_launchers
        title = self._wind_title(res)

        mpw = OverviewPlotWindow(title_text=title)

        sp = multiplot_factory(scores_plot, res, wl, title, mpw)
        clp = multiplot_factory(corr_loadings_plot, res, wl, title, mpw)
        evc = multiplot_factory(expl_var_x_plot, res, wl, title, mpw)
        evs = multiplot_factory(expl_var_y_plot, res, wl, title, mpw)

        ds_plots = [
            [sp, clp],
            [evc, evs]]

        mpw.plots.component_grid = ds_plots
        mpw.plots.shape = (2, 2)
        self._show_plot_window(mpw)

    def open_window(self, viewable, view_loop):
        """Expected viewable is by now:
          + Plot subtype
          + DataSet type
        """
        res = self.get_result()
        if isinstance(viewable, CLSectorPlot):
            plot_control = CLSectorPlotControl(viewable)
            win = SinglePlotWindow(
                plot=plot_control,
                res=res,
                view_loop=view_loop)
            self._show_plot_window(win)
        elif isinstance(viewable, ScatterSectorPlot):
            plot_control = PCSectorPlotControl(viewable)
            win = SinglePlotWindow(
                plot=plot_control,
                res=res,
                view_loop=view_loop)
            self._show_plot_window(win)
        else:
            super(PrefmapController, self).open_window(viewable, view_loop)


def pred_y_cal_table(res, pcid):
    ds = res.pred_cal_y[pcid-1]
    return ds


def pred_y_val_table(res, pcid):
    ds = res.pred_val_y[pcid-1]
    return ds


# Plot creators
def scores_plot(res):
    plot = PCScatterPlot(res.scores_x, res.expl_var_x, res.expl_var_y, title='X scores')
    return plot


def loadings_x_plot(res):
    if res.external_mapping:
        plot = PCScatterPlot(res.loadings_x, res.expl_var_x, title='X loadings')
    else:
        plot = ScatterSectorPlot(res.loadings_x, res.expl_var_x, title='X loadings')
    return plot


def loadings_y_plot(res):
    if res.external_mapping:
        plot = ScatterSectorPlot(res.loadings_y, res.expl_var_y, title='Y loadings')
    else:
        plot = PCScatterPlot(res.loadings_y, res.expl_var_y, title='Y loadings')
    return plot


def corr_loadings_plot(res):
    # plot = PCScatterPlot(title='Correlation loadings')
    clx = res.corr_loadings_x
    # clx.style.fg_color = 'blue'
    cly = res.corr_loadings_y
    # cly.style.fg_color = 'red'
    # plot.add_PC_set(clx, res.expl_var_x)
    # plot.add_PC_set(cly, res.expl_var_y)
    # plot.plot_circle(True)
    plot = CLSectorPlot(clx, res.expl_var_x,
                        cly, res.expl_var_y,
                        res.external_mapping,
                        title='X&Y correlation loadings')
    return plot


def expl_var_x_plot(res):
    plot = EVLinePlot(res.expl_var_x, title='Explained variance in X')
    return plot


def expl_var_y_plot(res):
    plot = EVLinePlot(res.expl_var_y, title='Explained variance in Y')
    return plot


no_view = _traitsui.View()


prefmap_view = _traitsui.View(
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
    title='Prefmap settings',
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
        label='=Overview plot',
        icon_path='graphics',
        icon_group='overview.ico',
        icon_open='overview.ico',
        children='window_launchers',
        view=prefmap_view,
        menu=[],
        on_dclick=overview_activator),
    _traitsui.TreeNode(
        node_for=[PrefmapController],
        label='=Y predicted (calibration)',
        icon_path='graphics',
        icon_group='overview.ico',
        icon_open='overview.ico',
        children='pred_y_cal_launch',
        view=prefmap_view,
        menu=[],
        # on_dclick=overview_activator,
    ),
    _traitsui.TreeNode(
        node_for=[PrefmapController],
        label='=Y predicted (validation)',
        icon_path='graphics',
        icon_group='overview.ico',
        icon_open='overview.ico',
        children='pred_y_val_launch',
        view=prefmap_view,
        menu=[],
        # on_dclick=overview_activator,
    ),
    _traitsui.TreeNode(
        node_for=[WindowLauncher],
        label='node_name',
        view=no_view,
        menu=[],
        on_dclick=dclk_activator)
    ]


class PrefmapCalcContainer(CalcContainer):
    calculator = _traits.Instance(Prefmap, Prefmap())



class PrefmapPluginController(PluginController):

    comb = _traits.Instance(PrefmapPicker, PrefmapPicker())
    last_selection = _traits.Set()

    dummy_model_controller = _traits.Instance(PrefmapController, PrefmapController(Prefmap()))

    def init(self, info):
        super(PrefmapPluginController, self).init(info)
        self._update_comb()


    @_traits.on_trait_change('model:dsc:[dsl_changed,ds_changed]',
                             post_init=False)
    def _update_selection_list(self, obj, name, new):
        self._update_comb()


    def _update_comb(self):
        dsc = self.model.dsc
        self.comb.col_set = [('', '')] + dsc.get_id_name_map('Descriptive analysis / sensory profiling')
        self.comb.row_set = [('', '')] + dsc.get_id_name_map('Consumer liking')
        # self.comb._generate_combinations()


    @_traits.on_trait_change('comb:combination_updated', post_init=True)
    def _handle_selection(self, obj, name, old, new):
        self.model.calculations = []
        selection = self.comb.get_selected_combinations()[0]
        self._make_calculation(selection[0], selection[1])


    def _make_calculation(self, id_c, id_s):
        ds_c = self.model.dsc[id_c]
        ds_s = self.model.dsc[id_s]

        # Check missing data
        if ds_c.missing_data or ds_s.missing_data:
            self._show_missing_warning()
            return

        # Check data set alignment
        ns_c = ds_c.n_objs
        ns_s = ds_s.n_objs
        if ns_c != ns_s:
            self._show_alignment_warning(ds_c, ds_s)
            return

        calc_model = Prefmap(id=id_c+id_s,
                             ds_C=ds_c,
                             ds_S=ds_s,
                             settings=self.model.calculator)
        calculation = PrefmapController(calc_model, win_handle=self.win_handle)
        self.model.add(calculation)


    def _show_missing_warning(self):
        dlg = ErrorMessage()
        dlg.err_msg = 'This matrix has missing values'
        dlg.err_val = ("At the current version of ConsumerCheck Prefmap does not handle missing values. There are three options to work around this problem:\n"
                       "  1. Impute the missing values with the imputation method of your choice outside ConsumerCheck and re-import the data\n"
                       "  2. Remove the column with the missing values and re-import the data\n"
                       "  3. Remove the row with the missing values and re-import the data")
        dlg.edit_traits(parent=self.win_handle, kind='modal')


    def _show_alignment_warning(self, ds_c, ds_s):
        dlg = ErrorMessage()
        dlg.err_msg = 'Consumer liking and sensory profiling data does not align'
        dlg.err_val = 'The Consumer liking data and descriptive analysis/sensory profiling data do not align. There are {0} rows in {1} and {2} rows in the {3}. Please select other data.'.format(ds_c.n_objs, ds_c.display_name, ds_s.n_objs, ds_s.display_name)
        dlg.edit_traits(parent=self.win_handle, kind='modal')



selection_view = _traitsui.Group(
    _traitsui.Item('controller.comb',
                   editor=_traitsui.InstanceEditor(),
                   style='custom',
                   show_label=False,
                   width=250,
                   height=150,
                   ),
    label='Select data set',
    show_border=True,
    )


prefmap_plugin_view =  make_plugin_view(
    'Prefmap', prefmap_nodes, selection_view, prefmap_view)


if __name__ == '__main__':
    print("Prefmap GUI test start")
    from tests.conftest import imp_ds
    one_branch = False

    # Folder, File name, Display name, DS type
    ds_C_meta = ('Cheese', 'ConsumerLiking.txt',
                 'Cheese liking', 'Consumer liking')
    ds_S_meta = ('Cheese', 'SensoryData.txt',
                 'Cheese profiling', 'Descriptive analysis / sensory profiling')
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
        prefmap = PrefmapCalcContainer(dsc=dsc)
        ppc = PrefmapPluginController(prefmap)
        ppc.configure_traits(
            view=prefmap_plugin_view)
