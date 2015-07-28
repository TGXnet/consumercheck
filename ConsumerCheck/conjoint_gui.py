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

# Std lib imports
import logging
logger = logging.getLogger('tgxnet.nofima.cc.'+__name__)
from itertools import combinations

# Scipy lib imports
import numpy as _np

# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui
from traits.trait_notifiers import set_change_event_tracers


def pre_tr(obj, trait_name, old, new, handler):
    print("Trace")


def post_tr(obj, trait_name, old, new, handler, exception=None):
    print("Trace: ", obj, trait_name, old, new, handler)
    if exception is not None:
        print("Trace ex: ", obj, trait_name, old, new, handler, exception)


# set_change_event_tracers(post_tracer=post_tr)


# Local imports
from dataset import DataSet
from dialogs import ErrorMessage
from conjoint_model import Conjoint
from plot_windows import SinglePlotWindow
from plot_conjoint import (MainEffectsPlot, InteractionPlot,
                           InteractionPlotControl)
from plugin_tree_helper import (WindowLauncher, dclk_activator)
from conjoint_base import PluginController
from plugin_base import (ModelController, CalcContainer,
                         dummy_view, TestOneNode, make_plugin_view)


class ConjointController(ModelController):
    '''Controller for one Conjoint calculation'''
    table_win_launchers = _traits.List(WindowLauncher)
    me_plot_launchers = _traits.List(WindowLauncher)
    int_plot_launchers = _traits.List(WindowLauncher)

    design_name = _traits.Str()
    cons_attr_name = _traits.Str()

    available_design_vars = _traits.List(_traits.Str())
    available_consumers_vars = _traits.List(_traits.Str())

    model_desc = _traits.Str(
        '''
        Consumer characteristics and design values can only be categorical values.<br /><br />
        Model structure descriptions:
        <ul>
        <li>1. Analysis of main effects, Random consumer effect AND interaction between consumer and the main effects.</li>
        <li>2. Main effects AND all 2-factor interactions. Random consumer effect AND interaction between consumer and all fixed effects (both main and interaction ones).</li>
        <li>3. Full factorial model with ALL possible fixed and random effects. (Automized reduction in random part, AND automized reduction in fixed part). The p-values may be inflated and should be interpreted with care when using this approach.</li>
        </ul>
        ''')

    def _name_default(self):
        return self.model.liking.display_name

    def _design_name_default(self):
        return self.model.design.display_name

    def _cons_attr_name_default(self):
        return self.model.consumers.display_name

    def _available_design_vars_default(self):
        return self.model.design.var_n

    def _available_consumers_vars_default(self):
        return self.model.consumers.var_n

    def _table_win_launchers_default(self):
        return self._populate_table_win_launchers()

    def _populate_table_win_launchers(self):
        # Populate table windows launchers
        table_win_launchers = [
            ("LS means", means_table),
            ("Fixed effects", fixed_table),
            ("Random effects", random_table),
            ("Pair-wise differences", diff_table),
            ("Full model residuals", residu_table),
            ("Double centred residuals", resid_ind_table),
            ]

        return [WindowLauncher(owner_ref=self, node_name=nn,
                               view_creator=fn, loop_name='table_win_launchers',)
                for nn, fn in table_win_launchers]

    @_traits.on_trait_change('model:[design_vars,consumers_vars,model_struct]')
    def _update_plot_lists(self):
        self._populate_me_plot_launchers()
        self._populate_int_plot_launchers()

    def _populate_me_plot_launchers(self):
        vn = [n.encode('ascii') for n
              in self.model.design_vars + self.model.consumers_vars]

        self.me_plot_launchers = [
            WindowLauncher(
                owner_ref=self, node_name=name,
                loop_name='me_plot_launchers',
                view_creator=plot_main_effects, func_parms=tuple([name]))
            for name in vn]

    def _populate_int_plot_launchers(self):
        vn = [n.encode('ascii') for n
              in self.model.design_vars + self.model.consumers_vars]

        if self.model.model_struct == 'Struct 2':
            int_plot_launchers = [
                ("{0}:{1}".format(*comb), comb[0], comb[1])
                for comb in combinations(vn, 2)]
        else:
            int_plot_launchers = []

        self.int_plot_launchers = [
            WindowLauncher(
                owner_ref=self, node_name=nn,
                loop_name='int_plot_launchers',
                view_creator=plot_interaction, func_parms=tuple([p_one, p_two]))
            for nn, p_one, p_two in int_plot_launchers]

    def open_window(self, viewable, view_loop):
        """Expected viewable is by now:
          + Plot subtype
          + DataSet type
        """
        if isinstance(viewable, InteractionPlot):
            res = self.get_result()
            plot_control = InteractionPlotControl(viewable)

            win = SinglePlotWindow(
                plot=plot_control,
                res=res,
                view_loop=view_loop,
                )

            self._show_plot_window(win)
        else:
            super(ConjointController, self).open_window(viewable, view_loop)


