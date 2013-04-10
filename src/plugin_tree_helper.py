'''Plugin infrastructure.

Base classes for a statistics method plugin.

Created on Sep 11, 2012

@author: Thomas Graff <graff.thomas@gmail.com>
'''
# Std. lib imports
import sys

# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui

# Local imports
from dataset_container import DatasetContainer


def dclk_activator(obj):
    open_win_func = obj.view_creator
    # open_win_func = getattr(obj.owner_ref, fn)
    if len(obj.func_parms) < 1:
        view = open_win_func(obj.owner_ref.model.res)
    else:
        view = open_win_func(obj.owner_ref.model.res, *obj.func_parms)
    obj.owner_ref.open_window(view)


class WindowLauncher(_traits.HasTraits):
    node_name = _traits.Str()
    # FIXME: Deprecated by view_creator
    func_name = _traits.Str()
    view_creator = _traits.Callable()
    # FIXME: Should not be nessesary for view navigator
    owner_ref = _traits.WeakRef()
    # FIXME: Rename to creator_parms
    func_parms = _traits.Tuple()



class ViewNavigator(_traits.HasTraits):
    view_loop = _traits.List(WindowLauncher)
    current_idx = _traits.Int(0)
    res = _traits.WeakRef()


    def show_next(self):
        if self.current_idx < len(self.view_loop)-1:
            self.current_idx += 1
        else:
            self.current_idx = 0
        vc = self.view_loop[self.current_idx]
        # return vc.view_creator(self.res, vc.func_parms)
        return vc.view_creator(self.res)


    def show_previous(self):
        if self.current_idx > 0:
            self.current_idx -= 1
        else:
            self.current_idx = len(self.view_loop) - 1
        vc = self.view_loop[self.current_idx]
        return vc.view_creator(self.res)



class Model(_traits.HasTraits):
    '''Base class for statistical analysis model'''
    id = _traits.Str()
    res = _traits.Property()
    '''res is an object with the interesting results of one model calculation'''


class ModelController(_traitsui.Controller):
    '''MVController base class for stat analysis model'''
    id = _traits.DelegatesTo('model')
    name = _traits.Str()
    plot_uis = _traits.List()
    win_handle = _traits.Any()


    def init(self, info):
        self.win_handle = info.ui.control


    def _name_default(self):
        raise NotImplementedError('_name_default')


    def __eq__(self, other):
        return self.id == other


    def __ne__(self, other):
        return self.id != other


    def _show_plot_window(self, plot_window):
        # FIXME: Setting parent forcing main ui to stay behind plot windows
        # plot_window.mother_ref = self
        if sys.platform == 'linux2':
            self.plot_uis.append(
                # plot_window.edit_traits(parent=self.win_handle, kind='live')
                plot_window.edit_traits(kind='live')
                )
        elif sys.platform == 'win32':
            # FIXME: Investigate more here
            self.plot_uis.append(
                plot_window.edit_traits(parent=self.win_handle, kind='live')
                # plot_window.edit_traits(kind='live')
                )
        else:
            raise NotImplementedError("Not implemented for this platform: ".format(sys.platform))



class CalcContainer(_traits.HasTraits):
    '''

    '''
    dsc = _traits.Instance(DatasetContainer)
    calculations = _traits.List(_traits.HasTraits)


    def add(self, calc):
        self.calculations.append(calc)


    def remove(self, calc_id):
        del(self.calculations[self.calculations.index(calc_id)])



class PluginController(_traitsui.Controller):
    update_tree = _traits.Event()
    selected_object = _traits.Any()
    edit_node = _traits.Instance(ModelController)


    @_traits.on_trait_change('selected_object')
    def _tree_selection_made(self, obj, name, new):
        if isinstance(new, ModelController):
            self.edit_node = new
        elif isinstance(new, WindowLauncher):
            self.edit_node = new.owner_ref
        else:
            self.edit_node = None


# plugin_view
def make_plugin_view(model_name, model_nodes, selection_view, model_view):
    node_label = '=' + model_name
    container_nodes=[
        _traitsui.TreeNode(
            node_for=[CalcContainer],
            label=node_label,
            children='',
            auto_open=True,
            menu=[],
            ),
        _traitsui.TreeNode(
            node_for=[CalcContainer],
            label=node_label,
            children='calculations',
            auto_open=True,
            menu=[],
            ),
        ]

    plugin_tree = _traitsui.TreeEditor(
        nodes=container_nodes+model_nodes,
        # refresh='controller.update_tree',
        selected='controller.selected_object',
        editable=False,
        hide_root=True,
        )

    plugin_view = _traitsui.View(
        _traitsui.Group(
            _traitsui.Item('controller.model', editor=plugin_tree, show_label=False),
            _traitsui.Group(
                selection_view,
                _traitsui.Group(
                    _traitsui.Item('controller.edit_node',
                                   editor=_traitsui.InstanceEditor(view=model_view),
                                   style='custom',
                                   show_label=False),
                    show_border=True,
                    ),
                orientation='vertical',
                ),
            _traitsui.Spring(width=230),
            orientation='horizontal',
            ),
        resizable=True,
        buttons=['OK'],
        )

    return plugin_view




class TestOneNode(_traits.HasTraits):
    one_model = _traits.Instance(ModelController)


def dummy_view(model_nodes):

    model_tree = _traitsui.TreeEditor(nodes=model_nodes)

    view = _traitsui.View(
        _traitsui.Item('one_model', editor=model_tree, show_label=False),
        resizable=True,
        buttons=['OK'],
        )

    return view
