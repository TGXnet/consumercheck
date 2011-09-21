
# FIXME: This is replaced by ui_datasets_tree

#stdlib imports
import logging

# Enthought imports
from enthought.traits.api import Instance, Int, List
from enthought.traits.ui.api import View, Item, Group, HGroup, ListStrEditor, \
     Handler, InstanceEditor


# Local imports
from dataset_collection import DatasetCollection
from dataset import DataSet
from ds_ui import ds_list_tab
# from table_ui import MatrixView


class DsViewHandler(Handler):
    """Handler for dataset view"""

    # list of tuples (internalName, displayName)
    _indexList = List()

    # View list of dataset names
    _nameList    = List()

    # Index to the selected dataset name
    _selIndex    = Int(-1)

    vs = Instance(DataSet, DataSet())


    # Called when some value in object changes
    def setattr(self, info, obj, name, value):
        super(DsViewHandler, self).setattr(info, obj, name, value)
        logging.info("setattr: %s change to %s", name, value)


    def object_ds_name_event_changed(self, uiInfo):
        """Reacts to changes in dataset names"""
        self._buildIndexList(uiInfo.object)
        logging.info("ds_name_event_changed: activated")


    def object_datasets_event_changed(self, uiInfo):
        if uiInfo.initialized:
            self._buildIndexList(uiInfo.object)
            self._activateLastAddedDataset()
        logging.info("dataDictContentChange_changed: activated")


    def _activateLastAddedDataset(self):
        self._selIndex = -1
        lastIndex = len(self._indexList) - 1
        self._selIndex = lastIndex


    # Generate indexList
    def _buildIndexList(self, datasetCollectionObject):
        self._indexList = datasetCollectionObject.id_name_list
        self._nameList = []
        for kName, dName in self._indexList:
            self._nameList.append(dName)


    # Also called on window creation
    def handler__selIndex_changed(self, uiInfo):
        if (uiInfo.initialized) and (uiInfo.handler._selIndex >= 0):
            name = self._indexToName(uiInfo.handler._selIndex)
            self.vs = uiInfo.object.get_by_id(name)
            logging.info(
                "selIndex_changed: index is %s and selected dataset is %s",
                uiInfo.handler._selIndex, name)


    def _indexToName(self, index):
        """Return dataset name from list index"""
        return self._indexList[index][0]


    # FIXME: Not in use yet!!
    # And shoud be a part of dataset handler
    def handler_viewTable_changed(self, uiInfo):
        """Activated show table."""
        if uiInfo.initialized:
            #mv = MatrixView(theDataset=uiInfo.objects.vs)
            # FIXME: Detta kan vel ikke funke
            mv = MatrixView()
            mv.edit_traits(kind='modal')
            logging.info("viewTable_changed: activated")

    # end DsViewHandler


dslist_view_item = Item(
    'handler._nameList',
    editor = ListStrEditor(
        editable=False,
        multi_select=False,
        activated_index='_selIndex',
        selected_index='_selIndex',
        ),
    height = 75,
    width = 200
    )


dataset_view_item = Item(
    'handler.vs',
    editor=InstanceEditor(view=ds_list_tab,),
    style='custom',
    ),


datasets_view = View(
    HGroup(
        Group(
            dslist_view_item,
            label = 'Collection list',
            show_border = True,
            ), # end Collection list group
        Group(
            dataset_view_item,
            label = 'Dataset',
            show_border = True,
            ), # end Dataset frame
        orientation = 'horizontal',
        # label='Datasets',
        ),
    handler = DsViewHandler,
    )


if __name__ == '__main__':
    from tests.tools import make_dsl_mock
    dsl = make_dsl_mock()
    ui = dsl.configure_traits(view=datasets_view)
