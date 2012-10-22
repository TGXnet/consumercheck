"""Prefmap module for ConsumerCheck application

Adds statistical methods, user inteface and plots for Prefmap
"""
from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'qt4'
# Enthought imports
from traits.api import HasTraits, Instance, Any
from traitsui.api import View, Item, TreeEditor, TreeNode

# Local imports
from prefmap_container_mvc import PrefmapsHandler, PrefmapsContainer, prefmaps_view
from prefmap_mvc import APrefmapHandler, a_prefmap_view


def dclk_overview(obj):
    obj.plot_overview()

def dclk_scores(obj):
    obj.plot_scores()

def dclk_corr_load(obj):
    obj.plot_corr_loading()

def dclk_expl_var_x(obj):
    obj.plot_expl_var_x()

def dclk_expl_var_y(obj):
    obj.plot_expl_var_y()

def dclk_loadings_x(obj):
    obj.plot_loadings_x()

def dclk_loadings_y(obj):
    obj.plot_loadings_y()


new_prefmap_tree = TreeEditor(
    nodes = [
        TreeNode(
            node_for = [PrefmapsHandler],
            children = '',
            label = '=Prefmap',
            auto_open = True,
            view = prefmaps_view,
            ),
        TreeNode(
            node_for = [PrefmapsHandler],
            children = 'mappings',
            label = 'name',
            view = prefmaps_view,
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
            children = '',
            label = 'name',
            # auto_open = True,
            view = a_prefmap_view,
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            label = '=Overview plot',
            on_dclick = dclk_overview,
            view = a_prefmap_view,
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            label = '=Scores plot',
            on_dclick = dclk_scores,
            view = a_prefmap_view,
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            label = '=X ~ Y correlation loadings plot',
            on_dclick = dclk_corr_load,
            view = a_prefmap_view,
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            label = '=Explained var X plot',
            on_dclick = dclk_expl_var_x,
            view = a_prefmap_view,
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            label = '=Explained var Y plot',
            on_dclick = dclk_expl_var_y,
            view = a_prefmap_view,
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            label = '=X loadings plot',
            on_dclick = dclk_loadings_x,
            view = a_prefmap_view,
            ),
        TreeNode(
            node_for = [APrefmapHandler],
            label = '=Y loadings plot',
            on_dclick = dclk_loadings_y,
            view = a_prefmap_view,
            ),
        ],
    # hide_root = True,
    selected='selected_obj',
    # editable = False,
    # auto_open = 2,
    )



class PrefmapPlugin(HasTraits):
    prefmap_handler = Instance(PrefmapsHandler)
    selected_obj = Any()

    def __init__(self, mother_ref, **kwargs):
        super(PrefmapPlugin, self).__init__(**kwargs)
        model = PrefmapsContainer(mother_ref=mother_ref)
        self.prefmap_handler = PrefmapsHandler(model=model)
        self.selected_obj = self.prefmap_handler


    traits_view = View(
        Item(name='prefmap_handler',
             editor=new_prefmap_tree,
             show_label=False),
        resizable=True,
        height=400,
        width=600,
        )



if __name__ == '__main__':
    print("Interactive start")
    import numpy as np
    from tests.conftest import TestContainer

    with np.errstate(invalid='ignore'):
        container = TestContainer()
        prefmap_plugin = PrefmapPlugin(mother_ref=container)
        prefmap_plugin.configure_traits()
