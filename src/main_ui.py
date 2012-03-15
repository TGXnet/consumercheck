
# stdlib imports
import logging

# Enthought imports
from traits.api import HasTraits, Instance, Event, on_trait_change
from traitsui.api import View, Item, Group, Handler, InstanceEditor
from traitsui.menu import Action, Menu, MenuBar


# Local imports
from dataset_collection import DatasetCollection
from importer_main import ImporterMain
from ui_datasets_tree import tree_view
from ui_tab_pca import PCAPlugin
from ui_tab_prefmap import PrefmapPlugin
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
        importer = ImporterMain()
        imported = importer.dialog_multi_import()
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
    # dsl = Instance(DatasetCollection)
    dsl = DatasetCollection()
    ds_event = Event()
    dsname_event = Event()
    
    splash = None

    # Object representing the PCA and the GUI tab
    pca = Instance(PCAPlugin)

    # Object representing the Prefmap and the GUI tab
    prefmap = Instance(PrefmapPlugin)

    # Create an action that open dialog for dataimport
    import_action = Action(name = 'Add &Dataset', action = 'import_data')
    # Create an action that exits the application.
    exit_action = Action(name='E&xit', action='_on_close')
    about_action = Action(name='&About', action='view_about')


    def __init__(self, **kwargs):
        super(MainUi, self).__init__(**kwargs)
        self.prefmap = PrefmapPlugin(mother_ref=self)
        self.pca = PCAPlugin(mother_ref=self)
        self.dsl.on_trait_change(self._dsl_updated, 'datasets_event')
        self.dsl.on_trait_change(self._ds_name_updated, 'ds_name_event')


    # @on_trait_change('', post_init=True)
    # @on_trait_change('dsl.datasets_event')
    def _dsl_updated(self, obj, name, new):
        print("main: dsl changed")
        self.ds_event = True


    # @on_trait_change('dsl.ds_name_event')
    def _ds_name_updated(self, obj, name, new):
        print("main: ds name changed")
        self.dsname_event = True


    # The main view
    traits_ui_view = View(
        Group(
            Item('dsl', editor=InstanceEditor(view=tree_view),
                 style='custom', label="Datasets", show_label=False),
            Item('pca', editor=InstanceEditor(),
                 style='custom', label="PCA", show_label=False),
            Item('prefmap', editor=InstanceEditor(),
                 style='custom', label="Prefmap", show_label=False),
            layout='tabbed'
            ), # end UI tabs group
        resizable = True,
        width=800,
        height=400,
        title = 'Consumer Check',
        menubar = MenuBar(
            Menu(import_action, exit_action, name = '&File'),
            Menu(about_action, name='&Help'),
            ),
        handler = MainViewHandler
        )


if __name__ == '__main__':
    from tests.conftest import make_dsl_mock
    dsl = make_dsl_mock()
    mother = MainUi(dsl=dsl)
    # mother = MainUi()
    ui = mother.configure_traits()
