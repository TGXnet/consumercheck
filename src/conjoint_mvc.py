# stdlib imports
import sys
import numpy as np
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


# Enthought imports
from traits.api import (HasTraits, Button, Bool, Enum, Instance, List, Str,
                        DelegatesTo, Property, cached_property, on_trait_change)
from traitsui.api import View, Group, Item, Spring, ModelView, CheckListEditor
from traitsui.menu import OKButton

# Local imports
from dataset import DataSet
from ds_table_view import DSTableViewer
from plot_windows import LinePlotWindow
# from ds_matrix_view import matrix_view
from conjoint_machine import ConjointMachine
from plot_conjoint import MainEffectsPlot, InteractionPlot, InteractionPlotWindow
from plugin_tree_helper import WindowLauncher


class ConjointCalcState(HasTraits):
    messages = Str()
    is_done = Bool(True)

    traits_view = View(
        Item('messages',show_label=False, springy=True, style='custom' ),
        title='Conjoint calculation status',
        height=300,
        width=600,
        resizable=True,
        buttons=[OKButton],
        )

    def _messages_changed(self, new):
        self.messages = '\n'.join(
            [line for line in new.split('\n') if not line.startswith('try')])

    def _is_done_changed(self, new):
        if new:
            logger.info('Conjoint result ready')
        else:
            logger.info('Staring conjoint calculation')


class AConjointModel(HasTraits):
    """Represent the Conjoint model of a dataset."""
    name = Str()
    nid = Str()
    mother_ref = Instance(HasTraits)

    # The imput data for calculation
    design_set = DelegatesTo('mother_ref')
    chosen_design_vars = DelegatesTo('mother_ref')
    consumer_attr_set = DelegatesTo('mother_ref')
    chosen_consumer_attr_vars = DelegatesTo('mother_ref')
    cons_liking = DataSet()

    # Conjoint settings
    model_structure_type = DelegatesTo('mother_ref')

    # Conjoint calculation state
    ccs = Instance(ConjointCalcState, ())
    cm = Instance(ConjointMachine, ())

    # depends_on
    result = Property(depends_on='mother_ref.chosen_design_vars, mother_ref.chosen_consumer_attr_vars, mother_ref.model_structure_type')

    @cached_property
    def _get_result(self):
        if not self.cm.run_state:
            self.cm.run_state = self.ccs

        self.cm.schedule_calculation(
            self.model_structure_type,
            self.consumer_attr_set, self.chosen_consumer_attr_vars,
            self.design_set, self.chosen_design_vars,
            self.cons_liking)
        self.ccs.edit_traits(kind='livemodal')
        return self.cm.get_result()


class AConjointHandler(ModelView):
    name = DelegatesTo('model')
    nid = DelegatesTo('model')

    win_uis = List()
    table_win_launchers = List(WindowLauncher)
    me_plot_launchers = List(WindowLauncher)
    int_plot_launchers = List(WindowLauncher)


    def __init__(self, *args, **kwargs):
        super(AConjointHandler, self).__init__(*args, **kwargs)
        self._update_nodes()


    def __eq__(self, other):
        return self.nid == other


    def __ne__(self, other):
        return self.nid != other


    @on_trait_change('model.mother_ref.chosen_design_vars')
    def _handle_design_vars(self):
        self._update_nodes()


    @on_trait_change('model.mother_ref.chosen_consumer_attr_vars')
    def _handle_consumer_attr_vars(self):
        self._update_nodes()


    @on_trait_change('model.mother_ref.model_structure_type')
    def _handle_model_struct(self):
        self._update_nodes()


    def _update_nodes(self):
        # Populate table windows launchers
        table_win_launchers = [
            ("LS means", 'show_means'),
            ("Fixed effects", 'show_fixed'),
            ("Random effects", 'show_random')]

        self.table_win_launchers = [
            WindowLauncher(owner_ref=self, node_name=nn, func_name=fn)
            for nn, fn in table_win_launchers]

        # Populate main effects plot launchers
        vn = [n.encode('ascii') for n
              in self.model.chosen_design_vars + self.model.chosen_consumer_attr_vars]

        self.me_plot_launchers = [
            WindowLauncher(
                owner_ref=self, node_name=name,
                func_name='plot_main_effects', func_parms=tuple([name]))
            for name in vn]

        # Populate interaction plot launchers
        if self.model.model_structure_type == 2:
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

        # self.model.mother_ref.update_conjoint_tree = True


    def show_random(self):
        logger.info('Show randomTable')
        cj_dm = self.cj_res_ds_adapter(self.model.result['randomTable'], (self.name +
                                       ' - ANOVA table for random effects'))
        dstv = DSTableViewer(cj_dm)
        dstv.edit_traits(view=dstv.get_view(), parent=self.model.mother_ref.win_handle, kind='live')


    def show_fixed(self):
        logger.info('Show fixed ANOVA table')
        cj_dm = self.cj_res_ds_adapter(self.model.result['anovaTable'], (self.name +
                                       ' - ANOVA table for fixed effects'))
        dstv = DSTableViewer(cj_dm)
        dstv.edit_traits(view=dstv.get_view(), parent=self.model.mother_ref.win_handle, kind='live')


    def show_means(self):
        logger.info('Show LS mean ANOVA table')
        cj_dm = self.cj_res_ds_adapter(self.model.result['lsmeansTable'], (self.name +
                                       ' - LS means (main effect and interaction)'))
        dstv = DSTableViewer(cj_dm)
        dstv.edit_traits(view=dstv.get_view(), parent=self.model.mother_ref.win_handle, kind='live')


    def plot_main_effects(self, attr_name,):
        mep = MainEffectsPlot(self.model.result, attr_name, self.me_plot_launchers)
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
            window.plot = MainEffectsPlot(self.model.result, *npl.func_parms, pl_ref=window.plot.pl_ref)
        elif npl.func_name == 'plot_interaction':
            window.plot = InteractionPlot(self.model.result, *npl.func_parms, pl_ref=window.plot.pl_ref)


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
            window.plot = MainEffectsPlot(self.model.result, *ppl.func_parms, pl_ref=window.plot.pl_ref)
        elif ppl.func_name == 'plot_interaction':
            window.plot = InteractionPlot(self.model.result, *ppl.func_parms, pl_ref=window.plot.pl_ref)


    def plot_interaction(self, attr_one, attr_two):
        plot = InteractionPlot(self.model.result,
                               attr_one, attr_two,
                               self.int_plot_launchers)
        spw = InteractionPlotWindow(
            plot=plot,
            title_text="{0}:{1}".format(attr_one, attr_two),
            vistog=False,
            )
        self._show_plot_window(spw)



    def cj_res_ds_adapter(self, cj_res, name='Dataset Viewer'):
        dm = DataSet(_ds_name=name)
        logger.debug(cj_res['data'])
        dm.matrix = cj_res['data']
        logger.debug(cj_res['colNames'])
        dm.variable_names = list(cj_res['colNames'])
        logger.debug(cj_res['rowNames'])
        dm.object_names = list(cj_res['rowNames'])
        return dm


    def _show_plot_window(self, plot_window):
        plot_window.mother_ref = self
        # FIXME: Setting parent forcing main ui to stay behind plot windows
        if sys.platform == 'linux2':
            self.win_uis.append(
                plot_window.edit_traits(parent=self.model.mother_ref.win_handle, kind='live')
                )
        elif sys.platform == 'win32':
            # FIXME: Investigate more here
            self.win_uis.append(
                plot_window.edit_traits(parent=self.model.mother_ref.win_handle, kind='live')
                # plot_window.edit_traits(kind='live')
                )
        else:
            raise Exception("Not implemented for this platform: ".format(sys.platform))


