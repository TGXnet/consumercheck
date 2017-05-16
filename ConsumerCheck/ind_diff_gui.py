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
import dataset as ds
import ind_diff_model as idm
import plot_ev_line as pel
import plot_pc_scatter as pps
import dialogs as dlgs
import ind_diff_picker as idp
import dataset_container as dc
import plot_windows as pw
import plugin_tree_helper as pth
import plugin_base as pb
from plot_pc_scatter import PCScatterPlot, PCPlotControl
from plot_windows import SinglePlotWindow


class DiffWindowLauncher(pth.WindowLauncher):
    plot_func_name = _traits.Str()


class Element(_traits.HasTraits):
    name = _traits.Str()
    index = _traits.Str()
    calcc = _traits.WeakRef()
    plots_act = _traits.List(DiffWindowLauncher)

    def _plots_act_default(self):

        acts = [
            # ("Overview", plot_overview),
            ("X Scores", 'plsr_x_scores_plot'),
            # ("X&Y correlation loadings", corr_loadings_plot),
            ("X Loadings", 'plsr_x_loadings_plot'),
            # ("Y loadings", loadings_y_plot),
            # ("Explained var in X", expl_var_x_plot),
            # ("Explained var in Y", expl_var_y_plot),
        ]

        return [DiffWindowLauncher(
            node_name=nn,
            plot_func_name=fn,
            owner_ref=self,
            loop_name='plots_act',) for nn, fn in acts]


class Group(Element):
    member_index = _traits.List()



class IndDiffController(pb.ModelController):

    pca_x_launchers = _traits.List(Element)
    idx_pls_launchers = _traits.List(Element)
    groups_list = _traits.List(Element)
    gr_name_inc = _traits.Int(0)


    def _name_default(self):
        return "indDiff - {0}".format(
            self.model.ds_L.display_name)


    @_traits.on_trait_change('model.ds_A')
    def _populate_idx_pls(self):
        # FIXME: When to activate this
        print("Watch this")
        enum_pc = list(self.model.pcax.loadings.mat.columns)
        self.pca_x_launchers = [Element(name=name, index=name, calcc=self) for name in enum_pc]


    def add_group(self, members):
        self.gr_name_inc += 1
        el = Group(name="Group {0}".format(self.gr_name_inc), calcc=self, member_index=list(members))
        self.groups_list.append(el)


    def _show_zero_var_warning(self):
        dlg = dlgs.ErrorMessage()
        dlg.err_msg = 'Removed zero variance variables'
        dlg.err_val = ', '.join(self.model.C_zero_std+self.model.S_zero_std)
        dlg.edit_traits(parent=self.win_handle, kind='modal')


    def get_result(self):
        try:
            res = self.model.res
        except idm.InComputeable:
            self._show_zero_var_warning()
            if self.model.C_zero_std:
                df = self.model.ds_L.mat.drop(self.model.C_zero_std, axis=1)
                olds = self.model.ds_L
                self.model.ds_L = ds.DataSet(
                    mat=df,
                    display_name=olds.display_name,
                    kind=olds.kind)
            if self.model.S_zero_std:
                df = self.model.ds_A.mat.drop(self.model.S_zero_std, axis=1)
                olds = self.model.ds_A
                self.model.ds_A = ds.DataSet(
                    mat=df,
                    display_name=olds.display_name,
                    kind=olds.kind)
            res = self.model.res

        return res


    def pca_loadings_plot(self):
        """Make PCA loadings
        """
        res = self.model.pcax
        plot = self.pca_x_loadings_plot(res)
        # wl = self.window_launchers
        # title = self._wind_title(res)
        # self._show_plot_window(plot)
        # view_loop = self.pca_x_launchers

        plot_control = PCPlotControl(plot, created_me=self)

        win = SinglePlotWindow(
            plot=plot_control,
            res=res
        )
        self._show_plot_window(win)


    def pca_x_loadings_plot(self, res):
        plot = pps.SelectionScatterPlot(res.loadings, title='X loadings')
        return plot


    def plsr_x_scores_plot(self, res):
        # plot = pps.PCScatterPlot(res.scores_x, res.expl_var_x, res.expl_var_y, title='X scores')
        plot = pps.PCScatterPlot(res.scores_x, title='X scores')
        return plot


    def plsr_x_loadings_plot(self, res):
        plot = pps.PCScatterPlot(res.loadings_x, title='X loadings')
        return plot


    def plsr_x_expl_var_plot(res):
        plot = pel.EVLinePlot(res.expl_var_x, title='Explained variance in X')
        return plot


    def open_window(self, viewable, view_loop):
        """Expected viewable is by now:
          + Plot subtype
          + DataSet type
        """
        res = self.get_result()
        if isinstance(viewable, pps.CLSectorPlot):
            plot_control = pps.CLSectorPlotControl(viewable)
            win = pw.SinglePlotWindow(
                plot=plot_control,
                res=res,
                # view_loop=view_loop
            )
            self._show_plot_window(win)
        elif isinstance(viewable, pps.ScatterSectorPlot):
            plot_control = pps.PCSectorPlotControl(viewable)
            win = pw.SinglePlotWindow(
                plot=plot_control,
                res=res,
                # view_loop=view_loop
            )
            self._show_plot_window(win)
        else:
            super(IndDiffController, self).open_window(viewable, view_loop)


