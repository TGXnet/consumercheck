
# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui

#Local imports
from basic_stat_model import BasicStat
from plot_histogram import BoxPlot, HistPlot, StackedHistPlot
from plugin_tree_helper import (WindowLauncher, dclk_activator)
from plugin_base import (ModelController, CalcContainer, PluginController,
                         dummy_view, TestOneNode, make_plugin_view)


class BasicStatController(ModelController):
    '''Controller for one basic statistics object'''
    base_win_launchers = _traits.List(_traits.Instance(WindowLauncher))
    idx_win_launchers = _traits.List(_traits.Instance(WindowLauncher))


    def _name_default(self):
        return self.model.ds.display_name


    def _base_win_launchers_default(self):
        return [WindowLauncher(node_name='Box plot',
                               view_creator=box_plot,
                               owner_ref=self,
                               loop_name='base_win_launchers'),
                WindowLauncher(node_name='Stacked histogram',
                               view_creator=stacked_histogram,
                               owner_ref=self,
                               loop_name='base_win_launchers')]


    def _idx_win_launchers_default(self):
        return self._create_win_launchers()


    @_traits.on_trait_change('model:summary_axis')
    def _axis_altered(self, obj, name, new):
        self.idx_win_launchers = self._create_win_launchers()


    def _create_win_launchers(self):
        if self.model.summary_axis == 'Row-wise':
            nl = self.model.ds.obj_n
        else:
            nl = self.model.ds.var_n

        wll = []
        for n in nl:
            wl = WindowLauncher(owner_ref=self, node_name=str(n),
                                view_creator=plot_histogram,
                                func_parms=tuple([n]),
                                loop_name='idx_win_launchers')
            wll.append(wl)

        return wll


# Plots creators

def box_plot(res):
    plot = BoxPlot(res.summary)
    return plot


def stacked_histogram(res):
    plot = StackedHistPlot(res.hist)
    return plot


def plot_histogram(res, obj_id):
    plot = HistPlot(res.hist, obj_id)
    return plot


no_view = _traitsui.View()


bs_view = _traitsui.View(
    _traitsui.Group(
        # _traitsui.Label('Summary axis:'),
        _traitsui.Item('summary_axis',
                       # editor=_traitsui.EnumEditor(cols=2),
                       # style='custom',
                       show_label=False
                       ),
        label='Summary axis',
        show_border=True,
        orientation='vertical',
        ),
    )


bs_nodes = [
    _traitsui.TreeNode(
        node_for=[BasicStatController],
        label='name',
        children='',
        view=bs_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[BasicStatController],
        label='=Plots for all samples',
        children='base_win_launchers',
        view=bs_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[BasicStatController],
        label='=Single Sample histograms',
        children='idx_win_launchers',
        view=bs_view,
        menu=[]),
    _traitsui.TreeNode(
        node_for=[WindowLauncher],
        label='node_name',
        view=no_view,
        menu=[],
        on_dclick=dclk_activator)
    ]


class BasicStatPluginController(PluginController):

    available_ds = _traits.List()
    selected_ds = _traits.List()

    dummy_model_controller = _traits.Instance(BasicStatController, BasicStatController(BasicStat()))

    # FIXME: I dont know why the initial populating is not handled by
    # _update_selection_list()
    def _available_ds_default(self):
        return self._get_selectable()


    @_traits.on_trait_change('model:dsc:[dsl_changed,ds_changed]',
                             post_init=False)
    def _update_selection_list(self, obj, name, new):
        self.available_ds = self._get_selectable()


    def _get_selectable(self, not_all=True):
        if not_all:
            return self.model.dsc.get_id_name_map('Consumer liking')
        else:
            return self.model.dsc.get_id_name_map()


    @_traits.on_trait_change('selected_ds')
    def _selection_made(self, obj, name, old_value, new_value):
        last = set(old_value)
        new = set(new_value)
        removed = last.difference(new)
        added = new.difference(last)
        if removed:
            self.model.remove(list(removed)[0])
        elif added:
            self._make_calculation(list(added)[0])

        self.update_tree = True


    def _make_calculation(self, ds_id):
        calc_model = BasicStat(id=ds_id, ds=self.model.dsc[ds_id])
        calculation = BasicStatController(calc_model)
        self.model.add(calculation)


selection_view = _traitsui.Group(
    _traitsui.Item('controller.selected_ds',
                   editor=_traitsui.CheckListEditor(
                       name='controller.available_ds'),
                   style='custom',
                   show_label=False,
                   width=200,
                   height=200,
                   ),
    label='Select dataset',
    show_border=True,
    )

bs_plugin_view = make_plugin_view(
    'Basic Statistics', bs_nodes, selection_view, bs_view)


if __name__ == '__main__':
    print("Basic stat GUI test start")
    from tests.conftest import all_dsc, synth_dsc, discrete_ds
    one_branch = False

    if one_branch:
        bs = BasicStat(ds=discrete_ds())
        bsc = BasicStatController(bs)
        tods = TestOneNode(one_model=bsc)
        tods.configure_traits(view=dummy_view(bs_nodes))
    else:
        bsp = CalcContainer(dsc=all_dsc())
        bspc = BasicStatPluginController(bsp)
        bspc.configure_traits(
            view=bs_plugin_view)
