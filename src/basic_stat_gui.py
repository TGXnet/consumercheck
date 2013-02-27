
# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui

#Local imports
from basic_stat_model import BasicStat, BasicStatPlugin, extract_summary, extract_histogram
from plugin_tree_helper import WindowLauncher, dclk_activator
from plot_histogram import BoxPlot, HistPlot, StackedHistPlot
from plot_windows import LinePlotWindow


class BasicStatController(_traitsui.Controller):
    '''Controller for one basic statistics object'''
    id = _traits.DelegatesTo('model')
    name = _traits.Str()
    base_win_launchers = _traits.List()
    idx_win_launchers = _traits.List()


    def _name_default(self):
        return self.model.ds.display_name


    def _base_win_launchers_default(self):
        return [WindowLauncher(node_name='Box plot',
                               func_name='box_plot',
                               owner_ref=self),
                WindowLauncher(node_name='Stacked histogram',
                               func_name='stacked_histogram',
                               owner_ref=self)]


    def _idx_win_launchers_default(self):
        return [WindowLauncher(owner_ref=self,
                               node_name=name,
                               func_name='plot_histogram',
                               func_parms=tuple([name]))
                for name in self.model.ds.obj_n]


    def box_plot(self):
        res = self.model.stat_res
        summary = extract_summary(res)
        plot = BoxPlot(summary)
        win = LinePlotWindow(plot=plot, title_text='Hello')
        win.edit_traits()


    def stacked_histogram(self):
        res = self.model.stat_res
        hist = extract_histogram(res)
        plot = StackedHistPlot(hist)
        win = LinePlotWindow(plot=plot, title_text='Hello')
        win.edit_traits()


    def plot_histogram(self, obj_id):
        res = self.model.stat_res
        hist = extract_histogram(res)
        plot = HistPlot(hist, obj_id)
        win = LinePlotWindow(plot=plot, title_text='Hello')
        win.edit_traits()


    def __eq__(self, other):
        return self.id == other


    def __ne__(self, other):
        return self.id != other


no_view = _traitsui.View()


bs_view = _traitsui.View(
    _traitsui.Item('test_dummy'),
    )


bsa_tnode = _traitsui.TreeNode(
    node_for=[BasicStatController],
    label='name',
    children='',
    view=bs_view,
    menu=[])


bsb_tnode = _traitsui.TreeNode(
    node_for=[BasicStatController],
    label='=Base plots',
    children='base_win_launchers',
    view=bs_view,
    menu=[])


bsc_tnode = _traitsui.TreeNode(
    node_for=[BasicStatController],
    label='=Object histogram',
    children='idx_win_launchers',
    view=bs_view,
    menu=[])


wl_tnode = _traitsui.TreeNode(
    node_for=[WindowLauncher],
    label='node_name',
    view=no_view,
    menu=[],
    on_dclick=dclk_activator)


bs_tree = _traitsui.TreeEditor(
    nodes=[bsa_tnode, bsb_tnode, bsc_tnode, wl_tnode],
    )



class BasicStatPluginController(_traitsui.Controller):

    available_ds = _traits.List()
    selected_ds = _traits.List()

    update_tree = _traits.Event()
    selected_object = _traits.Any()
    edit_node = _traits.Instance(BasicStatController)


    @_traits.on_trait_change('selected_object')
    def _tree_selection_made(self, obj, name, new):
        if isinstance(new, BasicStatController):
            self.edit_node = new
        elif isinstance(new, WindowLauncher):
            self.edit_node = new.owner_ref
        else:
            self.edit_node = None


    def _available_ds_default(self):
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
            self._make_task(list(added)[0])

        self.update_tree = True


    def _make_task(self, ds_id):
        tsk = self.model.make_model(ds_id)
        task = BasicStatController(tsk)
        self.model.add(task)


bsp_tnode = _traitsui.TreeNode(
    node_for=[BasicStatPlugin],
    label='=Basic stat',
    children='tasks',
    menu=[],
    )


bs_plugin_tree = _traitsui.TreeEditor(
    nodes=[bsa_tnode, bsb_tnode, bsc_tnode, bsp_tnode, wl_tnode],
    refresh='controller.update_tree',
    selected='controller.selected_object',
    editable=False,
    )


bs_plugin_view = _traitsui.View(
    _traitsui.Group(
        _traitsui.Item('controller.model', editor=bs_plugin_tree, show_label=False),
        _traitsui.Group(
            _traitsui.Group(
                _traitsui.Item('controller.selected_ds',
                               editor=_traitsui.CheckListEditor(name='controller.available_ds'),
                               style='custom',
                               show_label=False,
                               ),
                show_border=True,
                ),
            _traitsui.Group(
                _traitsui.Item('controller.edit_node',
                               editor=_traitsui.InstanceEditor(view=bs_view),
                               style='custom',
                               show_label=False),
                show_border=True,
                ),
            orientation='vertical',
            ),
        orientation='horizontal',
        ),
    resizable=True,
    buttons=['OK'],
    )



class TestOneDsTree(_traits.HasTraits):
    one_ds = _traits.Instance(BasicStatController)

    traits_view = _traitsui.View(
        _traitsui.Item('one_ds', editor=bs_tree, show_label=False),
        resizable=True,
        buttons=['OK'],
        )



if __name__ == '__main__':
    print("Basic stat GUI test started")
    from tests.conftest import synth_dsc, discrete_ds
    one_branch=False

    if one_branch:
        ds = discrete_ds()
        bs = BasicStat(ds=ds)
        bsc = BasicStatController(bs)
        tods = TestOneDsTree(one_ds=bsc)
        tods.configure_traits()
    else:
        dsc = synth_dsc()
        bsp = BasicStatPlugin(dsc=dsc)
        bspc = BasicStatPluginController(bsp)
        bspc.configure_traits(view=bs_plugin_view)
