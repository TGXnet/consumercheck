"""PCA module for ConsumerCheck application.

Adds statistical methods, user inteface and plots for PCA
"""

# Enthought imports
from traits.api import HasTraits, Instance, Any
from traitsui.api import View, Item, TreeEditor, TreeNode

# Local imports
from pca_container_mvc import PCAsHandler, PCAsContainer, pcas_view
from pca_mvc import APCAHandler, a_pca_view


def dclk_overview(obj):
    obj.plot_overview()

def dclk_scores(obj):
    obj.plot_scores()

def dclk_loadings(obj):
    obj.plot_loadings()

def dclk_corr_load(obj):
    obj.plot_corr_loading()

def dclk_expl_res_var(obj):
    obj.plot_expl_var()

new_pca_tree = TreeEditor(
    nodes = [
        TreeNode(
            node_for = [PCAsHandler],
            children = '',
            label = '=PCA',
            auto_open = True,
            view = pcas_view,
            ),
        TreeNode(
            node_for = [PCAsHandler],
            children = 'mappings',
            label = 'name',
            view = pcas_view,
            rename = False,
            rename_me = False,
            copy = False,
            delete = False,
            delete_me = False,
            insert = False,
            auto_open = True,
            ),
        TreeNode(
            node_for = [APCAHandler],
            children = '',
            label = 'name',
            # auto_open = True,
            view = a_pca_view,
            ),
        TreeNode(
            node_for = [APCAHandler],
            label = '=Overview',
            on_dclick = dclk_overview,
            view = a_pca_view,
            ),
        TreeNode(
            node_for = [APCAHandler],
            label = '=Scores',
            on_dclick = dclk_scores,
            view = a_pca_view,
            ),
        TreeNode(
            node_for = [APCAHandler],
            label = '=Loadings',
            on_dclick = dclk_loadings,
            view = a_pca_view,
            ),
        TreeNode(
            node_for = [APCAHandler],
            label = '=Correlation loadings',
            on_dclick = dclk_corr_load,
            view = a_pca_view,
            ),
        TreeNode( 
            node_for = [APCAHandler],
            label = '=Explained variance',
            on_dclick = dclk_expl_res_var,
            view = a_pca_view,
            ),
        ],
    selected='selected_obj',
    )



class PCAPlugin(HasTraits):
    pca_handler = Instance(PCAsHandler)
    selected_obj = Any()

    def __init__(self, mother_ref, **kwargs):
        super(PCAPlugin, self).__init__(**kwargs)
        model = PCAsContainer(mother_ref=mother_ref)
        self.pca_handler = PCAsHandler(model=model)
        self.selected_obj = self.pca_handler


    traits_view = View(
        Item(name='pca_handler',
             editor=new_pca_tree,
             show_label=False),
        resizable=True,
        height=200,
        width=800,
        )



if __name__ == '__main__':
    print("Interactive start")
    import numpy as np
    from tests.conftest import TestContainer

    with np.errstate(invalid='ignore'):
        container = TestContainer()
        pca_plugin = PCAPlugin(mother_ref=container)
        pca_plugin.configure_traits()
        