
# stdlib imports
import sys

import numpy as np

# Enthought imports
from traits.api import (HasTraits, Instance, Str, Int, List, Button, DelegatesTo,
                        Property, on_trait_change)
from traitsui.api import View, Group, Item, ModelView


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
    consumer_liking = DataSet()
    consumer_attributes = DataSet()

    # Conjoint settings
    structure = Int(1)

    # depends_on
    result = Property()


    def _get_result(self):
        cons_attr = self.consumer_attributes
        sel_cons_attr = ['sex']
        design_vars = self.design
        sel_design_vars = ['Flavour', 'Sugarlevel']
        cons_liking = self.consumer_liking
        cons_liking_tag = 'odourflavour'
        cj_mod = cj.RConjoint(
            self.structure,
            cons_attr, sel_cons_attr,
            design_vars, sel_design_vars,
            cons_liking, cons_liking_tag)




class AConjointHandler(ModelView):
    plot_uis = List()
    name = DelegatesTo('model')
    nid = DelegatesTo('model')

    def __eq__(self, other):
        return self.nid == other

    def __ne__(self, other):
        return self.nid != other

    def plot_random(self):
        s_plot = self._make_random_plot()
        spw = SinglePlotWindow(
            plot=s_plot,
            title_text=self._wind_title(),
            vistog=False
            )
        self._show_plot_window(spw)

    def _make_random_plot(self):
        res = self.model.result
        pc_tab = res.scores
        labels = self.model.sub_ds.object_names
        plot = PCScatterPlot(pc_tab, labels, title="Random")
        return plot


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


a_conjoint_view = View(
    Group(
        Group(
            Item('model.name'),
            # Item('model.standardize'),
            orientation='vertical',
            ),
        Item('', springy=True),
        orientation='horizontal',
        ),
    )


if __name__ == '__main__':
    from tests.conftest import make_dsl_mock
    dsl = make_dsl_mock()

    model = AConjointModel(
        nid='abc',
        name='Tore test',
        design=dsl.get_by_id('design'),
        consumer_liking=dsl.get_by_id('odour-flavour_liking'),
        consumer_attributes=dsl.get_by_id('consumerattributes'))


    class AConjointTestHandler(AConjointHandler):
        bt_plot_scores = Button('Plot scores')

        @on_trait_change('bt_plot_scores')
        def _on_bps(self, obj, name, new):
            self.plot_random()

        traits_view = View(
            Group(
                Group(
                    Item('model.name'),
                    orientation='vertical',
                    ),
                Item('', springy=True),
                Group(
                    Item('bt_plot_scores'),
                    ),
                orientation='horizontal',
                ),
            resizable=True,
            )


    controller = AConjointTestHandler(
        model=model)
    with np.errstate(invalid='ignore'):
        # controller.configure_traits()
        controller.model.print_traits()
