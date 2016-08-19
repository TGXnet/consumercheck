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

# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui

# Local imports
from dataset import DataSet
from pca_model import Pca, InComputeable
from ui_results import TableViewController
from dialogs import ErrorMessage
from plot_ev_line import EVLinePlot
from plot_pc_scatter import PCScatterPlot
from plot_windows import OverviewPlotWindow
from window_helper import multiplot_factory
from plugin_tree_helper import (WindowLauncher, dclk_activator, overview_activator)
from plugin_base import (ModelController, CalcContainer, PluginController, CalcContainer,
                         dummy_view, TestOneNode, make_plugin_view)



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
        return [WindowLauncher(node_name=nn, view_creator=fn,
                               owner_ref=self,
                               loop_name='window_launchers',
                               )
                for nn, fn in std_launchers]


    def _show_zero_var_warning(self):
        dlg = ErrorMessage()
        dlg.err_msg = 'Removed zero variance variables'
        dlg.err_val = ', '.join(self.model.zero_variance)
        dlg.edit_traits(parent=self.win_handle, kind='modal')


    def get_result(self):
        try:
            res = self.model.res
        except InComputeable:
            self._show_zero_var_warning()
            df = self.model.ds.mat.drop(self.model.zero_variance, axis=1)
            olds = self.model.ds
            self.model.ds = DataSet(mat=df,
                                    display_name=olds.display_name,
                                    kind=olds.kind)
            res = self.model.res

        return res


    def open_overview(self):
        """Make PCA overview plot.

        Plot an array of plots where we plot scores, loadings, corr. load and expl. var
        for each of the data sets.
        """
        res = self.get_result()
 
        wl = self.window_launchers
        title = self._wind_title(res)

        mpw = OverviewPlotWindow(title_text=title)

        sp = multiplot_factory(scores_plot, res, wl, title, mpw)
        lp = multiplot_factory(loadings_plot, res, wl, title, mpw)
        clp = multiplot_factory(corr_load_plot, res, wl, title, mpw)
        evp = multiplot_factory(expl_var_plot, res, wl, title, mpw)

        ds_plots = [[sp, lp],
                    [clp, evp]]

        mpw.plots.component_grid = ds_plots
        mpw.plots.shape = (2, 2)
        self._show_plot_window(mpw)


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


# Plots creators

def scores_plot(res):
    plot = PCScatterPlot(res.scores, res.expl_var, title='Scores')
    return plot


def loadings_plot(res):
    plot = PCScatterPlot(res.loadings, res.expl_var, title='Loadings')
    return plot


def corr_load_plot(res):
    plot = PCScatterPlot(res.corr_loadings, res.expl_var, title='Correlation loadings')
    plot.plot_circle(True)
    return plot


def expl_var_plot(res):
    plot = EVLinePlot(res.expl_var, title='Explained variance')
    return plot



no_view = _traitsui.View()


pca_view = _traitsui.View(
    _traitsui.Item('standardise', style='custom', show_label=True),
    _traitsui.Item('calc_n_pc',
                   editor=_traitsui.RangeEditor(
                       low_name='min_pc',
                       high_name='max_pc',
                       mode='auto'),
                   style='simple',
                   label='PC to calc:'),
    title='PCA settings',
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
        label='=Overview plot',
        icon_path='graphics',
        icon_group='overview.ico',
        icon_open='overview.ico',
        children='window_launchers',
        view=pca_view,
        menu=[],
        on_dclick=overview_activator),
    _traitsui.TreeNode(
        node_for=[WindowLauncher],
        label='node_name',
        view=no_view,
        menu=[],
        on_dclick=dclk_activator)
    ]


class PcaCalcContainer(CalcContainer):
    calculator = _traits.Instance(Pca, Pca())



class PcaPluginController(PluginController):
    available_ds = _traits.List()
    selected_ds = _traits.List()

    dummy_model_controller = _traits.Instance(PcaController, PcaController(Pca()))


    # FIXME: I dont know why the initial populating is not handled by
    # _update_selection_list()
    def _available_ds_default(self):
        return self._get_selectable()


    @_traits.on_trait_change('model:dsc:[dsl_changed,ds_changed]', post_init=False)
    def _update_selection_list(self, obj, name, new):
        self.available_ds = self._get_selectable()


    def _get_selectable(self):
        return self.model.dsc.get_id_name_map(kind_exclude='Product design')


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
        pcads = self.model.dsc[ds_id]
        if pcads.missing_data:
            self._show_missing_warning()
            return
        calc_model = Pca(id=ds_id, ds=pcads, settings=self.model.calculator)
        calculation = PcaController(calc_model, win_handle=self.win_handle)
        self.model.add(calculation)


    def _show_missing_warning(self):
        dlg = ErrorMessage()
        dlg.err_msg = 'This matrix has missing values'
        dlg.err_val = ("At the current version of ConsumerCheck PCA does not handle missing values. There are three options to work around this problem:\n"
                       "  1. Impute the missing values with the imputation method of your choice outside ConsumerCheck and re-import the data\n"
                       "  2. Remove the column with the missing values and re-import the data\n"
                       "  3. Remove the row with the missing values and re-import the data")
        dlg.edit_traits(parent=self.win_handle, kind='modal')



selection_view = _traitsui.Group(
    _traitsui.Item('controller.selected_ds',
                   editor=_traitsui.CheckListEditor(name='controller.available_ds'),
                   style='custom',
                   show_label=False,
                   width=200,
                   height=200,
                   ),
    label='Select data set',
    show_border=True,
    )


pca_plugin_view = make_plugin_view('Pca', pca_nodes, selection_view, pca_view)



if __name__ == '__main__':
    print("PCA GUI test start")
    from tests.conftest import iris_ds, synth_dsc, zero_var_ds
    one_branch = False

    if one_branch:
        tds = zero_var_ds()
        pca = Pca(ds=tds)
        pc = PcaController(pca)
        test = TestOneNode(one_model=pc)
        test.configure_traits(view=dummy_view(pca_nodes))
    else:
        pcap = PcaCalcContainer(dsc=synth_dsc())
        ppc = PcaPluginController(pcap)
        ppc.configure_traits(view=pca_plugin_view)
