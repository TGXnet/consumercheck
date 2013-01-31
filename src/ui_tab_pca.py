"""PCA module for ConsumerCheck application.

Adds statistical methods, user inteface and plots for PCA
"""

# Enthought imports
from traits.api import HasTraits, Instance, Any, on_trait_change
from traitsui.api import View, Group, Item, InstanceEditor, TreeEditor, TreeNode

# Local imports
from pca_container_mvc import PCAsHandler, PCAsContainer, pcas_view
from pca_mvc import APCAHandler, WindowLauncher
from plugin_tree_helper import dclk_activator


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
            children  = 'window_launchers',
            label = 'name',
#            auto_open=True,
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
#    auto_open=0,
    )



class PCAPlugin(HasTraits):
    pcas_handler = Instance(PCAsHandler)
    selected_obj = Any()

    def __init__(self, mother_ref, *args, **kwargs):
        super(PCAPlugin, self).__init__(*args, **kwargs)
        model = PCAsContainer(mother_ref=mother_ref)
        self.pcas_handler = PCAsHandler(model=model)
        self.selected_obj = self.pcas_handler


    @on_trait_change('selected_obj')
    def _sel_obj_changed(self, obj, name, new, old):
        print("Selected updated")
        
        obj.pcas_handler.model.selected_pca = new


    traits_view = View(
                       Group(
                             Item(name='pcas_handler',
                                  editor=pca_tree,
                                  show_label=False),
                             Item(name='pcas_handler',
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
    from tests.conftest import plugin_mother_mock

    container = plugin_mother_mock()
    pca_plugin = PCAPlugin(mother_ref=container)
    # To force populating selection list
    pca_plugin.pcas_handler._ds_changed(None)
    with np.errstate(invalid='ignore'):
        pca_plugin.configure_traits()
