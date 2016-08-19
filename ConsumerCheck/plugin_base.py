'''ConsumerCheck
'''
#-----------------------------------------------------------------------------
#  Copyright (C) 2014 Thomas Graff <thomas.graff@tgxnet.no>
#
#  This file is part of ConsumerCheck.
#
#  ConsumerCheck is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  ConsumerCheck is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ConsumerCheck.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------

# Std. lib imports
import sys

# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui
import chaco.api as _chaco

# Local imports
from dataset import DataSet
from ds_table_view import DSTableViewer
from plot_base import NoPlotControl
from plot_pc_scatter import PCScatterPlot, PCPlotControl
from plot_windows import SinglePlotWindow
from dataset_container import DatasetContainer


class Result(_traits.HasTraits):
    method_name = _traits.Str()
    input_ds_names = _traits.DictStrAny()

    def __init__(self, method_name):
        super(Result, self).__init__(method_name=method_name)


class Model(_traits.HasTraits):
    '''Base class for statistical analysis model'''
    id = _traits.Str()
    res = _traits.Property()
    '''res is an object with the interesting results
    of one model calculation
    '''


class ModelController(_traitsui.Controller):
    '''MVController base class for stat analysis model'''
    id = _traits.DelegatesTo('model')
    name = _traits.Str()
    plot_uis = _traits.List()
    win_handle = _traits.Any()

    # def init(self, info):
    #     super(ModelController, self).init(info)
    #     self.win_handle = info.ui.control

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
        if isinstance(viewable, PCScatterPlot):
            res = self.get_result()
            plot_control = PCPlotControl(viewable)

            win = SinglePlotWindow(
                plot=plot_control,
                res=res,
                view_loop=view_loop,
                )

            self._show_plot_window(win)
        elif isinstance(viewable, _chaco.DataView):
            res = self.get_result()
            plot_control = NoPlotControl(viewable)

            win = SinglePlotWindow(
                plot=plot_control,
                res=res,
                view_loop=view_loop,
                )

            self._show_plot_window(win)
        elif isinstance(viewable, DataSet):
            table = DSTableViewer(viewable)
            table.edit_traits(view=table.get_view(),
                              kind='live',
                              parent=self.win_handle)
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
        # elif sys.platform == 'win32':
        else:
            # FIXME: Investigate more here
            self.plot_uis.append(
                plot_window.edit_traits(parent=self.win_handle, kind='live')
                # plot_window.edit_traits(kind='live')
                )

    def _wind_title(self, res):
        mn = res.method_name
        return "{0} | Overview - ConsumerCheck".format(mn)


class CalcContainer(_traits.HasTraits):
    '''The end

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
    edit_node = _traits.Instance(Model)
    win_handle = _traits.Any()

    def init(self, info):
        self.selected_object = self.model
        self.edit_node = self.model.calculator
        self.win_handle = info.ui.control
        return True

    # @_traits.on_trait_change('selected_object')
    # def _tree_selection_made(self, obj, name, new):
    #     if isinstance(new, ModelController):
    #         self.edit_node = new
    #     elif isinstance(new, WindowLauncher):
    #         self.edit_node = new.owner_ref
    #     else:
    #         self.edit_node = self.dummy_model_controller


# plugin_view
def make_plugin_view(model_name, model_nodes, selection_view, model_view):
    node_label = '=' + model_name
    container_nodes = [
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
            # Left side tree
            _traitsui.Item('controller.model',
                           editor=plugin_tree,
                           show_label=False),
            # Right side
            _traitsui.Group(
                # Upper right side data set selection panel
                selection_view,
                # Lower right side calc settings panel
                _traitsui.Group(
                    _traitsui.Item('controller.edit_node',
                                   editor=_traitsui.InstanceEditor(
                                       view=model_view),
                                   style='custom',
                                   show_label=False),
                    show_border=True,
                    ),
                orientation='vertical',
                ),
            _traitsui.Spring(width=10),
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
