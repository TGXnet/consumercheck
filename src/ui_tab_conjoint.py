"""Conjoint module for ConsumerCheck application.

Adds statistical methods, user inteface and plots for Conjoint
"""

# Enthought imports
from traits.api import HasTraits, Instance, Any
from traitsui.api import View, Group, Item, InstanceEditor, TreeEditor, TreeNode

# Local imports
from conjoint_container_mvc import ConjointsHandler, ConjointsContainer, conjoints_view
from conjoint_mvc import AConjointHandler, WindowLauncher
from plugin_tree_helper import dclk_activator


conjoint_tree = TreeEditor(
    nodes = [
        TreeNode(
            node_for = [ConjointsHandler],
            children = '',
            label = '=Conjoint',
            auto_open = True,
            ),
        TreeNode(
            node_for = [ConjointsHandler],
            children = 'mappings',
            label = 'name',
            rename = False,
            rename_me = False,
            copy = False,
            delete = False,
            delete_me = False,
            insert = False,
            auto_open = True,
            ),
        TreeNode(
            node_for = [AConjointHandler],
            children = '',
            label = 'name',
            ),
        TreeNode(
            node_for = [AConjointHandler],
            children = 'table_win_launchers',
            label = '=Tables',
            ),
        TreeNode(
            node_for = [AConjointHandler],
            children = 'me_plot_launchers',
            label = '=Main effects plots',
            ),
        TreeNode(
            node_for = [WindowLauncher],
            label = 'node_name',
            on_dclick = dclk_activator,
            ),
        ],
     hide_root=True,
     editable=False,
     selected='selected_obj',
   )



class ConjointPlugin(HasTraits):
    conjoints_handler = Instance(ConjointsHandler)
    selected_obj = Any()

    def __init__(self, mother_ref, **kwargs):
        super(ConjointPlugin, self).__init__(**kwargs)
        model = ConjointsContainer(mother_ref=mother_ref)
        self.conjoints_handler = ConjointsHandler(model=model)
        self.selected_obj = self.conjoints_handler


    traits_view = View(
                       Group(
                             Item(name='conjoints_handler',
                                  editor=conjoint_tree,
                                  show_label=False),
                             Item(name='conjoints_handler',
                                  editor=InstanceEditor(view=conjoints_view),
                                  style='custom',
                                  show_label=False),
                             orientation='horizontal',
                             ),
        resizable=True,
        height=300,
        width=600,
        )



if __name__ == '__main__':
    print("Interactive start")
    import numpy as np
    from tests.conftest import PluginMotherMock

    container = PluginMotherMock()
    conjoint_plugin = ConjointPlugin(mother_ref=container)
    conjoint_plugin.conjoints_handler._ds_changed(None)
    with np.errstate(invalid='ignore'):
        conjoint_plugin.configure_traits()