# View creators

def plot_main_effects(res, attr_name):
    plot = MainEffectsPlot(res, attr_name)
    return plot


def plot_interaction(res, attr_one, attr_two):
    plot = InteractionPlot(res, attr_one, attr_two)
    return plot


def means_table(res):
    return res.lsmeansTable


def fixed_table(res):
    return res.anovaTable


def random_table(res):
    return res.randomTable


def diff_table(res):
    return res.lsmeansDiffTable


def residu_table(res):
    return res.residualsTable


def resid_ind_table(res):
    return res.residIndTable


no_view = _traitsui.View()


conjoint_view = _traitsui.View(
    _traitsui.Item('controller.model.owner_ref.model_struct', style='simple', show_label=False),
    _traitsui.Item('controller.model_desc',
                   editor=_traitsui.HTMLEditor(),
                   # height=250,
                   # width=400,
                   resizable=True,
                   show_label=False),
    title='Conjoint settings',
)


ds_exp_action = _traitsui.Action(
    name='Copy to Data set',
    visible_when='object.node_name in ("Double centred residuals", "Full model residuals")',
    action='handler.export_data(editor, object)',
    )


conjoint_nodes = [
    _traitsui.TreeNode(
        node_for=[ConjointController],
        label='name',
        children='',
        view=conjoint_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[ConjointController],
        label='=Analysis results',
        children='table_win_launchers',
        auto_open=True,
        view=conjoint_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[ConjointController],
        label='=Main effect plots',
        children='me_plot_launchers',
        auto_open=True,
        view=conjoint_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[ConjointController],
        label='=Interaction plots',
        children='int_plot_launchers',
        # FIXME: auto_open is her as and hack to force adding adding children
        # to int plots when model is changed to 2
        auto_open=True,
        view=conjoint_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[WindowLauncher],
        label='node_name',
        view=no_view,
        menu=_traitsui.Menu(ds_exp_action),
        on_dclick=dclk_activator,
        )
    ]


class ConjointCalcContainer(CalcContainer):
    # calculator = _traits.Instance(Conjoint, Conjoint())
    pass


