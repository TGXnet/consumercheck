
# stdlib imports
import logging
import webbrowser
from os import path, pardir
logger = logging.getLogger(__name__)

# Enthought imports
from traits.api import HasTraits, Instance, Any, Event, Bool
from traitsui.api import View, Item, Group, Handler, InstanceEditor
from traitsui.menu import Action, Menu, MenuBar


# Local imports
from dataset_collection import DatasetCollection
from importer_main import ImporterMain
from ui_datasets_tree import tree_view
from ui_tab_pca import PCAPlugin
from ui_tab_prefmap import PrefmapPlugin
from ui_tab_conjoint import ConjointPlugin
from about_consumercheck import ConsumerCheckAbout


class MainViewHandler(Handler):
    """Handler for dataset view"""


    def import_data(self, info):
        """Action called when activating importing of new dataset"""
        importer = ImporterMain()
        imported = importer.dialog_multi_import()
        for ds in imported:
            info.object.dsl.add_dataset(ds)
            logger.info("importDataset: internal name = %s", ds._ds_id)


    def _close_ds(self, info):
        datasets = []
        for i in info.object.dsl._datasets:
            datasets.append(i)
        for a in datasets:
            info.object.dsl.delete_dataset(a)


    def view_about(self, info):
        ConsumerCheckAbout().edit_traits()


    def view_user_manual(self, info):
        webbrowser.open(path.join(pardir, "docs-user", 'build', 'html', 'index.html'))


    def init(self, info):
        # Force update of plugin windows for preimported datasets
        info.object.ds_event = True
        # Close splash window
        info.object.win_handle = info.ui.control
        try:
            info.object.splash.close()
        except AttributeError:
            pass



class MainUi(HasTraits):
    """Main application class"""
    # Singular dataset list for the application
    # or not?
    # dsl = Instance(DatasetCollection)
    dsl = DatasetCollection()
    ds_event = Event()
    dsname_event = Event()
    # en_advanced = Bool(False)
    parent_win = Any()


    def _toggle_advanced(self):
        self.en_advanced = not self.en_advanced
        print(self.en_advanced)

    splash = None

    # Object representing the PCA and the GUI tab
    pca = Instance(PCAPlugin)

    # Object representing the Prefmap and the GUI tab
    prefmap = Instance(PrefmapPlugin)
    
    # Object representing the Conjoint and the GUI tab
    conjoint = Instance(ConjointPlugin)

    # Create an action that open dialog for dataimport
    import_action = Action(name = 'Add &Dataset', action = 'import_data')
    # Create an action that exits the application.
    exit_action = Action(name='E&xit', action='_on_close')
    about_action = Action(name='&About', action='view_about')
    user_manual_action = Action(name='&User manual', action='view_user_manual')
    close_action = Action(name='&Remove Datasets', action='_close_ds')
    advanced_action = Action(name='&Advanced settings', checked_when='en_advanced',
                             style='toggle', action='_toggle_advanced')


    def __init__(self, **kwargs):
        super(MainUi, self).__init__(**kwargs)
        self.prefmap = PrefmapPlugin(mother_ref=self)
        self.pca = PCAPlugin(mother_ref=self)
        self.conjoint = ConjointPlugin(mother_ref=self)
        self.dsl.on_trait_change(self._dsl_updated, 'datasets_event')
        self.dsl.on_trait_change(self._ds_name_updated, 'ds_name_event')


    # @on_trait_change('', post_init=True)
    # @on_trait_change('dsl.datasets_event')
    def _dsl_updated(self, obj, name, new):
        self.ds_event = True


    # @on_trait_change('dsl.ds_name_event')
    def _ds_name_updated(self, obj, name, new):
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
            Item('conjoint', editor=InstanceEditor(),
                 style='custom', label="Conjoint", show_label=False),
            layout='tabbed'
            ), # end UI tabs group
        resizable = True,
        width=800,
        height=400,
        title = 'Consumer Check',
        menubar = MenuBar(
            Menu(import_action, close_action, exit_action, name='&File'),
#            Menu(advanced_action, name='&Settings'),
            Menu(about_action, user_manual_action, name='&Help'),
            ),
        handler = MainViewHandler
        )


if __name__ == '__main__':
    import numpy as np
    from tests.conftest import dsc_mock
    lfn = __file__.split('.')[0]+'.log'
    logging.basicConfig(level=logging.INFO,
                        # format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        # datefmt='%m-%d %H:%M',
                        filename=lfn,
                        filemode='w')

    logger.info('Start interactive')

    dsl = dsc_mock()
    mother = MainUi(dsl=dsl)
    # mother = MainUi()
    with np.errstate(invalid='ignore'):
        ui = mother.configure_traits()
