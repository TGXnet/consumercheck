"""Conjoint module for ConsumerCheck application.

Adds statistical methods, user inteface and plots for Conjoint
"""

# Enthought imports
from traits.api import HasTraits, Instance, Any
from traitsui.api import View, Item, TreeEditor, TreeNode

# Local imports
from conjoint_container_mvc import ConjointsHandler, ConjointsContainer, conjoints_view
from conjoint_mvc import AConjointHandler, a_conjoint_view


def dclk_random(obj):
    obj.plot_random()

def dclk_fixed(obj):
    obj.plot_fixed()

def dclk_means(obj):
    obj.plot_means()


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
            label = '=Random',
            on_dclick = dclk_random,
            view = a_conjoint_view,
            ),
        TreeNode(
            node_for = [AConjointHandler],
            label = '=Fixed',
            on_dclick = dclk_fixed,
            view = a_conjoint_view,
            ),
        TreeNode(
            node_for = [AConjointHandler],
            label = '=Means',
            on_dclick = dclk_means,
            view = a_conjoint_view,
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

    with np.errstate(invalid='ignore'):
        container = TestContainer()
        conjoint_plugin = ConjointPlugin(mother_ref=container)
        conjoint_plugin.configure_traits()
        conjoint_plugin.conjoints_handler._ds_changed(None)
