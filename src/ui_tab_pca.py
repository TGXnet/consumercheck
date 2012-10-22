"""PCA module for ConsumerCheck application.

Adds statistical methods, user inteface and plots for PCA
"""
from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'qt4'
# Enthought imports
from traits.api import HasTraits, Instance, Any
from traitsui.api import View, Item, TreeEditor, TreeNode

# Local imports
from pca_container_mvc import PCAsHandler, PCAsContainer, pcas_view
from pca_mvc import APCAHandler, a_pca_view, PlotLauncher, launch_view


def dclk_plot_switch(obj):
    fn = obj.func_name
    plot_func = getattr(obj.pca_ref, fn)
    plot_func()


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
            children  = 'plot_launchers',
            label = 'name',
            view = a_pca_view,
            auto_open=True,
            ),
        TreeNode(
            node_for = [PlotLauncher],
            label = 'node_name',
            on_dclick = dclk_plot_switch,
            view = launch_view,
            ),
        ],
    # hide_root=True,
    selected='selected_obj',
    # auto_open=0,
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
        height=300,
        width=600,
        )



if __name__ == '__main__':
    print("Interactive start")
    import numpy as np
    from tests.conftest import TestContainer

    with np.errstate(invalid='ignore'):
        container = TestContainer()
        pca_plugin = PCAPlugin(mother_ref=container)
        # To force populating selection list
        pca_plugin.pca_handler._ds_changed(None)
        pca_plugin.configure_traits()
