# coding=utf-8

# Enthought imports
from enthought.traits.api \
    import HasTraits, Instance, DelegatesTo, Button, Str, File, Bool
from enthought.traits.ui.api \
    import View, Item, Group, ListStrEditor, Handler, FileEditor, InstanceEditor
from enthought.traits.ui.menu \
    import Action, Menu, MenuBar


# Local imports
from dataset_collection import DatasetCollection
from dataset import DataSet


class DsViewHandler(Handler):
    """Handler for dataset view"""

#    def setattr(self, info, object, name, value):
#        Handler.setattr(self, info, object, name, value)
#        print 'Change:', name, 'to', value



    # Also called on window creation
    def object__selIndex_changed(self, info):
        if not info.initialized:
            # Inital assign view to dummy dataset
            # info.object.vs = DataSet()
            pass
        else:
            if info.object._selIndex >= 0:
                info.object.vs = info.object.vc.retriveDatasetByIndex(info.object._selIndex)
                print "Vs changed to", info.object.vs


    # Event handler signature
    # extended_traitname_changed(info)
    # default context is object
    def importDataset(self, uiInfo):
        """Action called when activating importing of new dataset"""
        fi = FileImport()
        fi.configure_traits(kind='modal')
        ds = DataSet()
        ds.importDataset(fi.fileName, fi.colHead)
        uiInfo.object.vc.addDataset(ds)


    def object__delSet_changed(self, uiInfo):
        """Action called when activating removing of selected dataset"""
        print "Remove dataset pressed"



class FileImport(HasTraits):
    """File import dialog"""
    fileName = File()
    colHead = Bool(True)



class DatasetsView(HasTraits):
    """Tree like view for dataset collection and panel for each dataset. """

    # View Collection
    vc = Instance(DatasetCollection)
    # View Set
    vs = Instance(DataSet, DataSet())

    # Delegations
    # Collection
    _dispNameIndex      = DelegatesTo('vc')
    _selIndex           = DelegatesTo('vc')
    _addSet             = Button(label='Import')
    _delSet             = Button(label='Remove')

    
    setImport = Action(name = 'Add &Dataset',
                       action = 'importDataset')
    # Create an action that exits the application.
    exitAction = Action(name='E&xit',
                        action='_on_close')


    # Data set
    _displayName        = DelegatesTo('vs')
    _datasetType        = DelegatesTo('vs')
    _matrixColumnHeader = DelegatesTo('vs')
    _isCalculated       = DelegatesTo('vs')
    _isActive           = DelegatesTo('vs')

    # Test tab for PCA
    _pca = Str('PCA comming here')


    traits_ui_view = View(
        Group(
            Group(
                Group(
                    Item('_dispNameIndex',
                         editor = ListStrEditor(
                            editable=False,
                            multi_select=False,
                            activated_index='_selIndex',
                            selected_index='_selIndex',
                            ),
                         height = 75,
                         width = 200
                         ),
                    Item('_addSet'),
                    Item('_delSet'),
                    label='Collection list',
                    show_border=True
                    ),
                Group(
                    Item(name = 'vs',
                         editor=InstanceEditor(
                            view=View(
                                Item(name = '_displayName'),
                                Item(name = '_datasetType')
                                ),
                            ),
                         style='custom',
                         ),
                    label='Collection',
                    show_border=True,
                    ),
                orientation = 'horizontal',
                label='Datasets'
                ),
            Group(
                Item('_pca'),
                label='PCA analysis',
                ),
            layout='tabbed'
            ),
#        width = 800, height = 600,
        resizable = True,
        title = 'Consumer Check',
        menubar = MenuBar(
            Menu(setImport, exitAction,
                 name = '&File'
                 )
            ),
        handler = DsViewHandler(),
        )
