# -*- coding: utf-8 -*-

# stdlib imports
import logging

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
from ds import DataSet
from file_importer_ui import FileImporterUi
from ui_datasets_tree import tree_view
from ui_tab_pca import PcaModel, pca_tree_view
from ui_tab_prefmap import PrefmapModel, prefmap_tree_view


class MainViewHandler(Handler):
    """Handler for dataset view"""

    # Called when some value in object changes
    def setattr(self, info, object, name, value):
        super(MainViewHandler, self).setattr(info, object, name, value)
        logging.info('setattr: Variables %s set to %s', name, value)

    # Event handler signature
    # extended_traitname_changed(info)
    # default context is object
    def importDataset(self, uiInfo):
        """Action called when activating importing of new dataset"""
        importerUi = FileImporterUi()
        fiUi = importerUi.edit_traits(kind='modal')
        if fiUi.result:
            ds = DataSet()
            ds.importDataset(
                importerUi.fileName,
                importerUi.haveVarNames,
                importerUi.haveObjNames
                )
            uiInfo.object.dsl.addDataset(ds)
            logging.info("importDataset: internal name = %s", ds._internalName)
        else:
            logging.info("importDataset: aborted")

    # end MainViewHandler



class MainUi(HasTraits):
    """Main application class"""
    # Singular dataset list for the application
    # or not?
    dsl = DatasetCollection()

    # Object representing the PCA and the GUI tab
    pca = Instance(PcaModel, PcaModel(dsl=dsl))

    # Object representing the Prefmap and the GUI tab
    prefmap = Instance(PrefmapModel, PrefmapModel(dsl=dsl))

    # Create an action that open dialog for dataimport
    setImport = Action(name = 'Add &Dataset',
                       action = 'importDataset')
    # Create an action that exits the application.
    exitAction = Action(name='E&xit',
                        action='_on_close')


    # The main view
    traits_ui_view = View(
        Group(
            Item('dsl', editor=InstanceEditor(view = tree_view), style='custom'),
            Item('pca', editor=InstanceEditor(view = pca_tree_view), style='custom'),
            Item('prefmap', editor=InstanceEditor(view = prefmap_tree_view), style='custom'),
            layout='tabbed'
            ), # end UI tabs group
        resizable = True,
        width = .3,
        height = .3,
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
    # dsl = DatasetCollection()
    mother = MainUi()
    ui = mother.edit_traits()
    # ui = MainViewHandler().edit_traits( context = dsl )
