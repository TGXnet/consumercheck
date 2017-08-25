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
from plot_windows import SinglePlotWindow


class DiffWindowLauncher(pth.WindowLauncher):
    plot_func_name = _traits.Str()


class TreeElement(_traits.HasTraits):
    '''Represent a calculation (analysis) in the Individual Difference methods ensembe
    '''
    name = _traits.Str()
    calcc = _traits.WeakRef()
    plots_act = _traits.List(DiffWindowLauncher)

    def _plots_act_default(self):

        acts = [
            # ("Overview", plot_overview),
            ("X Scores", 'plsr_x_scores_plot'),
            ("X & Y correlation loadings", 'plsr_corr_loadings_plot'),
            ("X Loadings", 'plsr_x_loadings_plot'),
            ("Y loadings", 'plsr_y_loadings_plot'),
            ("Explained var in X", 'plsr_x_expl_var_plot'),
            ("Explained var in Y", 'plsr_y_expl_var_plot'),
        ]

        return [DiffWindowLauncher(
            node_name=nn,
            plot_func_name=fn,
            owner_ref=self,
            loop_name='plots_act',) for nn, fn in acts]


class SegmentTE(TreeElement):
    pass


class PCLikingTE(TreeElement):
    pass


class ColorTE(TreeElement):
    def _plots_act_default(self):

        acts = [
            # ("Overview", plot_overview),
            # ("Scores", 'pca_color_scores_plot'),
            # ("X&Y correlation loadings", corr_loadings_plot),
            ("Loadings", 'pca_color_loadings_plot'),
            # ("Y loadings", loadings_y_plot),
            # ("Explained var in X", expl_var_x_plot),
            # ("Explained var in Y", expl_var_y_plot),
        ]

        return [DiffWindowLauncher(
            node_name=nn,
            plot_func_name=fn,
            owner_ref=self,
            loop_name='plots_act',) for nn, fn in acts]


class IndDiffController(pb.ModelController):

    individual_differences = _traits.List(TreeElement)
    segments_analysis = _traits.List()
    apriori_segments = _traits.List(TreeElement)


    def _name_default(self):
        return "indDiff - {0}".format(self.model.ds_L.display_name)


    def _individual_differences_default(self):
        return [PCLikingTE(name='Pricipal components of likings', calcc=self),
                TreeElement(name='Liking data', calcc=self)]


    def _segments_analysis_default(self):
        return [DiffWindowLauncher(node_name='Define segments', plot_func_name='define_segments_plot', owner_ref=self),
                SegmentTE(name='Discriminant analysis', calcc=self)]


    def _apriori_segments_default(self):
        attrs = self.model.ds_X
        segments = []
        for sub in attrs.get_subset_groups():
            segments.append(ColorTE(name=sub, calcc=self))
        return segments


    def _show_zero_var_warning(self):
        dlg = dlgs.ErrorMessage()
        dlg.err_msg = 'Removed zero variance variables'
        dlg.err_val = ', '.join(self.model.C_zero_std+self.model.S_zero_std)
        dlg.edit_traits(parent=self.win_handle, kind='modal')


    def define_segments_plot(self):
        res = self.model.pca_L
        plot = self.pca_x_loadings_plot(res)
        plot_control = pps.PCSelectionControl(plot)

        win = SinglePlotWindow(
            plot=plot_control,
            res=res
        )
        self._show_plot_window(win)


    def pca_x_loadings_plot(self, res):
        self.model.selected_segments = seg = ds.Factor('Segments', 500)
        plot = pps.SelectionScatterPlot(res.loadings, title='Liking scores')
        plot.data.coloring_factor = seg
        return plot


    def pca_color_loadings_plot(self, res, group):
        res.loadings.subs = self.model.ds_A.subs
        plot = pps.SelectionScatterPlot(res.loadings, title='Liking scores')
        plot.color_subsets_group(group)
        return plot


    def plsr_x_scores_plot(self, res):
        plot = pps.PCScatterPlot(res.scores_x, res.expl_var_x, res.expl_var_y, title='X scores')
        return plot


    def plsr_corr_loadings_plot(self, res):
        plot = pps.CLPlot(
            res.corr_loadings_x, res.expl_var_x,
            res.corr_loadings_y, res.expl_var_y,
            em=False,
            title='X & Y correlation loadings')
        return plot


    def plsr_x_loadings_plot(self, res):
        plot = pps.PCScatterPlot(res.loadings_x, res.expl_var_x, title='X loadings')
        return plot


    def plsr_y_loadings_plot(self, res):
        plot = pps.PCScatterPlot(res.loadings_y, res.expl_var_y, title='Y loadings')
        return plot


    def plsr_x_expl_var_plot(self, res):
        plot = pel.EVLinePlot(res.expl_var_x, title='Explained variance in X')
        return plot


    def plsr_y_expl_var_plot(self, res):
        plot = pel.EVLinePlot(res.expl_var_y, title='Explained variance in Y')
        return plot


    def open_window(self, viewable, view_loop, res):
        """Expected viewable is by now:
          + Plot subtype
          + DataSet type
        """
        if isinstance(viewable, pps.PCScatterPlot):
            plot_control = pps.PCPlotControl(viewable)
            win = SinglePlotWindow(
                plot=plot_control,
                res=res,
            )
            self._show_plot_window(win)
        elif isinstance(viewable, pps.CLPlot):
            plot_control = pps.CLPlotControl(viewable)
            win = pw.SinglePlotWindow(
                plot=plot_control,
                res=res,
            )
            self._show_plot_window(win)
        elif isinstance(viewable, pel.EVLinePlot):
            plot_control = pps.NoPlotControl(viewable)
            win = SinglePlotWindow(
                plot=plot_control,
                res=res,
            )
            self._show_plot_window(win)
        else:
            print("open_window missing something")
            # super(IndDiffController, self).open_window(viewable, view_loop)


