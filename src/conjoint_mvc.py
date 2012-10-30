
# stdlib imports
import sys
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

import numpy as np

# Enthought imports
from traits.api import (HasTraits, Button, Bool, Enum, Instance, List, Str,
                        DelegatesTo, Property, cached_property, on_trait_change)
from traitsui.api import View, Group, Item, Spring, ModelView, CheckListEditor
from traitsui.menu import OKButton

# Local imports
from dataset import DataSet
from ds_table_view import DSTableViewer
# from ds_matrix_view import matrix_view
from conjoint_machine import ConjointMachine
from plot_conjoint import MainEffectsPlot, InteractionPlot
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
    table_win_launchers = List()
    me_plot_launchers = List(Instance(WindowLauncher))
    int_plot_launchers = List()


    def __init__(self, *args, **kwargs):
        super(AConjointHandler, self).__init__(*args, **kwargs)
        self._populate_win_launchers()


    def __eq__(self, other):
        return self.nid == other


    def __ne__(self, other):
        return self.nid != other


    def _populate_win_launchers(self):
        table_win_launchers = [
            ("LS means", 'show_means'),
            ("Fixed effects", 'show_fixed'),
            ("Random effects", 'show_random')]

        self.table_win_launchers = [
            WindowLauncher(owner_ref=self, node_name=nn, func_name=fn)
            for nn, fn in table_win_launchers]
        
        #FIXME: remove test lines under this line
        vn = []
#        for name in self.model.result['lsmeansTable']['data'].dtype.names:
#            if name != ' Estimate ':
#                vn.append(name)
#            else:
#                print "///else///"
#                break
        self.me_plot_launchers = [
            WindowLauncher(
                owner_ref=self, node_name=name,
                func_name='plot_main_effects', func_parms=tuple([name]))
            for name in vn]


    # @on_trait_change('model:ccs:is_done')
    def _update_plot_launchers(self, new=True):
        if new:
            vn = []
            for name in self.model.result['lsmeansTable']['data'].dtype.names:
                if name != ' Estimate ':
                    vn.append(name)
                else:
                    break

            self.me_plot_launchers = [
                WindowLauncher(
                    owner_ref=self, node_name=name,
                    func_name='plot_main_effects', func_parms=tuple([name]))
                for name in vn]

            int_plot_launchers = [
                ("Flavour:Sugarlevel", 'Flavour', 'Sugarlevel'),
                ("Flavour:Sex", 'Flavour', 'Sex'),
                ("Sugarlevel:Sex", 'Sugarlevel', 'Sex'),
                ]

            self.int_plot_launchers = [
                WindowLauncher(
                    owner_ref=self, node_name=nn,
                    func_name='plot_interaction', func_parms=tuple([p_one, p_two]))
                for nn, p_one, p_two in int_plot_launchers]
            self.print_traits()
            print"#self.me_plot_launchers:"
            print self.me_plot_launchers


    def show_random(self):
        logger.info('Show randomTable')
        cj_dm = self.cj_res_ds_adapter(self.model.result['randomTable'], (self.name +
                                       ' - ANOVA table for random effects'))
        self._update_plot_launchers()
        dstv = DSTableViewer(cj_dm)
        dstv.configure_traits(view=dstv.get_view())


    def show_fixed(self):
        logger.info('Show fixed ANOVA table')
        cj_dm = self.cj_res_ds_adapter(self.model.result['anovaTable'], (self.name +
                                       ' - ANOVA table for fixed effects'))
        self._update_plot_launchers()
        dstv = DSTableViewer(cj_dm)
        dstv.configure_traits(view=dstv.get_view())


    def show_means(self):
        logger.info('Show LS mean ANOVA table')
        cj_dm = self.cj_res_ds_adapter(self.model.result['lsmeansTable'], (self.name +
                                       ' - LS means (main effect and interaction)'))
        self._update_plot_launchers()
        dstv = DSTableViewer(cj_dm)
        dstv.configure_traits(view=dstv.get_view())


    def plot_main_effects(self, attr_name):
        print "starting plot main effects"
        print attr_name
        mep = MainEffectsPlot(self.model.result, attr_name)
        mep.new_window(True)


    def plot_interaction(self, attr_one, attr_two):
        mep = InteractionPlot(self.model.result, attr_one, attr_two)
        mep.new_window(True)


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
        # FIXME: Setting parent forcing main ui to stay behind plot windows
        if sys.platform == 'linux2':
            self.win_uis.append( plot_window.edit_traits(kind='live') )
        elif sys.platform == 'win32':
            # FIXME: Investigate more here
            self.win_uis.append(
                # plot_window.edit_traits(parent=self.info.ui.control, kind='nonmodal')
                plot_window.edit_traits(kind='live')
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
            label='Consumer attributes',
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
    from tests.conftest import dsc_mock
    dsl = dsc_mock()


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


        @on_trait_change('bt_show_random')
        def _on_bsr(self, obj, name, new):
            self.show_random()

        @on_trait_change('bt_show_fixed')
        def _on_bsf(self, obj, name, new):
            self.show_fixed()

        @on_trait_change('bt_show_means')
        def _on_bsm(self, obj, name, new):
            self.show_means()


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