# Plot creators

def dclk_activator(obj):
    plot_func_name = obj.plot_func_name
    if isinstance(obj.owner_ref, Group):
        res = obj.owner_ref.calcc.model.calc_plsr_groups(obj.owner_ref.member_index)
    elif isinstance(obj.owner_ref, Element):
        res = obj.owner_ref.calcc.model.calc_plsr_pcx(obj.owner_ref.index)
    loop = obj.owner_ref.plots_act
    func = getattr(obj.owner_ref.calcc, plot_func_name)
    view = func(res)
    obj.owner_ref.calcc.open_window(view, loop)


def plot_pca_loadings(obj):
    obj.pca_loadings_plot()


no_view = _traitsui.View()


ind_diff_view = _traitsui.View(
    _traitsui.Item('calc_n_pc',
                   editor=_traitsui.RangeEditor(
                       low_name='min_pc', high_name='max_pc', mode='auto'),
                   style='simple',
                   label='PC to calc:'),
    title='IndDiff settings',
)


ind_diff_nodes = [
    _traitsui.TreeNode(
        node_for=[IndDiffController],
        label='name',
        children='',
        view=ind_diff_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[IndDiffController],
        label='=PCA(set name)',
        icon_path='graphics',
        icon_group='overview.ico',
        icon_open='overview.ico',
        children='pca_x_launchers',
        view=ind_diff_view,
        menu=[],
        on_dclick=plot_pca_loadings),
    _traitsui.TreeNode(
        node_for=[IndDiffController],
        label='=PLSR(X, Y)',
        icon_path='graphics',
        icon_group='overview.ico',
        icon_open='overview.ico',
        children='idx_pls_launchers',
        view=ind_diff_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[IndDiffController],
        label='=Groups',
        icon_path='graphics',
        icon_group='overview.ico',
        icon_open='overview.ico',
        children='groups_list',
        view=ind_diff_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[Element],
        label='name',
        children='plots_act',
        view=no_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[DiffWindowLauncher],
        label='node_name',
        view=no_view,
        menu=[],
        on_dclick=dclk_activator
    ),
]


class IndDiffCalcContainer(pb.CalcContainer):
    calculator = _traits.Instance(idm.IndDiff, idm.IndDiff())



