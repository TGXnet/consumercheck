
# stdlib imports
import logging

# Enthought imports
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import View, Item, Group, Handler, InstanceEditor
from enthought.traits.ui.menu import Action, Menu, MenuBar


# Local imports
from dataset_collection import DatasetCollection
from file_importer import FileImporter
from ui_datasets_tree import tree_view
from ui_tab_pca import PcaModelViewHandler, pca_tree_view
from ui_tab_prefmap import PrefmapModelViewHandler, prefmap_tree_view
from about_consumercheck import ConsumerCheckAbout


class MainViewHandler(Handler):
    """Handler for dataset view"""
    # Called when some value in object changes
    def setattr(self, info, obj, name, value):
        super(MainViewHandler, self).setattr(info, obj, name, value)
        logging.info('setattr: Variables %s set to %s', name, value)

    # Event handler signature
    # extended_traitname_changed(info)
    # default context is object
    def import_data(self, ui_info):
        """Action called when activating importing of new dataset"""
        importer = FileImporter()
        imported = importer.interactiveMultiImport()
        for ds in imported:
            ui_info.object.dsl.add_dataset(ds)
            logging.info("importDataset: internal name = %s", ds._ds_id)

    def view_about(self, ui_info):
        ConsumerCheckAbout().edit_traits()
        
    def init(self, ui_info):
        try:
            ui_info.object.splash.close()
        except AttributeError:
            pass

    # end MainViewHandler



class MainUi(HasTraits):
    """Main application class"""
    # Singular dataset list for the application
    # or not?
    dsl = DatasetCollection()
    
    splash = None

    # Object representing the PCA and the GUI tab
    pca = Instance(PcaModelViewHandler)

    # Object representing the Prefmap and the GUI tab
    prefmap = Instance(PrefmapModelViewHandler)

    # Create an action that open dialog for dataimport
    import_action = Action(name = 'Add &Dataset', action = 'import_data')
    # Create an action that exits the application.
    exit_action = Action(name='E&xit', action='_on_close')
    about_action = Action(name='&About', action='view_about')

    def _pca_changed(self, old, new):
        logging.info("Setting pca mother")
        if old is not None:
            old.main_ui_ptr = None
        if new is not None:
            new.main_ui_ptr = self

    def _prefmap_changed(self, old, new):
        logging.info("Setting prefmap mother")
        if old is not None:
            old.main_ui_ptr = None
        if new is not None:
            new.main_ui_ptr = self

    # The main view
    traits_ui_view = View(
        Group(
            Item('dsl', editor=InstanceEditor(view = tree_view),
                 style='custom', label="Datasets", show_label=False),
            Item('pca', editor=InstanceEditor(view = pca_tree_view),
                 style='custom', label="PCA", show_label=False),
            Item('prefmap', editor=InstanceEditor(view = prefmap_tree_view),
                 style='custom', label="Prefmap", show_label=False),
            layout='tabbed'
            ), # end UI tabs group
        resizable = True,
        width = .3,
        height = .3,
        title = 'Consumer Check',
        menubar = MenuBar(
            Menu(import_action, exit_action, name = '&File'),
            Menu(about_action, name='&Help'),
            ),
        handler = MainViewHandler
        )


if __name__ == '__main__':
    from tests.tools import make_dsl_mock
    dsl = make_dsl_mock()
    mother = MainUi(dsl=dsl)
    ui = mother.configure_traits()
    # ui = MainViewHandler().edit_traits( context = dsl )
