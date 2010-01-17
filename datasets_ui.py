# coding=utf-8

# Enthought imports
from enthought.traits.api \
    import HasTraits, Instance, DelegatesTo, Button, Str, Int,\
    File, Bool, List, on_trait_change
from enthought.traits.ui.api \
    import View, Item, Group, ListStrEditor, Handler, FileEditor,\
    InstanceEditor, ButtonEditor
from enthought.traits.ui.menu \
    import Action, Menu, MenuBar



# Local imports
from dataset_collection import DatasetCollection
from dataset import DataSet
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

    # Create an action that open dialog for dataimport
    setImport = Action(name = 'Add &Dataset',
                       action = 'importDataset')
    # Create an action that exits the application.
    exitAction = Action(name='E&xit',
                        action='_on_close')

    # Test tab for PCA
    _pca = Str('PCA comming here')

    # Button to show dataset table
    _viewTable = Button(label = 'Show table')

    # View Set
    # vs = Instance(DataSet, DataSet())
    vs = Instance(DataSet)

    pca_view_group = Group(
        Item('handler._pca'),
        label='PCA analysis',
        )

    dataset_view_item = Item('handler._nameList',
                             editor = ListStrEditor(
            editable=False,
            multi_select=False,
            activated_index='_selIndex',
            selected_index='_selIndex',
            ),
                             height = 75,
                             width = 200
                             )



    datasets_view_group = Group(
        Group(
            dataset_view_item,
            Item('handler._viewTable',
                 editor = ButtonEditor() ),
            label='Collection list',
            show_border=True
            ), # end Collection list group
        Group(
            Item('handler.vs',
                 editor=InstanceEditor(
                    view=View(
                        # FIXME: Check if this directly should reflect members in dataset class
                        Item(name = '_displayName'),
                        Item(name = '_datasetType'),
                        ),
                    ),
                 style='custom',
                 ),
            label='Dataset',
            show_border=True,
            ), # end Dataset frame
        orientation = 'horizontal',
        label='Datasets'
        )



    # The dataset view
    traits_ui_view = View(
        Group(
            datasets_view_group,
            pca_view_group,
            layout='tabbed'
            ), # end UI tabs group
        width = 700, height = 250,
        resizable = True,
        title = 'Consumer Check',
        menubar = MenuBar(
            Menu(setImport, exitAction,
                 name = '&File'
                 )
            ),
        )



    # Called when some value in object changes
    def setattr(self, info, object, name, value):
        super(DsViewHandler, self).setattr(info, object, name, value)
        print 'DsViewHandler:setattr:', name, 'to', value


    # generateIndexList
    def object__updated_changed(self, info):
        """Reacts to changes in dataset names"""
        # Ask te dc to return a list of tuples
        print "DsViewHandler: Updated changed"


    def object__dataDict_changed(self, info):
        """Reacts to changes in dataset"""
        print "DsViewHandler: dataDict changed"


    # Also called on window creation
    def handler__selIndex_changed(self, info):
        if not info.initialized:
            # Inital assign view to dummy dataset
            self.vs = DataSet()
            print "DsViewHandler:selIndex_changed"
        else:
            if info.handler._selIndex >= 0:
                name = self.indexToName(info.handler._selIndex)
                self.vs = info.object.retriveDatasetByName(name)
                print "DsViewHandler:selIndex_changed to", info.handler._selIndex


    def indexToName(self, index):
        """Return dataset name from list index"""
        return self._indexList[index][0]


    # Event handler signature
    # extended_traitname_changed(info)
    # default context is object
    def importDataset(self, uiInfo):
        """Action called when activating importing of new dataset"""
        fi = FileImport()
        fiUi = fi.edit_traits(kind='modal')
        if fiUi.result:
            # FIXME: Handle Cancel/abort
            ds = DataSet()
            ds.importDataset(fi.fileName, fi.colHead)
            uiInfo.object.addDataset(ds)
            self.updateIndexList(uiInfo)
            print "DsViewHandler:importDataset", ds._matrix
        else:
            print "DsViewHandler:import aborted"


    def handler_viewTable_changed(self, uiInfo):
        """Activated show table."""
        if not uiInfo.initialized:
            pass
        else:
            #mv = MatrixView(theDataset=uiInfo.objects.vs)
            # FIXME: Detta kan vel ikke funke
            mv = MatrixView()
            mv.edit_traits(kind='modal')
            print "DsViewHandler:Table view activated"


    def updateIndexList(self, uiInfo):
        """Regenerate the indexLists"""
        self._indexList = []
        self._nameList = []
        for sn, so in uiInfo.object._dataDict.iteritems():
            tu = (sn, so._displayName)
            self._indexList.append(tu)
            self._nameList.append(so._displayName)




    # end DsViewHandler




if __name__ == '__main__':
    """Run the application. """
    from enthought.pyface.api import GUI

    dc = DatasetCollection()
    ui = DsViewHandler().edit_traits( context = dc )
    GUI().start_event_loop()
