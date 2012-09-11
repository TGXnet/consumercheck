"""PCA module for ConsumerCheck application.

Adds statistical methods, user inteface and plots for PCA
"""

# Enthought imports
from traits.api import HasTraits, Instance, Any
from traitsui.api import View, Group, Item, InstanceEditor, TreeEditor, TreeNode

# Local imports
from pca_container_mvc import PCAsHandler, PCAsContainer, pcas_view
from pca_mvc import APCAHandler, PlotLauncher


def dclk_activator(obj):
    fn = obj.func_name
    plot_func = getattr(obj.pca_ref, fn)
    plot_func()


pca_tree = TreeEditor(
    nodes = [
        TreeNode(
            node_for = [PCAsHandler],
            children = '',
            label = '=PCA',
            auto_open = True,
            ),
        TreeNode(
            node_for = [PCAsHandler],
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
            node_for = [APCAHandler],
            children  = 'plot_launchers',
            label = 'name',
#            auto_open=True,
            ),
        TreeNode(
            node_for = [PlotLauncher],
            label = 'node_name',
            on_dclick = dclk_activator,
            ),
        ],
    hide_root=True,
    editable=False,
    selected='selected_obj',
#    auto_open=0,
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
                       Group(
                             Item(name='pca_handler',
                                  editor=pca_tree,
                                  show_label=False),
                             Item(name='pca_handler',
                                  editor=InstanceEditor(view=pcas_view),
                                  style='custom',
                                  show_label=False),
                             orientation='horizontal'
                             ),
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
