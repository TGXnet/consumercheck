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


class TreeElement(_traits.HasTraits):
    # FIXME: What kind of element is this?
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


class Segment(TreeElement):
    member_index = _traits.List()


class IndDiffController(pb.ModelController):

    individual_differences = _traits.List(TreeElement)
    segments_analysis = _traits.List(TreeElement)
    apriori_segments = _traits.List(TreeElement)

    gr_name_inc = _traits.Int(0)


    def _name_default(self):
        return "indDiff - {0}".format(self.model.ds_L.display_name)


    def _individual_differences_default(self):
        return [TreeElement(name='Pricipal components of likings', index='', calcc=self),
                TreeElement(name='Liking data', index='', calcc=self)]


    def add_segment(self, members):
        self.gr_name_inc += 1
        el = Segment(name="Segment {0}".format(self.gr_name_inc), calcc=self, member_index=list(members))
        self.segments_analysis.append(el)


    def _show_zero_var_warning(self):
        dlg = dlgs.ErrorMessage()
        dlg.err_msg = 'Removed zero variance variables'
        dlg.err_val = ', '.join(self.model.C_zero_std+self.model.S_zero_std)
        dlg.edit_traits(parent=self.win_handle, kind='modal')


    def pca_loadings_plot(self):
        """Make PCA loadings
        """
        res = self.model.pca_Y
        plot = self.pca_x_loadings_plot(res)
        # wl = self.window_launchers
        # title = self._wind_title(res)
        # self._show_plot_window(plot)
        # view_loop = self.pca_x_response

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
        if isinstance(viewable, pps.CLSectorPlot):
            plot_control = pps.CLSectorPlotControl(viewable)
            win = pw.SinglePlotWindow(
                plot=plot_control,
                # res=res,
                # view_loop=view_loop
            )
            self._show_plot_window(win)
        elif isinstance(viewable, pps.ScatterSectorPlot):
            plot_control = pps.PCSectorPlotControl(viewable)
            win = pw.SinglePlotWindow(
                plot=plot_control,
            )
            self._show_plot_window(win)
        elif isinstance(viewable, PCScatterPlot):
            plot_control = PCPlotControl(viewable)
            win = SinglePlotWindow(
                plot=plot_control,
            )
            self._show_plot_window(win)
        else:
            print("Something missing here")
            # super(IndDiffController, self).open_window(viewable, view_loop)


# Plot creators

def dclk_activator(obj):
    owner = obj.owner_ref
    pfn = obj.plot_func_name
    if isinstance(owner, Segment):
        res = owner.calcc.model.calc_plsr_da(owner.calcc.segments_analysis)
        func = getattr(owner.calcc, pfn)
        view = func(res)
        loop = owner.plots_act
        owner.calcc.open_window(view, loop)
    elif isinstance(owner, TreeElement):
        # Raw linking
        res = owner.calcc.model.calc_pls_raw_liking()
        func = getattr(owner.calcc, pfn)
        view = func(res)
        loop = owner.plots_act
        owner.calcc.open_window(view, loop)
    elif isinstance(owner, IndDiffController):
        func = getattr(owner, pfn)
        func()


no_view = _traitsui.View()


ind_diff_view = _traitsui.View(
    # _traitsui.Item('calc_n_pc',
    #                editor=_traitsui.RangeEditor(
    #                    low_name='min_pc', high_name='max_pc', mode='auto'),
    #                style='simple',
    #                label='PC to calc:'),
    _traitsui.Item('dummify_variables',
                   editor=_traitsui.CheckListEditor(name='consumer_variables'),
                   style='custom',
                   label='Dummify variables:'),
    title='IndDiff settings',
)



ds_dum_attr_action = _traitsui.Action(
    name='Export dummified attributes',
    # visible_when='object.node_name in ("Fixed residuals", "Full model residuals")',
    action='handler.export_dum_attr(editor, object)',
)


ds_dum_seg_action = _traitsui.Action(
    name='Export dummified segments',
    # visible_when='object.node_name in ("Fixed residuals", "Full model residuals")',
    action='handler.export_dum_segments(editor, object)',
)




ind_diff_nodes = [
    _traitsui.TreeNode(
        node_for=[IndDiffController],
        label='name',
        children='',
        view=ind_diff_view,
        menu=[]
    ),
    _traitsui.TreeNode(
        node_for=[IndDiffController],
        label='=Individual difference per ce',
        children='individual_differences',
        view=ind_diff_view,
        menu=_traitsui.Menu(ds_dum_attr_action),
    ),
    _traitsui.TreeNode(
        node_for=[IndDiffController],
        label='=Analysis of segments',
        children='segments_analysis',
        view=ind_diff_view,
        menu=_traitsui.Menu(ds_dum_seg_action),
    ),
    _traitsui.TreeNode(
        node_for=[IndDiffController],
        label='=Coloring of a priori segments',
        children='apriori_segments',
        view=ind_diff_view,
        menu=_traitsui.Menu(ds_dum_seg_action),
    ),
    _traitsui.TreeNode(
        node_for=[TreeElement],
        label='name',
        children='plots_act',
        view=no_view,
        menu=[]
    ),
    _traitsui.TreeNode(
        node_for=[DiffWindowLauncher],
        label='node_name',
        icon_path='graphics',
        icon_group='overview.ico',
        icon_open='overview.ico',
        view=no_view,
        menu=[],
        on_dclick=dclk_activator,
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

        calc.model.id = ds_l.id + id_a
        calc.model.ds_A = ds_a

        self.model.calculator.consumer_variables = calc.model.ds_A.var_n


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


    def export_dum_attr(self, editor, obj):
        dummy = obj.model.ds_X
        dummy.display_name += '_dummified'
        self.model.dsc.add(dummy)


    def export_dum_segments(self, editor, obj):
        dummy = obj.model.make_liking_dummy_segmented(obj.segments_analysis)
        dummy.display_name += '_dummified'
        self.model.dsc.add(dummy)







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
