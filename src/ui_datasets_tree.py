# stdlib imports
import logging

# Enthought imports
from traits.api import HasTraits, Str, List, Instance, Event
from traitsui.api import Item, View, TreeEditor, Handler, TreeNode
from traitsui.tree_node import TreeNode as TN
# Local imports
from dataset import DataSet
from ds_ui import ds_list_tab
from importer_main import DND
from ds_matrix_view import TableViewer

# FIXME: This is dirty
ds_tree_win_handle = None

class Datasets(HasTraits):
    name     = Str( 'FIXME: Datasets default name' )
    imported = List( DataSet )


    def updateList(self, dcObj):
        self.imported = dcObj.get_dataset_list()
    # end Datasets


class DatasetsTreeHandler(Handler):
    name    = Str( 'FIXME: This should not be shown' )
    collection = Instance( Datasets, Datasets(name = 'Datasets') )
    update_tree = Event()

    # Called when some value in object changes
    def setattr(self, info, obj, name, value):
        super(DatasetsTreeHandler, self).setattr(info, obj, name, value)
        logging.info("setattr: %s change to %s", name, value)


    # Called when the the window is created
    def init(self, info):
        global ds_tree_win_handle
        self._updateDatasetsList(info.object)
        ds_tree_win_handle = info.ui.control


    def object_datasets_event_changed(self, uiInfo):
        self._updateDatasetsList(uiInfo.object)
        self.update_tree = True


    def _updateDatasetsList(self, obj):
        self.collection.updateList(obj)
# end DatasetTreeHandler


# Create an empty view for objects that have no data to display:
no_view = View()


#Gjor saa denne returnerer importert funksjon fra importer_main som gjor nesten
# det samme som dialog_multi_import per fil i dropped_object
class TreeNode(TN):
    def drop_object(self, object, dropped_object):
        file_path = dropped_object.path
        ds = DND.dnd_import_data(file_path)
        object.imported.append(ds)


    def get_icon ( self, object, is_expanded ):
        """ Returns custom icon name or the icon for a specified object.
        """
        if not self.allows_children( object ):
            if hasattr(object, 'ds_type'):
                if object.ds_type == 'Design variable':
                    return 'design_variable.ico'
                elif object.ds_type == 'Sensory profiling':
                    return 'sensory_profiling.ico'
                elif object.ds_type == 'Consumer liking':
                    return 'customer_liking.ico'
                elif object.ds_type == 'Consumer characteristics':
                    return 'customer_attributes.ico'
            return self.icon_item
        if is_expanded:
            return self.icon_open
        return self.icon_group


def show_ds_table(obj):
    tv = TableViewer(obj)
    tv.edit_traits(parent=ds_tree_win_handle)


# Define the TreeEditor used to display the hierarchy:
datasets_tree = TreeEditor(
    nodes = [
        TreeNode( node_for  = [ Datasets ],
                  auto_open = True,
                  children  = '',
                  label     = 'name',
                  view      = View( [ 'name' ] ),
                  menu      = False,
                  ),
        TreeNode( node_for  = [ Datasets ],
                  auto_open = True,
                  children  = 'imported',
                  label     = '=Imported',
                  view      = no_view,
                  add       = [ DataSet ],
                  menu      = False,
                  ),
        TreeNode( node_for  = [ DataSet ],
                  auto_open = True,
                  label     = 'display_name',
                  view      = ds_list_tab,
                  icon_path = 'graphics',
                  on_dclick = show_ds_table,
                  menu      = False,
                  ),
        ],
    )


tree_view = View(
    Item( 'handler.collection',
          editor = datasets_tree,
          resizable = True,
          show_label = False
          ),
    title = 'Datasets tree',
    resizable = True,
    width = .4,
    height = .3,
    handler = DatasetsTreeHandler(),
    )


if __name__ == '__main__':
    from tests.conftest import all_dsc
    dsc = all_dsc()
    ui = dsc.configure_traits(view=tree_view)