gr_sel = Group(
    Item('model.name', style='readonly'),
    Group(
        Group(
            Item('model.chosen_design_vars',
                 editor=CheckListEditor(),
                 style='readonly',
                 show_label=False,
                 ),
            show_border=True,
            label='Design variables',
            ),
        Group(
            Item('model.chosen_consumer_attr_vars',
                 editor=CheckListEditor(),
                 style='readonly',
                 show_label=False,
                 ),
            show_border=True,
            label='Consumer characteristics',
            ),
        orientation='horizontal',
        ),
    Group(
        Group(
            Item('model.model_structure_type',
                 style='readonly',
                 width=150,
                 show_label=False),
            show_border=True,
            label='Model model_structure_type',
            ),
        Spring(),
        orientation='horizontal',
        ),
    orientation='vertical',
    )


a_conjoint_view = View(
    gr_sel,
    )


if __name__ == '__main__':
    from tests.conftest import conjoint_dsc
    dsl = conjoint_dsc()


    class MocMother(HasTraits):
        chosen_design_vars = List([u'Flavour', u'Sugarlevel'])
        chosen_consumer_attr_vars = List([u'Sex'])
        model_structure_type = Enum(1, 2, 3)
        design_set = Instance(DataSet),
        consumer_attr_set = Instance(DataSet)

    moc = MocMother()
    moc.design_set = dsl.get_by_id('design')
    moc.consumer_attr_set = dsl.get_by_id('consumerattributes')
    moc.print_traits()

    model = AConjointModel(
        nid='conjoint',
        name='Conjoint test',
        mother_ref=moc,
        cons_liking=dsl.get_by_id('odour-flavour_liking'))


    class AConjointTestHandler(AConjointHandler):
        bt_show_random = Button('Show random table')
        bt_show_fixed = Button('Show fixed table')
        bt_show_means = Button('Show means table')
        bt_show_flavour_plot = Button('Show flavour plot')


        @on_trait_change('bt_show_random')
        def _on_bsr(self, obj, name, new):
            self.show_random()

        @on_trait_change('bt_show_fixed')
        def _on_bsf(self, obj, name, new):
            self.show_fixed()

        @on_trait_change('bt_show_means')
        def _on_bsm(self, obj, name, new):
            self.show_means()

        @on_trait_change('bt_show_flavour_plot')
        def _on_bsp(self, obj, name, new):
            self.plot_main_effects('Flavour')


        traits_view = View(
            Group(
                gr_sel,
                Group(
                    Item('bt_show_random',
                         show_label=False),
                    Item('bt_show_fixed',
                         show_label=False),
                    Item('bt_show_means',
                         show_label=False),
                    Item('bt_show_flavour_plot',
                         show_label=False),
                    show_border=True,
                    ),
                ),
            resizable=True,
            width=400,
            height=400,
            )


    controller = AConjointTestHandler(model=model)
    with np.errstate(invalid='ignore'):
        controller.configure_traits()