class ConjointPluginController(PluginController):
    available_design_sets = _traits.List()
    available_consumer_characteristics_sets = _traits.List()
    available_consumer_liking_sets = _traits.List()
    selected_design = _traits.Str()
    selected_consumer_characteristics_set = _traits.Str()
    selected_consumer_liking_sets = _traits.List()
    design = _traits.Instance(DataSet, DataSet())
    consumers = _traits.Instance(DataSet, DataSet())

    sel_design_var = _traits.List()
    design_vars = _traits.List()
    sel_cons_char = _traits.List()
    consumer_vars = _traits.List()

    model_struct = _traits.Enum('Struct 1', 'Struct 2', 'Struct 3')

    dummy_model_controller = _traits.Instance(ConjointController)
    exported = _traits.Int(0)
    liking_msg = _traits.Str('(You must select design first!)')

    def _dummy_model_controller_default(self):
        return ConjointController(Conjoint(owner_ref=self))

    @_traits.on_trait_change('model:dsc:[dsl_changed,ds_changed]', post_init=False)
    def _update_selection_list(self, obj, name, new):
        self.available_design_sets = self._available_design_sets_default()
        self.available_consumer_characteristics_sets = self._available_consumer_characteristics_sets_default()
        self.available_consumer_liking_sets = self._available_consumer_liking_sets_default()

    def _available_design_sets_default(self):
        return [('', '')] + self.model.dsc.get_id_name_map('Product design')

    def _available_consumer_characteristics_sets_default(self):
        return [('', '')] + self.model.dsc.get_id_name_map('Consumer characteristics')

    def _available_consumer_liking_sets_default(self):
        return self.model.dsc.get_id_name_map('Consumer liking')

    @_traits.on_trait_change('selected_design')
    def _upd_des_attr_list(self, obj, name, old_value, new_value):
        self.selected_consumer_characteristics_set = ''
        self.selected_consumer_liking_sets = []
        d = self.model.dsc[self.selected_design]
        nn = []
        for k, v in d.mat.iteritems():
            nn.append((k, len(_np.unique(v.values))))
        varn = []
        for k, v in nn:
            varn.append((k, "{0} ({1})".format(k, v)))
        self.design = d
        self.design_vars = varn

    @_traits.on_trait_change('selected_consumer_characteristics_set')
    def _upd_cons_attr_list(self, obj, name, old_value, new_value):
        if self.selected_consumer_characteristics_set:
            d = self.model.dsc[self.selected_consumer_characteristics_set]
        else:
            d = DataSet()
        nn = []
        for k, v in d.mat.iteritems():
            nn.append((k, len(_np.unique(v.values))))
        # Check if some attribute have more than five categories
        for k, v in nn:
            if v > 5:
                warn = """
{0} has {1} categories. Conjoint is not suitable
for variables with a large number of categories.
""".format(k, v)
                cw = ConjointWarning(messages=warn)
                cw.edit_traits()
        varn = []
        for k, v in nn:
            varn.append((k, "{0} ({1})".format(k, v)))
        self.consumers = d
        self.consumer_vars = varn

#    @_traits.on_trait_change('sel_design_var')
#    def _upd_design_var(self, obj, name, old_value, new_value):
#        if isinstance(self.selected_object, ModelController):
#            self.selected_object.model.design_vars = new_value
#        elif isinstance(self.selected_object, WindowLauncher):
#            self.selected_object.owner_ref.model.design_vars = new_value
#
#
#    @_traits.on_trait_change('sel_cons_char')
#    def _upd_cons_char(self, obj, name, old_value, new_value):
#        if isinstance(self.selected_object, ModelController):
#            self.selected_object.model.consumers_vars = new_value
#        elif isinstance(self.selected_object, WindowLauncher):
#            self.selected_object.owner_ref.model.consumers_vars = new_value

    @_traits.on_trait_change('selected_consumer_liking_sets')
    def _liking_set_selected(self, obj, name, old_value, new_value):
        # if self.selected_design == '':
        #     warn = """You must select design first."""
        #     cw = ConjointWarning(messages=warn)
        #     cw.edit_traits()
        #     # del(self.selected_consumer_liking_sets[0])
        #     return
        last = set(old_value)
        new = set(new_value)
        removed = last.difference(new)
        added = new.difference(last)
        if removed:
            self.model.remove(list(removed)[0])
        elif added:
            self._make_calculation(list(added)[0])

        self.update_tree = True

    def _make_calculation(self, liking_id):
        # d = self.model.dsc[self.selected_design]
        l = self.model.dsc[liking_id]
        ## if self.selected_consumer_characteristics_set:
        ##     c = self.model.dsc[self.selected_consumer_characteristics_set]
        ## else:
        ##     c = DataSet(display_name = '-')

        # Check data set alignment
        nds = self.design.n_objs
        nls = l.n_objs
        nlc = l.n_vars
        nca = self.consumers.n_objs

        if nca > 0:
            if (nds != nls) or (nlc != nca):
                self._show_alignment_warning(nds, nls, nlc, nca)
                return
        else:
            if nds != nls:
                self._show_alignment_warning(nds, nls, nlc)
                return

        calc_model = Conjoint(owner_ref=self, id=liking_id,
                              ## design=d,
                              design_vars=self.sel_design_var,
                              ## consumers=c,
                              consumers_vars=self.sel_cons_char,
                              liking=l)
        calculation = ConjointController(calc_model, win_handle=self.win_handle)
        calculation._update_plot_lists()
        self.model.add(calculation)

    def _show_alignment_warning(self, nds, nls, nlc, nca=0):
        dlg = ErrorMessage()
        dlg.err_msg = 'Alignment mismatch between the data set'
        dlg.err_val = 'There is {0} variants in the design matrix and {1} variants in the liking matrix. There is {2} consumers in the liking matrix and {3} consumers in the consumer characteristics matrix'.format(nds, nls, nlc, nca)
        dlg.edit_traits(parent=self.win_handle, kind='modal')

    def export_data(self, editor, obj):
        parent = editor.get_parent(obj)
        res_name = obj.node_name
        ind_resid = DataSet()
        if res_name == 'Double centred residuals':
            ind_resid.copy_traits(
                parent.model.res.residIndTable, traits=['mat', 'style'])
            ind_resid.display_name = '_double centred residuals ' + str(self.exported)
        elif res_name == 'Full model residuals':
            ind_resid.copy_traits(
                parent.model.res.residualsTable, traits=['mat', 'style'])
            ind_resid.display_name = '_full model residuals ' + str(self.exported)
        ind_resid.kind = 'Descriptive analysis / sensory profiling'
        self.exported += 1
        self.model.dsc.add(ind_resid)

    @_traits.on_trait_change('model_struct')
    def _struct_changed(self, info):
        self.update_tree = True


