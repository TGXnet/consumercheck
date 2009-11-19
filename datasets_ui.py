# coding=utf-8

# Enthought imports
from enthought.traits.api \
    import HasTraits, Instance, DelegatesTo, Button, Str
from enthought.traits.ui.api \
    import View, Item, Group, ListStrEditor, Handler, FileEditor
from enthought.traits.ui.menu \
    import Action, OKButton, CancelButton

# Local imports
from dataset_collection import DatasetCollection
from dataset import DataSet




class DsViewHandler(Handler):
    """Handler for dataset view"""

    def setattr(self, info, object, name, value):
        Handler.setattr(self, info, object, name, value)
        print 'Change:', name, 'to', value



    # Also called on window creation
    def object__selIndex_changed(self, info):
        if not info.initialized:
            info.object.vs = info.object.vc.retriveDatasetByIndex(0)
        else:
            info.object.vs = info.object.vc.retriveDatasetByIndex(info.object._selIndex)
            print "Vs changed to", info.object.vs



    def import_dataset(self, uiInfo):
        """Action called when activating importing of new dataset"""
        print "Import dataset pressed"


    def remove_dataset(self, uiInfo):
        """Action called when activating removing of selected dataset"""
        print "Remove dataset pressed"





class DatasetsView(HasTraits):
    """Tree like view for dataset collection and panel for each dataset. """

    # View Collection
    vc = Instance(DatasetCollection)
    # View Set
    vs = Instance(DataSet)

    # Delegations
    # Collection
    _dispNameIndex      = DelegatesTo('vc')
    _selIndex           = DelegatesTo('vc')
    _testBool           = DelegatesTo('vc')
    _addSet             = Button(label='Import')
    _delSet             = Button(label='Remove')

    # Data set
    _internalName       = DelegatesTo('vs')
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
                    Item('_testBool'),
                    label='Collection list',
                    show_border=True
                    ),
                Group(
                    Item('_internalName'),
                    Item('_displayName'),
                    Item('_datasetType'),
                    Item('_matrixColumnHeader'),
                    Item('_isCalculated'),
                    Item('_isActive'),
                    label='Collection',
                    show_border=True
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
        title = 'Consumer Check',
        handler = DsViewHandler(),
        buttons = [OKButton, CancelButton]
        )
