
# Std. lib imports
import sys

# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui
import chaco.api as _chaco

# Local imports
from dataset import DataSet
from ds_table_view import DSTableViewer
from plot_windows import SinglePlotWindow, PCPlotWindow
from dataset_container import DatasetContainer
from plugin_tree_helper import WindowLauncher



class Result(_traits.HasTraits):
    method_name = _traits.Str('Basic stat')

    def __init__(self, method_name):
        super(Result, self).__init__(method_name=method_name)


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


    def get_result(self):
        return self.model.res


    def open_window(self, viewable, view_loop):
        """Expected viewable is by now:
          + Plot subtype
          + DataSet type
        """
        if isinstance(viewable, _chaco.DataView):
            res = self.get_result()

            win = PCPlotWindow(
                plot=viewable,
                res=res,
                view_loop=view_loop,
                title_text=self._wind_title(res),
                vistog=False
                )

            self._show_plot_window(win)
        elif isinstance(viewable, DataSet):
            table = DSTableViewer(viewable)
            table.edit_traits(view=table.get_view(), kind='live', parent=self.win_handle)
        else:
            raise NotImplementedError("Do not know how to open this")


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
            raise NotImplementedError(
                "Not implemented for this platform: {0}".format(sys.platform))


    def _wind_title(self, res):
        ds_name = self.model.ds.display_name
        mn = res.method_name
        return "{0} | {1} - ConsumerCheck".format(ds_name, mn)



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


    def init(self, info):
        self.selected_object = self.model


    @_traits.on_trait_change('selected_object')
    def _tree_selection_made(self, obj, name, new):
        if isinstance(new, ModelController):
            self.edit_node = new
        elif isinstance(new, WindowLauncher):
            self.edit_node = new.owner_ref
        else:
            self.edit_node = self.dummy_model_controller


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
            _traitsui.Spring(width=30),
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