class ConjointWarning(_traits.HasTraits):
    messages = _traits.Str()

    traits_view = _traitsui.View(
        _traitsui.Item('messages', show_label=False, springy=True, style='custom'),
        title='Conjoint warning',
        height=300,
        width=600,
        resizable=True,
        buttons=[_traitsui.OKButton],
        )


selection_view = _traitsui.Group(
    _traitsui.Group(
        _traitsui.Group(
            _traitsui.Label('Design:'),
            _traitsui.Item('controller.selected_design',
                           editor=_traitsui.CheckListEditor(name='controller.available_design_sets'),
                           style='simple',
                           show_label=False,
                           ),
            _traitsui.Label('Variables:'),
            _traitsui.Item('controller.sel_design_var',
                           editor=_traitsui.CheckListEditor(
                               name='controller.design_vars'),
                           style='custom',
                           show_label=False,
                           ),
            show_border=True,
        ),
        _traitsui.Group(
            _traitsui.Label('Consumer characteristics:'),
            _traitsui.Item('controller.selected_consumer_characteristics_set',
                           editor=_traitsui.CheckListEditor(name='controller.available_consumer_characteristics_sets'),
                           style='simple',
                           show_label=False,
                           ),
            _traitsui.Label('Variables:'),
            _traitsui.Item('controller.sel_cons_char',
                           editor=_traitsui.CheckListEditor(
                               name='controller.consumer_vars'),
                           style='custom',
                           show_label=False,
                           # height=100,
                           ),
            show_border=True,
        ),
        _traitsui.Group(
            _traitsui.Label('Liking set:'),
            _traitsui.UItem('controller.liking_msg', style='readonly', visible_when="controller.selected_design == ''"),
            _traitsui.Item('controller.selected_consumer_liking_sets',
                           editor=_traitsui.CheckListEditor(name='controller.available_consumer_liking_sets'),
                           style='custom',
                           show_label=False,
                           # width=400,
                           enabled_when="controller.selected_design != ''",
                           ),
            show_border=True,
            ),
        orientation='horizontal',
        ),
    # _traitsui.Item('controller.model_struct', style='simple', label='Model'),
    label='Select data set',
    show_border=True,
)

conjoint_plugin_view = make_plugin_view('Conjoint', conjoint_nodes, selection_view, conjoint_view)


if __name__ == '__main__':
    print("Conjoint GUI test start")
    from tests.conftest import conjoint_dsc
    from dataset_container import get_ds_by_name

    one_branch = False
    dsc = conjoint_dsc()

    if one_branch:
        d = get_ds_by_name('Tine yogurt design', dsc)
        l = get_ds_by_name('Odour-flavor', dsc)
        c = get_ds_by_name('Consumers', dsc)

        cj = Conjoint(design=d, liking=l, consumers=c)
        cjc = ConjointController(cj)
        test = TestOneNode(one_model=cjc)
        test.configure_traits(view=dummy_view(conjoint_nodes))
    else:
        conjoint = CalcContainer(dsc=conjoint_dsc())
        cpc = ConjointPluginController(conjoint)
        cpc.configure_traits(view=conjoint_plugin_view)
