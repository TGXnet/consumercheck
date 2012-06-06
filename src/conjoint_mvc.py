
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
from traits.api import (HasTraits, Button, Enum, Bool, Dict, Instance, List, Str,
                        DelegatesTo, Property, cached_property, on_trait_change)
from traitsui.api import View, Group, Item, Spring, ModelView, CheckListEditor
from traitsui.menu import (OKButton)

# Local imports
from dataset import DataSet
# from ds_matrix_view import matrix_view
from dataset_matrix import DatasetMatrix
from conjoint_machine import ConjointMachine


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
    design = DataSet()
    sel_design_vars = List()
    cons_attr = DataSet()
    sel_cons_attr_vars = List()
    cons_liking = DataSet()

    # Conjoint settings
    structure = Enum(1, 2, 3)

    # Conjoint calculation state
    ccs = Instance(ConjointCalcState, ())
    cm = Instance(ConjointMachine, ())

    # depends_on
    result = Property(depends_on='sel_design_vars, sel_cons_attr_vars, structure')

    @cached_property
    def _get_result(self):
        if not self.cm.run_state:
            self.cm.run_state = self.ccs

        self.cm.schedule_calculation(
            self.structure,
            self.cons_attr, self.sel_cons_attr_vars,
            self.design, self.sel_design_vars,
            self.cons_liking)
        self.ccs.edit_traits(kind='livemodal')
        return self.cm.get_result()


class AConjointHandler(ModelView):
    plot_uis = List()
    name = DelegatesTo('model')
    nid = DelegatesTo('model')

    design_vars = List()
    sel_design_vars = DelegatesTo('model')
    cons_attr_vars = List()
    sel_cons_attr_vars = DelegatesTo('model')

    def __eq__(self, other):
        return self.nid == other


    def __ne__(self, other):
        return self.nid != other


    @on_trait_change('model:mother_ref:chosen_design_vars')
    def _mother_design_var_selected(self, new):
        self.sel_design_vars = new


    @on_trait_change('model:mother_ref:chosen_consumer_attr_vars')
    def _mother_cons_attr_selected(self, new):
        self.sel_cons_attr_vars = new


    def model_design_changed(self, info):
        print("Design changed")
        self.design_vars = self.model.design.variable_names


    def model_cons_attr_changed(self, info):
        print("Cons attr changed")
        self.cons_attr_vars = self.model.cons_attr.variable_names


    def show_random(self):
        logger.info('Show randomTable')
        cj_dm = self.cj_res_ds_adapter(self.model.result['randomTable'])
        # cj_dm._ds_name = 'ANOVA table for random effects'
        cj_dm.edit_traits(view=cj_dm.get_view(
            self.name + ' - ANOVA table for random effects'))


    def show_fixed(self):
        logger.info('Show fixed ANOVA table')
        cj_dm = self.cj_res_ds_adapter(self.model.result['anovaTable'])
        # cj_dm._ds_name = 'ANOVA table for fixed effects'
        cj_dm.edit_traits(view=cj_dm.get_view(
            self.name + ' - ANOVA table for fixed effects'))


    def show_means(self):
        logger.info('Show LS mean ANOVA table')
        cj_dm = self.cj_res_ds_adapter(self.model.result['lsmeansTable'])
        # cj_dm._ds_name = 'LS means (main effect and interaction)'
        cj_dm.edit_traits(view=cj_dm.get_view(
            self.name + ' - LS means (main effect and interaction)'))


    def cj_res_ds_adapter(self, cj_res):
        dm = DatasetMatrix()
        logger.debug(cj_res['data'])
        dm.matrix = cj_res['data']
        logger.debug(cj_res['colNames'])
        dm.col_names = list(cj_res['colNames'])
        logger.debug(cj_res['rowNames'])
        dm.row_names = list(cj_res['rowNames'])
        return dm


    def _show_plot_window(self, plot_window):
        # FIXME: Setting parent forcing main ui to stay behind plot windows
        if sys.platform == 'linux2':
            self.plot_uis.append( plot_window.edit_traits(kind='live') )
        elif sys.platform == 'win32':
            # FIXME: Investigate more here
            self.plot_uis.append(
                # plot_window.edit_traits(parent=self.info.ui.control, kind='nonmodal')
                plot_window.edit_traits(kind='live')
                )
        else:
            raise Exception("Not implemented for this platform: ".format(sys.platform))


gr_sel = Group(
    Item('model.name',
         style='readonly'),
    Group(
        Group(
            Item('model.sel_design_vars',
                 editor=CheckListEditor(name='object.design_vars'),
                 style='custom',
                 show_label=False,
                 ),
            show_border=True,
            label='Design variables',
            ),
        Group(
            Item('model.sel_cons_attr_vars',
                 editor=CheckListEditor(name='object.cons_attr_vars'),
                 style='custom',
                 show_label=False,
                 ),
            show_border=True,
            label='Consumer attributes',
            ),
        orientation='horizontal',
        ),
    Group(
        Group(
            Item('model.structure', show_label=False, width=150),
            show_border=True,
            label='Model structure',
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
    from tests.conftest import make_dsl_mock
    dsl = make_dsl_mock()


    class MocMother(HasTraits):
        chosen_design_vars = List()
        chosen_consumer_attr_vars = List()


    model = AConjointModel(
        nid='conjoint',
        name='Conjoint test',
        mother_ref=MocMother(),
        design=dsl.get_by_id('design'),
        cons_liking=dsl.get_by_id('odour-flavour_liking'),
        cons_attr=dsl.get_by_id('consumerattributes'))


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
        # controller.model.print_traits()
