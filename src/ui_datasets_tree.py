
# stdlib imports
import logging

# Enthought imports
from traits.api import HasTraits, Str, List, Instance, on_trait_change
from traitsui.api import Item, View, TreeEditor, Handler, TreeNode
from traitsui.tree_node import TreeNode as TN
# Local imports
from ds_ui import DataSet, ds_list_tab
from importer_main import DND


class Datasets(HasTraits):
    name     = Str( 'FIXME: Datasets default name' )
    imported = List( DataSet )

    def updateList(self, dcObj):
        self.imported = dcObj.get_dataset_list()

    # end Datasets


class DatasetsTreeHandler(Handler):
    name    = Str( 'FIXME: Dette skal ikke vises' )
    collection = Instance( Datasets, Datasets(name = 'Datasets') )


    # Called when some value in object changes
    def setattr(self, info, obj, name, value):
        super(DatasetsTreeHandler, self).setattr(info, obj, name, value)
        logging.info("setattr: %s change to %s", name, value)


    # Called when the the window is created
    def init(self, uiInfo):
        self._updateDatasetsList(uiInfo.object)


    def object_datasets_event_changed(self, uiInfo):
        self._updateDatasetsList(uiInfo.object)


    def _updateDatasetsList(self, obj):
        self.collection.updateList(obj)

# end DatasetTreeHandler


# Create an empty view for objects that have no data to display:
no_view = View()

#
##Gjor saa denne returnerer importert funksjon fra importer_main som gjor nesten det samme som dialog_multi_import per fil i dropped_object
class TreeNode(TN):
    def drop_object(self, object, dropped_object):
        file_path = dropped_object.path
        ds = DND.dnd_import_data(file_path)
        
        object.imported.append(ds)


# Define the TreeEditor used to display the hierarchy:
datasets_tree = TreeEditor(
    nodes = [
        TreeNode( node_for  = [ Datasets ],
                  auto_open = True,
                  children  = '',
                  label     = 'name',
                  view      = View( [ 'name' ] )
                  ),
        TreeNode( node_for  = [ Datasets ],
                  auto_open = True,
                  children  = 'imported',
                  label     = '=Imported',
                  view      = no_view,
                  add       = [ DataSet ],
                  ),
        TreeNode( node_for  = [ DataSet ],
                  auto_open = True,
                  label     = '_ds_name',
                  view      = ds_list_tab,
                  )
        ]
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
    from tests.conftest import make_dsl_mock
    dsl = make_dsl_mock()
    ui = dsl.configure_traits(view=tree_view)
