
# Std lib imports
from itertools import combinations
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    # datefmt='%m-%d %H:%M',
                    datefmt='%y%m%dT%H:%M:%S',
                    # filename='/temp/myapp.log',
                    # filemode='w',
                    )
if __name__ == '__main__':
    logger = logging.getLogger('tgxnet.nofima.cc.' + __file__.split('.')[0])
else:
    logger = logging.getLogger(__name__)

# Scipy lib imports
import pandas as _pd

# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui
import chaco.api as _chaco


# Local imports
# from dataset import DataSet
from dataset import DataSet
from conjoint_model import Conjoint
from ds_table_view import DSTableViewer
# from ui_results import TableViewController
from plot_windows import LinePlotWindow, SinglePlotWindow
from plot_conjoint import MainEffectsPlot, InteractionPlot, InteractionPlotWindow

from window_helper import multiplot_factory
from plugin_tree_helper import (WindowLauncher, dclk_activator, overview_activator)
from plugin_base import (ModelController, CalcContainer, PluginController,
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
            ("Residuals", residu_table),
            ]

        return [WindowLauncher(owner_ref=self, node_name=nn, view_creator=fn)
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
                view_creator=plot_interaction, func_parms=tuple([p_one, p_two]))
            for nn, p_one, p_two in int_plot_launchers]


    def open_window(self, viewable):
        """Expected viewable is by now:
          + Plot subtype
          + DataSet type
        """
        if isinstance(viewable, _chaco.DataView):
            print("Plot")
            res = self.model.res

            win = SinglePlotWindow(
                plot=viewable,
                res=res,
                view_loop=self.me_plot_launchers,
                title_text=self._wind_title(res),
                vistog=False
                )

            self._show_plot_window(win)
        elif isinstance(viewable, DataSet):
            table = DSTableViewer(viewable)
            table.edit_traits(view=table.get_view(), kind='live')


    def _wind_title(self, res):
        ds_name = self.model.design.display_name
        # mn = res.method_name
        return "{0} | Conjoint - ConsumerCheck".format(ds_name)



def cj_res_ds_adapter(cj_res, name='Dataset Viewer'):
    cj_df = _pd.DataFrame(cj_res['data'])
    cj_df.index = cj_res['rowNames']
    cj_df.columns = cj_res['colNames']
    dm = DataSet(mat=cj_df, display_name=name)

    return dm



# View creators

def plot_main_effects(res, attr_name):
    plot = MainEffectsPlot(res, attr_name)
    return plot


def plot_interaction(res, attr_one, attr_two):
    plot = InteractionPlot(res, attr_one, attr_two)
    return plot


def means_table(res):
    label= 'LS means (main effect and interaction)'
    cj_dm = cj_res_ds_adapter(res.lsmeansTable, label)

    return cj_dm


def fixed_table(res):
    label = 'ANOVA table for fixed effects'
    cj_dm = cj_res_ds_adapter(res.anovaTable, label)

    return cj_dm


def random_table(res):
    label = 'ANOVA table for random effects'
    cj_dm = cj_res_ds_adapter(res.randomTable, label)

    return cj_dm


def diff_table(res):
    label = 'Pair-wise differences'
    cj_dm = cj_res_ds_adapter(res.lsmeansDiffTable, label)

    return cj_dm


def residu_table(res):
    label = 'Residuals'
    cj_dm = cj_res_ds_adapter(res.residualsTable, label)

    return cj_dm


no_view = _traitsui.View()


