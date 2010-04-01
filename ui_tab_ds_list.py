# coding=utf-8

#stdlib imports
import logging

# Enthought imports
from enthought.traits.api \
    import HasTraits, Instance, DelegatesTo, Button, Str, Int,\
    File, Bool, List, on_trait_change
from enthought.traits.ui.api \
    import View, Item, Group, HGroup, ListStrEditor, Handler, FileEditor,\
    InstanceEditor, ButtonEditor
from enthought.traits.ui.menu \
    import Action, Menu, MenuBar



# Local imports
from dataset_collection import DatasetCollection
from ds import DataSet
from ds_ui import ds_list_tab
from table_ui import MatrixView
from file_import_ui import FileImport


class DsViewHandler(Handler):
    """Handler for dataset view"""

    # list of tuples (internalName, displayName)
    _indexList = List()
    # View list of dataset names
    _nameList    = List()
    # Index to the selected dataset name
    _selIndex    = Int(0)

    # Button to show dataset table
    _updateList = Button(label = 'Update List')

    vs = Instance(DataSet, DataSet())


    # Called when some value in object changes
    def setattr(self, info, object, name, value):
        super(DsViewHandler, self).setattr(info, object, name, value)
        logging.info("setattr: %s change to %s", name, value)


    # generateIndexList
    def object__updated_changed(self, info):
        """Reacts to changes in dataset names"""
        self.handler__updateList_changed(info)
        logging.info("update_changed: activated")


    def object__dataDict_changed(self, info):
        """Reacts to changes in dataset"""
        logging.info("dataDict_changed: dataDict changed")


    # Also called on window creation
    def handler__selIndex_changed(self, info):
        if not info.initialized:
            # Inital assign view to dummy dataset
            logging.info("selIndex_changed: initialized")
        else:
            if info.handler._selIndex >= 0:
                name = self.indexToName(info.handler._selIndex)
                self.vs = info.object.retriveDatasetByName(name)
                logging.info("selIndex_changed: index is %s and selected dataset is %s", info.handler._selIndex, name)


    def indexToName(self, index):
        """Return dataset name from list index"""
        return self._indexList[index][0]


    def handler__updateList_changed(self, uiInfo):
        """Regenerate the indexLists"""
        self._indexList = []
        self._nameList = []
        for sn, so in uiInfo.object._dataDict.iteritems():
            tu = (sn, so._displayName)
            self._indexList.append(tu)
            self._nameList.append(so._displayName)


    def handler_viewTable_changed(self, uiInfo):
        """Activated show table."""
        if not uiInfo.initialized:
            pass
        else:
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
            Item('handler._updateList',),
            label='Collection list',
            show_border=True
            ), # end Collection list group
        Group(
            dataset_view_item,
            label='Dataset',
            show_border=True,
            ), # end Dataset frame
        orientation = 'horizontal',
        # label='Datasets',
    ),
    handler = DsViewHandler,
    )


if __name__ == '__main__':
    """Run the application. """
    ds1 = DataSet(_internalName = 'test1', _displayName = 'Test 1')
    ds1.importDataset('./testdata/Ost.txt', True)
    ds1._displayName = 'Oste test'
    ds2 = DataSet(_internalName = 'test2', _displayName = 'Test 2')
    dc = DatasetCollection()
    dc.addDataset(ds1)
    dc.addDataset(ds2)
    ui = dc.edit_traits(datasets_view)