# Plot creators

def dclk_activator(obj):
    owner = obj.owner_ref
    pfn = obj.plot_func_name
    if isinstance(owner, SegmentTE):
        res = owner.calcc.model.calc_plsr_da(owner.calcc.model.selected_segments)
        func = getattr(owner.calcc, pfn)
        view = func(res)
        loop = owner.plots_act
        owner.calcc.open_window(view, loop, res)
    elif isinstance(owner, ColorTE):
        res = owner.calcc.model.pca_L
        func = getattr(owner.calcc, pfn)
        view = func(res, owner.name)
        loop = owner.plots_act
        owner.calcc.open_window(view, loop, res)
    elif isinstance(owner, PCLikingTE):
        res = owner.calcc.model.calc_pls_pc_likings(owner.calcc.model.settings.selected_liking_pc)
        func = getattr(owner.calcc, pfn)
        view = func(res)
        loop = owner.plots_act
        owner.calcc.open_window(view, loop, res)
    elif isinstance(owner, TreeElement):
        res = owner.calcc.model.calc_pls_raw_liking()
        func = getattr(owner.calcc, pfn)
        view = func(res)
        loop = owner.plots_act
        owner.calcc.open_window(view, loop, res)
    elif isinstance(owner, IndDiffController):
        func = getattr(owner, pfn)
        func()


no_view = _traitsui.View()


ind_diff_view = _traitsui.View(
    _traitsui.Item('ev_export_segments', show_label=False),
    _traitsui.Item('ev_export_dummified', show_label=False),
    _traitsui.Item('num_segments', style='readonly'),
    _traitsui.Group(
        _traitsui.Item('dummify_variables',
                       editor=_traitsui.CheckListEditor(name='consumer_variables'),
                       style='custom',
                       label='Dummify variables:'),
        label='Dummify variables',
    ),
    _traitsui.Group(
        _traitsui.Item('selected_liking_pc',
                       editor=_traitsui.CheckListEditor(name='n_Y_pc'),
                       style='custom',
                       label='Liking PC:'),
        label='Liking PC',
    ),
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
        view=no_view,
        menu=[]
    ),
    _traitsui.TreeNode(
        node_for=[IndDiffController],
        label='=Individual difference per ce',
        children='individual_differences',
        view=no_view,
        menu=_traitsui.Menu(ds_dum_attr_action),
    ),
    _traitsui.TreeNode(
        node_for=[IndDiffController],
        label='=Analysis of segments',
        children='segments_analysis',
        view=no_view,
        menu=_traitsui.Menu(ds_dum_seg_action),
    ),
    _traitsui.TreeNode(
        node_for=[IndDiffController],
        label='=Coloring of a priori segments',
        children='apriori_segments',
        view=no_view,
        menu=_traitsui.Menu(ds_dum_seg_action),
    ),
    _traitsui.TreeNode(
        node_for=[TreeElement, PCLikingTE],
        label='name',
        children='plots_act',
        view=no_view,
        menu=[]
    ),
    _traitsui.TreeNode(
        node_for=[SegmentTE],
        label='name',
        children='plots_act',
        view=no_view,
        menu=[]
    ),
    _traitsui.TreeNode(
        node_for=[ColorTE],
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

    def __init__(self, *args, **kwargs):
        super(IndDiffCalcContainer, self).__init__(*args, **kwargs)
        self.calculator.owner = self


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
