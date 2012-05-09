

# stdlib imports
import sys

# Enthought imports
from traits.api import (HasTraits, Instance, Str, List, Button, DelegatesTo,
                        PrototypedFrom, Property, on_trait_change)
from traitsui.api import View, Group, Item, ModelView, RangeEditor
from enable.api import BaseTool
import numpy as np

# Local imports
from nipals import PCA
from dataset import DataSet
from plot_pc_scatter import PCScatterPlot
from plot_windows import SinglePlotWindow
from ds_slicer_view import ds_obj_slicer_view, ds_var_slicer_view


#Double click tool
class DClickTool(BaseTool):
    plot_dict = {}
    #List that holds the function names
    func_list = ['plot_random','plot_fixed', 'plot_means']
    #Triggered on double click
    def normal_left_dclick(self,event):
        self._build_plot_list()
        call_function = getattr(self.ref, self.plot_dict[self.component.title])()
    #Builds a dictionary that holds the function names, based on func_list, with the window title as key
    def _build_plot_list(self):
        for e,i in enumerate(self.component.container.plot_components):
            self.plot_dict[i.title] = self.func_list[e]


class AConjointModel(HasTraits):
    """Represent the Conjoint model of a dataset."""
    name = Str()
    plot_type = Str()
    nid = Str()
    # Shoud be Instance(PrefmapsContainer)
    # but who comes first?
    mother_ref = Instance(HasTraits)
    ds = DataSet()
    sub_ds = DataSet()
    # FIXME: To be replaced by groups

    # depends_on
    result = Property()




class AConjointHandler(ModelView):
    plot_uis = List()
    name = DelegatesTo('model')
    nid = DelegatesTo('model')


    def __eq__(self, other):
        return self.nid == other

    def __ne__(self, other):
        return self.nid != other

    def plot_random(self):
        self.model.plot_type = 'Random Plot'
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

    def plot_fixed(self):
        self.model.plot_type = 'Fixed Plot'
        l_plot = self._make_fixed_plot()
        spw = SinglePlotWindow(
            plot=l_plot,
            title_text=self._wind_title(),
            vistog=False
            )
        self._show_plot_window(spw)

    def _make_fixed_plot(self):
        res = self.model.result
        pc_tab = res.loadings
        labels = self.model.sub_ds.variable_names
        plot = PCScatterPlot(pc_tab, labels, title="Fixed")
        return plot
    
    def plot_means(self):
        self.model.plot_type = 'Means Plot'
        l_plot = self._make_means_plot()
        spw = SinglePlotWindow(
            plot=l_plot,
            title_text=self._wind_title(),
            vistog=False
            )
        self._show_plot_window(spw)

    def _make_means_plot(self):
        res = self.model.result
        pc_tab = res.loadings
        labels = self.model.sub_ds.variable_names
        plot = PCScatterPlot(pc_tab, labels, title="Means")
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
        dstype = self.model.plot_type
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
    # Things to fix for testing
    # mother_ref: standardize, pc_to_calc
    from traits.api import Bool, Enum
    from tests.conftest import make_ds_mock
    ds = make_ds_mock()

    class MocMother(HasTraits):
        standardize = Bool(True)
        pc_to_calc = Enum(2,3,4,5,6)

    moc_mother = MocMother()
    
    model = AConjointModel(
        name='Tore test',
        ds=ds,
        mother_ref=moc_mother)

    class AConjointTestHandler(AConjointHandler):
        bt_plot_overview = Button('Plot overview')
        bt_plot_scores = Button('Plot scores')
        bt_plot_loadings = Button('Plot loadings')
        bt_plot_corr_loadings = Button('Plot corr loadings')
        bt_plot_expl_var = Button('Plot explainded variance')

        @on_trait_change('bt_plot_overview')
        def _on_bpo(self, obj, name, new):
            self.plot_overview()

        @on_trait_change('bt_plot_scores')
        def _on_bps(self, obj, name, new):
            self.plot_scores()

        @on_trait_change('bt_plot_loadings')
        def _on_bpl(self, obj, name, new):
            self.plot_loadings()

        @on_trait_change('bt_plot_corr_loadings')
        def _on_bpcl(self, obj, name, new):
            self.plot_corr_loading()

        @on_trait_change('bt_plot_expl_var')
        def _on_bpev(self, obj, name, new):
            self.plot_expl_var()

        traits_view = View(
            Group(
                Group(
                    Item('model.name'),
                    # Item('model.standardize'),
                    Item('model.pc_to_calc'),
                    Item('show_sel_obj',
                         show_label=False),
                    Item('show_sel_var',
                         show_label=False),
                    orientation='vertical',
                    ),
                Item('', springy=True),
                Group(
                    Item('bt_plot_overview'),
                    Item('bt_plot_scores'),
                    Item('bt_plot_loadings'),
                    Item('bt_plot_corr_loadings'),
                    Item('bt_plot_expl_var'),
                    ),
                orientation='horizontal',
                ),
            resizable=True,
            )


    controller = AConjointTestHandler(
        model=model)
    with np.errstate(invalid='ignore'):
        controller.configure_traits()