conjoint_view = _traitsui.View(
    _traitsui.Item('controller.name', style='readonly', label='Consumer likings'),
    _traitsui.Item('controller.design_name', style='readonly', label='Design'),
    _traitsui.Item('controller.cons_attr_name', style='readonly', label='Consumer charactersitics'),
    _traitsui.Item('model_struct', style='simple', label='Model'),
    _traitsui.Group(
        _traitsui.Group(
            _traitsui.Item('design_vars',
                           editor=_traitsui.CheckListEditor(name='controller.available_design_vars'),
                           style='custom',
                           show_label=False,
                           ),
            label='Design variables:',
            show_border=True,
            springy=True,
            ),
        _traitsui.Group(
            _traitsui.Item('consumers_vars',
                           editor=_traitsui.CheckListEditor(name='controller.available_consumers_vars'),
                           style='custom',
                           show_label=False,
                           ),
            label='Consumer variables:',
            show_border=True,
            springy=True,
            ),
        orientation='horizontal',
        ),
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
        label='=Base tables',
        children='table_win_launchers',
        view=conjoint_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[ConjointController],
        label='=Main effect plots',
        children='me_plot_launchers',
        view=conjoint_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[ConjointController],
        label='=Interaction plots',
        children='int_plot_launchers',
        view=conjoint_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[WindowLauncher],
        label='node_name',
        view=no_view,
        menu=[],
        on_dclick=dclk_activator,
        )
    ]



class ConjointPluginController(PluginController):
    available_design_sets = _traits.List()
    available_consumer_characteristics_sets = _traits.List()
    available_consumer_liking_sets = _traits.List()
    selected_design = _traits.Str()
    selected_consumer_characteristics_set = _traits.Str()
    selected_consumer_liking_sets = _traits.List()


    @_traits.on_trait_change('model:dsc:[dsl_changed,ds_changed]', post_init=False)
    def _update_selection_list(self, obj, name, new):
        self.available_design_sets = self._available_design_sets_default()
        self.available_consumer_characteristics_sets = self._available_consumer_characteristics_sets_default()
        self.available_consumer_liking_sets = self._available_consumer_liking_sets_default()


    def _available_design_sets_default(self):
        return self.model.dsc.get_id_name_map('Design variable')


    def _available_consumer_characteristics_sets_default(self):
        return self.model.dsc.get_id_name_map('Consumer characteristics')


    def _available_consumer_liking_sets_default(self):
        return self.model.dsc.get_id_name_map('Consumer liking')


    @_traits.on_trait_change('selected_consumer_liking_sets')
    def _liking_set_selected(self, obj, name, old_value, new_value):
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
        d = self.model.dsc[self.selected_design]
        c = self.model.dsc[self.selected_consumer_characteristics_set]
        l = self.model.dsc[liking_id]
        calc_model = Conjoint(id=liking_id, design=d, liking=l, consumers=c)
        calculation = ConjointController(calc_model)
        self.model.add(calculation)


selection_view = _traitsui.Group(
    _traitsui.Group(
        _traitsui.Group(
            _traitsui.Label('Design:'),
            _traitsui.Item('controller.selected_design',
                           editor=_traitsui.CheckListEditor(name='controller.available_design_sets'),
                           style='simple',
                           show_label=False,
                           ),
            _traitsui.Label('Consumer characteristics:'),
            _traitsui.Item('controller.selected_consumer_characteristics_set',
                           editor=_traitsui.CheckListEditor(name='controller.available_consumer_characteristics_sets'),
                           style='simple',
                           show_label=False,
                           ),
            show_border=True,
            ),
        _traitsui.Group(
            _traitsui.Label('Liking set:'),
            _traitsui.Item('controller.selected_consumer_liking_sets',
                           editor=_traitsui.CheckListEditor(name='controller.available_consumer_liking_sets'),
                           style='custom',
                           show_label=False,
                           width=200,
                           height=200,
                           ),
            show_border=True,
            ),
        orientation='horizontal',
        ),
    label='Select dataset',
    show_border=True,
    )


conjoint_plugin_view = make_plugin_view('Conjoint', conjoint_nodes, selection_view, conjoint_view)



if __name__ == '__main__':
    print("Conjoint GUI test start")
    from tests.conftest import conjoint_dsc
    from dataset_container import get_ds_by_name

    one_branch = True
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
