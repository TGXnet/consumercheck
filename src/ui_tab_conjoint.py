"""Conjoint module for ConsumerCheck application.

Adds statistical methods, user inteface and plots for Conjoint
"""

# Enthought imports
from traits.api import HasTraits, Instance, Any
from traitsui.api import View, Item, TreeEditor, TreeNode

# Local imports
from conjoint_container_mvc import ConjointsHandler, ConjointsContainer, conjoints_view
from conjoint_mvc import AConjointHandler, WindowLauncher, a_conjoint_view
from plugin_tree_helper import dclk_activator


no_view = View()


new_conjoint_tree = TreeEditor(
    nodes = [
        TreeNode(
            node_for = [ConjointsHandler],
            children = '',
            label = '=Conjoint',
            auto_open = True,
            view = conjoints_view,
            ),
        TreeNode(
            node_for = [ConjointsHandler],
            children = 'mappings',
            label = 'name',
            view = conjoints_view,
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
            # auto_open = True,
            view = a_conjoint_view,
            ),
        TreeNode(
            node_for = [AConjointHandler],
            children = 'table_win_launchers',
            label = '=Tables',
            view = a_conjoint_view,
            auto_open = True,
            ),
        TreeNode(
            node_for = [AConjointHandler],
            children = 'me_plot_launchers',
            label = '=Main effects plots',
            view = a_conjoint_view,
            auto_open = True,
            ),
        ## TreeNode(
        ##     node_for = [AConjointHandler],
        ##     children = 'int_plot_launchers',
        ##     label = '=Interaction plots',
        ##     view = a_conjoint_view,
        ##     auto_open = True,
        ##     ),
        TreeNode(
            node_for = [WindowLauncher],
            label = 'node_name',
            on_dclick = dclk_activator,
            view = no_view,
            ),
        ],
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
        Item(name='conjoints_handler',
             editor=new_conjoint_tree,
             show_label=False),
        resizable=True,
        height=300,
        width=600,
        )



if __name__ == '__main__':
    print("Interactive start")
    import numpy as np
    from tests.conftest import TestContainer

    container = TestContainer()
    conjoint_plugin = ConjointPlugin(mother_ref=container)
    conjoint_plugin.conjoints_handler._ds_changed(None)
    with np.errstate(invalid='ignore'):
        conjoint_plugin.configure_traits()
