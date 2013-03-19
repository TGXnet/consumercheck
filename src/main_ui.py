
# stdlib imports
import logging
import webbrowser
from os import path, pardir
logger = logging.getLogger(__name__)

# Enthought imports
from traits.api import HasTraits, Instance, Any, Event
from traitsui.api import View, Item, Group, Handler, InstanceEditor
from traitsui.menu import Action, Menu, MenuBar

# Local imports
from dataset_container import DatasetContainer
from ui_tab_container_tree import tree_editor
from importer_main import ImporterMain
from basic_stat_gui import BasicStatPluginController, bs_plugin_view
from pca_gui import PcaPluginController, pca_plugin_view
from prefmap_gui import PrefmapPluginController, prefmap_plugin_view
from ui_tab_conjoint import ConjointPlugin
from about_consumercheck import ConsumerCheckAbout
from plugin_tree_helper import CalcContainer


class MainViewHandler(Handler):
    """Handler for dataset view"""


    def import_data(self, info):
        """Action called when activating importing of new dataset"""
        importer = ImporterMain()
        imported = importer.dialog_multi_import()
        if imported:
            info.object.dsc.add(*tuple(imported))


    def _close_ds(self, info):
        info.object.dsc.dsl = []


    def view_about(self, info):
        ConsumerCheckAbout().edit_traits()


    def view_user_manual(self, info):
        dev_path = path.join(pardir, "docs-user", 'build', 'html', 'index.html')
        inst_path = path.join('help-docs', 'index.html')
        if path.exists(inst_path):
            webbrowser.open(inst_path)
        else:
            webbrowser.open(dev_path)


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
    dsc = DatasetContainer()
    ds_event = Event()
    dsname_event = Event()
    tulle_event = Event()
    # en_advanced = Bool(False)
    parent_win = Any()

    splash = None


    # Object representating the basic stat
    basic_stat = Instance(BasicStatPluginController)

    # Object representing the PCA and the GUI tab
    pca = Instance(PcaPluginController)

    # Object representing the Prefmap and the GUI tab
    prefmap = Instance(PrefmapPluginController)

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
        self.conjoint = ConjointPlugin(mother_ref=self)
        self.dsc.on_trait_change(self._dsl_updated, 'dsl_changed')
        self.dsc.on_trait_change(self._ds_name_updated, 'ds_changed')


    def _basic_stat_default(self):
        basic_statisitc = CalcContainer(dsc=self.dsc)
        return BasicStatPluginController(basic_statisitc)


    def _pca_default(self):
        pca = CalcContainer(dsc=self.dsc)
        return PcaPluginController(pca)


    def _prefmap_default(self):
        prefmap = CalcContainer(dsc=self.dsc)
        return PrefmapPluginController(prefmap)


    def _dsl_updated(self, obj, name, new):
        self.ds_event = True
        self.tulle_event = True


    def _ds_name_updated(self, obj, name, new):
        self.dsname_event = True
        # self.tulle_event = True


    def _toggle_advanced(self):
        self.en_advanced = not self.en_advanced
        print(self.en_advanced)


    # The main view
    traits_ui_view = View(
        Group(
            Item('dsc', editor=tree_editor, label="Datasets", show_label=False),
            Item('basic_stat', editor=InstanceEditor(view=bs_plugin_view),
                 style='custom', label="Basic stat", show_label=False),
            Item('pca', editor=InstanceEditor(view=pca_plugin_view),
                 style='custom', label="PCA", show_label=False),
            Item('prefmap', editor=InstanceEditor(view=prefmap_plugin_view),
                 style='custom', label="Prefmap", show_label=False),
            Item('conjoint', editor=InstanceEditor(),
                 style='custom', label="Conjoint", show_label=False),
            layout='tabbed'
            ), # end UI tabs group
        resizable = True,
        width=1000,
        height=600,
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
    from tests.conftest import all_dsc
    lfn = __file__.split('.')[0]+'.log'
    logging.basicConfig(level=logging.INFO,
                        # format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        # datefmt='%m-%d %H:%M',
                        filename=lfn,
                        filemode='w')

    logger.info('Start interactive')

    mother = MainUi(dsc=all_dsc())
    with np.errstate(invalid='ignore'):
        ui = mother.configure_traits()
