# -*- coding: utf-8 -*-

# stdlib imports
import logging

# Enthought imports
from enthought.traits.api \
    import HasTraits, Str, Regex, List, Dict, Instance
from enthought.traits.ui.api \
    import Item, View, TreeEditor, TreeNode, Handler

# Local imports
from ds_ui import DataSet, ds_list_tab


class Datasets ( HasTraits ):
    """ Defines a company with datasets and employees. """
    name     = Str( 'FIXME: Datasets default name' )
    imported = List( DataSet )

    def updateList(self, dcObj):
        self.imported = dcObj.getDatasetList()

# end Datasets


class DatasetsTreeHandler(Handler):
    name    = Str( 'FIXME: Dette skal ikke vises' )
    collection = Instance( Datasets, Datasets(name = 'Datasets') )


    # Called when some value in object changes
    def setattr(self, info, object, name, value):
        super(DsViewHandler, self).setattr(info, object, name, value)
        logging.info("setattr: %s change to %s", name, value)


    # Called when the the window is created
    def init(self, uiInfo):
        self._updateDatasetsList(uiInfo)


    def object_dataDictContentChanged_changed(self, uiInfo):
        self._updateDatasetsList(uiInfo)


    def _updateDatasetsList(self, uiInfo):
        self.collection.updateList(uiInfo.object)

# end DatasetTreeHandler


# Create an empty view for objects that have no data to display:
no_view = View()


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
                  label     = '_displayName',
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
