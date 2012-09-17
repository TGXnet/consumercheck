"""Prefmap module for ConsumerCheck application

Adds statistical methods, user inteface and plots for Prefmap
"""

# Enthought imports
from traits.api import HasTraits, Instance, Any
from traitsui.api import View, Group, Item, InstanceEditor, TreeEditor, TreeNode

# Local imports
from prefmap_container_mvc import PrefmapsHandler, PrefmapsContainer, prefmaps_view
from prefmap_mvc import APrefmapHandler, WindowLauncher
from plugin_tree_helper import dclk_activator


prefmap_tree = TreeEditor(
    nodes = [
        TreeNode(
            node_for = [PrefmapsHandler],
            children = '',
            label = '=Prefmap',
            auto_open = True,
            ),
        TreeNode(
            node_for = [PrefmapsHandler],
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
            node_for = [APrefmapHandler],
            children = 'window_launchers',
            label = 'name',
            # auto_open = True,
            ),
        TreeNode(
            node_for = [WindowLauncher],
            label = 'node_name',
            on_dclick = dclk_activator,
            ),
        ],
    hide_root = True,
    selected='selected_obj',
    editable = False,
    )



class PrefmapPlugin(HasTraits):
    prefmaps_handler = Instance(PrefmapsHandler)
    selected_obj = Any()

    def __init__(self, mother_ref, **kwargs):
        super(PrefmapPlugin, self).__init__(**kwargs)
        model = PrefmapsContainer(mother_ref=mother_ref)
        self.prefmaps_handler = PrefmapsHandler(model=model)
        self.selected_obj = self.prefmaps_handler


    traits_view = View(
                       Group(
                             Item(name='prefmaps_handler',
                                  editor=prefmap_tree,
                                  show_label=False),
                             Item(name='prefmaps_handler',
                                  editor=InstanceEditor(view=prefmaps_view),
                                  style='custom',
                                  show_label=False),
                             orientation='horizontal',
                             ),
        resizable=True,
        height=400,
        width=600,
        )



if __name__ == '__main__':
    print("Interactive start")
    import numpy as np
    from tests.conftest import TestContainer

    container = TestContainer()
    prefmap_plugin = PrefmapPlugin(mother_ref=container)
    # To force populating selection list
    prefmap_plugin.prefmaps_handler.dsl_changed()
    with np.errstate(invalid='ignore'):
        prefmap_plugin.configure_traits()
