
# stdlib imports
import sys

import numpy as np

# Enthought imports
from traits.api import (HasTraits, Button, Enum, Bool, Dict, Instance, List, Str,
                        DelegatesTo, Property, cached_property, on_trait_change)
from traitsui.api import View, Group, Item, Spring, ModelView, CheckListEditor
from traitsui.menu import (OKButton)

# Local imports
from dataset import DataSet
from ds_matrix_view import matrix_view
# import conjoint as cj
from conjoint_machine import ConjointMachine




class ConjointCalcState(HasTraits):
    messages = Str()
    is_done = Bool(False)

    traits_view = View(
        Item('messages',show_label=False, springy=True, style='custom' ),
        Item('is_done',show_label=False, springy=True, style='readonly' ),
        height=400,
        width=1200,
        resizable=True,
        buttons=[OKButton],
        )




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
    # result = Property(depends_on='sel_design_vars, sel_cons_attr_vars, structure')
    result = Dict()


    def update_conjoint_result(self):
        if not self.cm.run_state:
            self.cm.run_state = self.ccs
            
        self.ccs.edit_traits()
        self.cm.schedule_calculation(
            self.structure,
            self.cons_attr, self.sel_cons_attr_vars,
            self.design, self.sel_design_vars,
            self.cons_liking)


    @on_trait_change('ccs.is_done')
    def _result_ready(self):
        print("Result ready")
        self.result = self.cm.get_result()


    # @cached_property
    ## def _get_result(self):
        ## cj_mod = cj.RConjoint(
            ## self.structure,
            ## self.cons_attr, self.sel_cons_attr_vars,
            ## self.design, self.sel_design_vars,
            ## self.cons_liking)
        ## return cj_mod


class AConjointHandler(ModelView):
    plot_uis = List()
    name = DelegatesTo('model')
    nid = DelegatesTo('model')

    # design_vars = List(['Flavour', 'Sugarlevel'])
    sel_design_vars = DelegatesTo('model')
    # cons_attr_vars = List(['Sex', 'Age'])
    sel_cons_attr_vars = DelegatesTo('model')

    btn_calc_conjoint = Button('Calculate conjoint')

    def __eq__(self, other):
        return self.nid == other


    def __ne__(self, other):
        return self.nid != other

    @on_trait_change('model:mother_ref:chosen_design_vars')
    def new_design(self, obj, ref, new):
        print("Design changed")
        self.sel_design_vars = new

    @on_trait_change('model:mother_ref:chosen_consumer_attr_vars')
    def new_cons_attr(self, obj, ref, new):
        print("Cons attr changed")
        self.sel_cons_attr_vars = new


    def _btn_calc_conjoint_fired(self):
        self.model.update_conjoint_result()


    def show_random(self):
        # rand_map = self.model.result.randomTable()
        cj_ds = self.cj_res_ds_adapter(self.model.result['randomTable'])
        cj_ds._ds_name = 'ANOVA table for random effects'
        cj_ds.edit_traits(view=matrix_view)


    def show_fixed(self):
        # anova_map = self.model.result.anovaTable()
        cj_ds = self.cj_res_ds_adapter(self.model.result['anovaTable'])
        cj_ds._ds_name = 'ANOVA table for fixed effects'
        cj_ds.edit_traits(view=matrix_view)


    def show_means(self):
        # ls_means_map = self.model.result.lsmeansTable()
        cj_ds = self.cj_res_ds_adapter(self.model.result['lsmeansTable'])
        cj_ds._ds_name = 'LS means (main effect and interaction)'
        cj_ds.edit_traits(view=matrix_view)


    def cj_res_ds_adapter(self, cj_res):
        ds = DataSet()
        print(cj_res['data'])
        ds.matrix = cj_res['data']
        print(cj_res['colNames'])
        ds.variable_names = list(cj_res['colNames'])
        print(cj_res['rowNames'])
        ds.object_names = list(cj_res['rowNames'])
        ds._is_calculated = True
        ds.print_traits()
        return ds


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
        Item('btn_calc_conjoint', show_label=False),
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

    model = AConjointModel(
        nid='conjoint',
        name='Conjoint test',
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
            height=300,
            )


    controller = AConjointTestHandler(model=model)
    with np.errstate(invalid='ignore'):
        controller.configure_traits()
        # controller.model.print_traits()
