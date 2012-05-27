
# stdlib imports
import sys

import numpy as np

# Enthought imports
from traits.api import (HasTraits, Instance, Str, Int, List, Button, DelegatesTo,
                        Property, on_trait_change)
from traitsui.api import View, Group, Item, ModelView, CheckListEditor


# Local imports
from dataset import DataSet
from plot_pc_scatter import PCScatterPlot
from plot_windows import SinglePlotWindow
from ds_slicer_view import ds_obj_slicer_view, ds_var_slicer_view
import conjoint as cj



class AConjointModel(HasTraits):
    """Represent the Conjoint model of a dataset."""
    name = Str()
    nid = Str()
    # Shoud be Instance(PrefmapsContainer)
    # but who comes first?
    mother_ref = Instance(HasTraits)

    # The imput data for calculation
    design = DataSet()
    sel_design_vars = List()
    cons_attr = DataSet()
    sel_cons_attr_vars = List()
    cons_liking = DataSet()

    # Conjoint settings
    structure = Int(1)

    # depends_on
    result = Property()


    def _get_result(self):
        cj_mod = cj.RConjoint(
            self.structure,
            self.cons_attr, self.sel_cons_attr_vars,
            self.design, self.sel_design_vars,
            self.cons_liking)


class AConjointHandler(ModelView):
    plot_uis = List()
    name = DelegatesTo('model')
    nid = DelegatesTo('model')

    # design_vars = List(['Flavour', 'Sugarlevel'])
    design_vars = List()
    # cons_attr_vars = List(['Sex', 'Age'])
    cons_attr_vars = List()


    def __eq__(self, other):
        return self.nid == other


    def __ne__(self, other):
        return self.nid != other


    def model_design_changed(self, info):
        print("Design changed")
        self.design_vars = self.model.design.variable_names


    def model_cons_attr_changed(self, info):
        print("Cons attr changed")
        self.cons_attr_vars = self.model.cons_attr.variable_names


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


    def _wind_title(self):
        ds_name = self.model.ds._ds_name
        return "{0} | Conjoint - {1} - ConsumerCheck".format(ds_name, dstype)


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
            label='Test1',
            ),
        Group(
            Item('model.sel_cons_attr_vars',
                 editor=CheckListEditor(name='object.cons_attr_vars'),
                 style='custom',
                 show_label=False,
                 ),
            show_border=True,
            label='Test2',
            ),
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
        bt_calc_conjoint = Button('Calc Conjoint')

        @on_trait_change('bt_calc_conjoint')
        def _on_bcc(self, obj, name, new):
            self.model.print_traits()

        traits_view = View(
            Group(
                gr_sel,
                Group(
                    Item('bt_calc_conjoint',
                         show_label=False),
                    show_border=True,
                    ),
                ),
            resizable=True,
            )


    controller = AConjointTestHandler(model=model)
    with np.errstate(invalid='ignore'):
        controller.configure_traits()
        # controller.model.print_traits()
