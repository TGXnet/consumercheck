
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

# Local imports
# from dataset import DataSet
from dataset import DataSet
from conjoint_model import Conjoint
from ds_table_view import DSTableViewer
# from ui_results import TableViewController
from plot_windows import LinePlotWindow
from plot_conjoint import MainEffectsPlot, InteractionPlot, InteractionPlotWindow
from plugin_tree_helper import (WindowLauncher, dclk_activator, ModelController,
                                CalcContainer, PluginController, dummy_view,
                                TestOneNode, make_plugin_view)


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
            ("LS means", 'show_means'),
            ("Fixed effects", 'show_fixed'),
            ("Random effects", 'show_random'),
            ("Pair-wise differences", 'show_diff'),
            ("Residuals", 'show_residu'),
            ]

        return [WindowLauncher(owner_ref=self, node_name=nn, func_name=fn)
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
                func_name='plot_main_effects', func_parms=tuple([name]))
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
                func_name='plot_interaction', func_parms=tuple([p_one, p_two]))
            for nn, p_one, p_two in int_plot_launchers]


    def show_random(self):
        logger.info('Show randomTable')
        cj_dm = self.cj_res_ds_adapter(self.model.res['randomTable'], (self.name +
                                       ' - ANOVA table for random effects'))
        dstv = DSTableViewer(cj_dm)
        dstv.edit_traits(view=dstv.get_view(), parent=self.win_handle, kind='live')
        # dstv.edit_traits(view=dstv.get_view(), kind='live')


    def show_fixed(self):
        logger.info('Show fixed ANOVA table')
        cj_dm = self.cj_res_ds_adapter(self.model.res['anovaTable'], (self.name +
                                       ' - ANOVA table for fixed effects'))
        dstv = DSTableViewer(cj_dm)
        dstv.edit_traits(view=dstv.get_view(), parent=self.win_handle, kind='live')
        # dstv.edit_traits(view=dstv.get_view(), kind='live')


    def show_means(self):
        logger.info('Show LS mean ANOVA table')
        cj_dm = self.cj_res_ds_adapter(self.model.res['lsmeansTable'], (self.name +
                                       ' - LS means (main effect and interaction)'))
        dstv = DSTableViewer(cj_dm)
        dstv.edit_traits(view=dstv.get_view(), parent=self.win_handle, kind='live')
        # dstv.edit_traits(view=dstv.get_view(), kind='live')


    def show_diff(self):
        logger.info('Show difference table')
        cj_dm = self.cj_res_ds_adapter(self.model.res['lsmeansDiffTable'], (self.name +
                                       ' - Pair-wise differences'))
        dstv = DSTableViewer(cj_dm)
        dstv.edit_traits(view=dstv.get_view(), parent=self.win_handle, kind='live')
        # dstv.edit_traits(view=dstv.get_view(), kind='live')


    def show_residu(self):
        logger.info('Show residuals table')
        cj_dm = self.cj_res_ds_adapter(self.model.res['residualsTable'], (self.name +
                                       ' - Residuals'))
        dstv = DSTableViewer(cj_dm)
        dstv.edit_traits(view=dstv.get_view(), parent=self.win_handle, kind='live')
        # dstv.edit_traits(view=dstv.get_view(), kind='live')


    def plot_main_effects(self, attr_name):
        mep = MainEffectsPlot(self.model.res, attr_name, self.me_plot_launchers)
        spw = LinePlotWindow(
            plot=mep,
            title_text=attr_name,
            vistog=False
            )
        self._show_plot_window(spw)


    def show_next_plot(self, window):
        next_pos = 0
        for i, pl in enumerate(window.plot.pl_ref):
            if pl.node_name == window.title_text:
                next_pos = i + 1
        if next_pos >= len(window.plot.pl_ref):
            next_pos = 0
        # Next Plot Launcher
        npl = window.plot.pl_ref[next_pos]
        window.title_text = npl.node_name
        if npl.func_name == 'plot_main_effects':
            window.plot = MainEffectsPlot(self.model.res, *npl.func_parms, pl_ref=window.plot.pl_ref)
        elif npl.func_name == 'plot_interaction':
            window.plot = InteractionPlot(self.model.res, *npl.func_parms, pl_ref=window.plot.pl_ref)


    def show_previous_plot(self, window):
        next_pos = 0
        for i, pl in enumerate(window.plot.pl_ref):
            if pl.node_name == window.title_text:
                next_pos = i - 1
        if next_pos < 0:
            next_pos = len(window.plot.pl_ref) - 1
        # Previous Plot Launcher
        ppl = window.plot.pl_ref[next_pos]
        window.title_text = ppl.node_name
        if ppl.func_name == 'plot_main_effects':
            window.plot = MainEffectsPlot(self.model.res, *ppl.func_parms, pl_ref=window.plot.pl_ref)
        elif ppl.func_name == 'plot_interaction':
            window.plot = InteractionPlot(self.model.res, *ppl.func_parms, pl_ref=window.plot.pl_ref)


    def plot_interaction(self, attr_one, attr_two):
        plot = InteractionPlot(self.model.res,
                               attr_one, attr_two,
                               self.int_plot_launchers)
        spw = InteractionPlotWindow(
            plot=plot,
            title_text="{0}:{1}".format(attr_one, attr_two),
            vistog=False,
            )
        self._show_plot_window(spw)


    def cj_res_ds_adapter(self, cj_res, name='Dataset Viewer'):
        cj_df = _pd.DataFrame(cj_res['data'])
        cj_df.index = cj_res['rowNames']
        cj_df.columns = cj_res['colNames']
        dm = DataSet(mat=cj_df, display_name=name)
        return dm



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
        on_dclick=dclk_activator)
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
