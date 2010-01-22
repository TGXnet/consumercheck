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
from file_import_ui import FileImport
from ui_tab_pca import PcaModel
from ui_tab_ds_list import datasets_view


class MainViewHandler(Handler):
    """Handler for dataset view"""

    # Called when some value in object changes
    def setattr(self, info, object, name, value):
        super(DsViewHandler, self).setattr(info, object, name, value)
        print 'DsViewHandler:setattr:', name, 'to', value

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

    # end MainViewHandler



class MainUi(HasTraits):
    """Main application class"""
    # Singular dataset list for the application
    # or not?
    dsl = Instance(DatasetCollection, DatasetCollection())
    currset = DataSet()

    # Object representing the PCA and the GUI tab
    pca = Instance(PcaModel, PcaModel(ds=currset))

    # Create an action that open dialog for dataimport
    setImport = Action(name = 'Add &Dataset',
                       action = 'importDataset')
    # Create an action that exits the application.
    exitAction = Action(name='E&xit',
                        action='_on_close')


    # The main view
    traits_ui_view = View(
        Group(
            Item('dsl', editor=InstanceEditor(view=datasets_view), style='custom'),
            Item('pca', editor=InstanceEditor(), style='custom'),
            layout='tabbed'
            ), # end UI tabs group
        title = 'Consumer Check',
        menubar = MenuBar(
            Menu(setImport, exitAction,
                 name = '&File'
                 )
            ),
        handler = MainViewHandler
        )


if __name__ == '__main__':
    """Run the application. """
    from enthought.pyface.api import GUI

    # dsl = DatasetCollection()
    mother = MainUi()
    ui = mother.edit_traits()
    # ui = MainViewHandler().edit_traits( context = dsl )