class IndDiffPluginController(pb.PluginController):

    comb = _traits.Instance(idp.IndDiffPicker, idp.IndDiffPicker())
    last_selection = _traits.Set()

    dummy_model_controller = _traits.Instance(IndDiffController, IndDiffController(idm.IndDiff()))

    def init(self, info):
        super(IndDiffPluginController, self).init(info)
        self._update_comb()


    @_traits.on_trait_change('model:dsc:[dsl_changed,ds_changed]',
                             post_init=False)
    def _update_selection_list(self, obj, name, new):
        self._update_comb()


    def _update_comb(self):
        dsc = self.model.dsc
        self.comb.like_set = [('', '')] + dsc.get_id_name_map('Consumer liking')
        self.comb.attr_set = [('', '')] + dsc.get_id_name_map('Consumer characteristics')


    @_traits.on_trait_change('comb:consumer_liking_updated', post_init=False)
    def _handle_like_sel(self, obj, name, old, new):
        self.model.calculations = []
        selection = self.comb.sel_like[0]
        self._make_pca_calc(selection)


    def _make_pca_calc(self, id_l):
        ds_l = self.model.dsc[id_l]

        # Check missing data
        if ds_l.missing_data:
            self._show_missing_warning()
            return

        calc_model = idm.IndDiff(
            id=id_l,
            ds_L=ds_l,
            settings=self.model.calculator)
        calculation = IndDiffController(calc_model, win_handle=self.win_handle)
        self.model.add(calculation)


    @_traits.on_trait_change('comb:consumer_attributes_updated', post_init=False)
    def _handle_attr_sel(self, obj, name, old, new):
        print("Its happening")
        selection = self.comb.sel_attr[0]
        self._make_pls_calc(selection)


    def _make_pls_calc(self, id_a):
        ds_a = self.model.dsc[id_a]
        calc = self.model.calculations[0]
        ds_l = calc.model.ds_L

        # Check missing data
        if ds_a.missing_data:
            self._show_missing_warning()
            return

        # Check data set alignment
        # ns_l = ds_l.n_objs
        # ns_a = ds_a.n_objs
        # if ns_l != ns_a:
        #     self._show_alignment_warning(ds_l, ds_a)
        #     return

        calc.model.id = ds_l.id + id_a
        calc.model.ds_A = ds_a


    def _show_missing_warning(self):
        dlg = dlgs.ErrorMessage()
        dlg.err_msg = 'This matrix has missing values'
        dlg.err_val = (
            "At the current version of ConsumerCheck IndDiff does not handle missing values. "
            "There are three options to work around this problem:\n"
            "  1. Impute the missing values with the imputation method of your choice "
            "outside ConsumerCheck and re-import the data\n"
            "  2. Remove the column with the missing values and re-import the data\n"
            "  3. Remove the row with the missing values and re-import the data")
        dlg.edit_traits(parent=self.win_handle, kind='modal')


    def _show_alignment_warning(self, ds_l, ds_a):
        dlg = dlgs.ErrorMessage()
        dlg.err_msg = 'Consumer liking and sensory profiling data does not align'
        dlg.err_val = (
            "The Consumer liking data and descriptive analysis/sensory profiling "
            "data do not align. There are {0} rows in {1} and {2} rows in the {3}. "
            "Please select other data."
        ).format(ds_l.n_objs, ds_l.display_name, ds_a.n_objs, ds_a.display_name)
        dlg.edit_traits(parent=self.win_handle, kind='modal')


selection_view = _traitsui.Group(
    _traitsui.Item(
        'controller.comb',
        editor=_traitsui.InstanceEditor(),
        style='custom',
        show_label=False,
        width=250,
        height=150,),
    label='Select data set',
    show_border=True,
)


ind_diff_plugin_view = pb.make_plugin_view(
    'IndDiff', ind_diff_nodes, selection_view, ind_diff_view)


if __name__ == '__main__':
    print("IndDiff GUI test start")
    from tests.conftest import imp_ds
    one_branch = False

    # Folder, File name, Display name, DS type
    # ds_L_meta = ('HamData', 'Ham_consumer_liking.txt',
    #              'Ham liking', 'Consumer liking')
    # ds_A_meta = ('HamData', 'Ham_consumer_characteristics.txt',
    #              'Consumer values', 'Consumer characteristics')
    ds_L_meta = ('Cheese', 'ConsumerLiking.txt',
                 'Cheese liking', 'Consumer liking')
    ds_A_meta = ('Cheese', 'ConsumerValues.txt',
                 'Consumer values', 'Consumer characteristics')
    L = imp_ds(ds_L_meta)
    A = imp_ds(ds_A_meta)

    if one_branch:
        ind_diff = idm.IndDiff(ds_L=L, ds_A=A)
        pc = IndDiffController(ind_diff)
        test = pb.TestOneNode(one_model=pc)
        test.configure_traits(view=pb.dummy_view(ind_diff_nodes))
    else:
        dsc = dc.DatasetContainer()
        dsc.add(L)
        dsc.add(A)
        ind_diff = IndDiffCalcContainer(dsc=dsc)
        ppc = IndDiffPluginController(ind_diff)
        ppc.configure_traits(
            view=ind_diff_plugin_view)
        # ppc.print_traits()
