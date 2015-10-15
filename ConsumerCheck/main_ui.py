#-----------------------------------------------------------------------------
#  Copyright (C) 2014 Thomas Graff <thomas.graff@tgxnet.no>
#
#  This file is part of ConsumerCheck.
#
#  ConsumerCheck is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  ConsumerCheck is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ConsumerCheck.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------

# Std lib imports
import logging
logger = logging.getLogger('tgxnet.nofima.cc.'+__name__)
import webbrowser
from os import path, pardir

# Enthought imports
from traits.api import HasTraits, Instance, Any, TraitError
from traitsui.api import View, Item, Group, Handler, InstanceEditor
from traitsui.menu import Action, Menu, MenuBar

# Local imports
import cc_config as conf
from dataset import DataSet
from dataset_container import DatasetContainer
from ui_tab_container_tree import tree_editor
from importer_main import ImporterMain
from about_consumercheck import ConsumerCheckAbout

# Plugin imports
from basic_stat_gui import BasicStatPluginController, BasicStatCalcContainer, bs_plugin_view
from pca_gui import PcaPluginController, PcaCalcContainer, pca_plugin_view
from prefmap_gui import PrefmapPluginController, PrefmapCalcContainer, prefmap_plugin_view
from plscr_gui import PlsrPcrPluginController, PlsrPcrCalcContainer, plscr_plugin_view
from conjoint_gui import ConjointPluginController, ConjointCalcContainer, conjoint_plugin_view

state_file = conf.pkl_file_url()


class MainViewHandler(Handler):
    """Handler for data set view"""

    importer = Instance(ImporterMain, ImporterMain())

    def import_data(self, info):
        """Action called when activating importing of new data set"""
        # importer = ImporterMain()
        imported = self.importer.dialog_multi_import(info.ui.control)
        if imported:
            info.object.dsc.add(*tuple(imported))

    def _close_ds(self, info):
        info.object.dsc.empty()

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
        # Close splash window
        logger.info('Init main ui')
        info.object.win_handle = info.ui.control

        # Import workspace
        try:
            info.object.dsc.read_datasets(state_file)
        except (IOError, TypeError, ImportError, TraitError):
            # FIXME: Open infor dialog
            logger.warning('Could not read workspace file')
        try:
            info.object.splash.close()
        except AttributeError:
            pass

    def closed(self, info, is_ok):
        info.object.dsc.save_datasets(state_file)

    def transpose_ds(self, editor, obj):
        dsc = editor.get_parent(obj)
        dst = DataSet()
        dst.mat = obj.mat.T
        dst.kind = obj.kind
        dst.display_name = obj.display_name + '_T'
        dsc.add(dst)


class MainUi(HasTraits):
    """Main application class"""
    dsc = DatasetContainer()
    # en_advanced = Bool(False)
    win_handle = Any()
    splash = None

    # Object representating the basic stat
    basic_stat = Instance(BasicStatPluginController)
    # Object representing the PCA and the GUI tab
    pca = Instance(PcaPluginController)
    # Object representing the Prefmap and the GUI tab
    prefmap = Instance(PrefmapPluginController)
    # Object representing the PlsrPcr and the GUI tab
    plscr = Instance(PlsrPcrPluginController)
    # Object representing the Conjoint and the GUI tab
    conjoint = Instance(ConjointPluginController)

    # Create an action that open dialog for dataimport
    import_action = Action(name='Add &Data set', action='import_data')
    # Create an action that exits the application.
    exit_action = Action(name='E&xit', action='_on_close')
    about_action = Action(name='&About', action='view_about')
    user_manual_action = Action(name='&User manual', action='view_user_manual')
    close_action = Action(name='&Remove Data sets', action='_close_ds')
    advanced_action = Action(name='&Advanced settings', checked_when='en_advanced',
                             style='toggle', action='_toggle_advanced')

    def _basic_stat_default(self):
        basic_statisitc = BasicStatCalcContainer(dsc=self.dsc)
        return BasicStatPluginController(basic_statisitc)

    def _pca_default(self):
        pca = PcaCalcContainer(dsc=self.dsc)
        return PcaPluginController(pca)

    def _prefmap_default(self):
        prefmap = PrefmapCalcContainer(dsc=self.dsc)
        return PrefmapPluginController(prefmap)

    def _plscr_default(self):
        plscr = PlsrPcrCalcContainer(dsc=self.dsc)
        return PlsrPcrPluginController(plscr)

    def _conjoint_default(self):
        conjoint = ConjointCalcContainer(dsc=self.dsc)
        return ConjointPluginController(conjoint)

    def _toggle_advanced(self):
        self.en_advanced = not self.en_advanced
        print(self.en_advanced)


    # The main view
    traits_ui_view = View(
        Group(
            Item('dsc', editor=tree_editor, label="Data sets", show_label=False),
            Item('basic_stat', editor=InstanceEditor(view=bs_plugin_view),
                 style='custom', label="Basic stat liking", show_label=False),
            Item('pca', editor=InstanceEditor(view=pca_plugin_view),
                 style='custom', label="PCA", show_label=False),
            Item('prefmap', editor=InstanceEditor(view=prefmap_plugin_view),
                 style='custom', label="Prefmap", show_label=False),
            Item('plscr', editor=InstanceEditor(view=plscr_plugin_view),
                 style='custom', label="PLSR/PCR", show_label=False),
            Item('conjoint', editor=InstanceEditor(view=conjoint_plugin_view),
                 style='custom', label="Conjoint", show_label=False),
            layout='tabbed'
        ),  # end UI tabs group
        resizable=True,
        width=1000,
        height=600,
        title='ConsumerCheck',
        menubar=MenuBar(
            Menu(import_action,
                 close_action,
#                 exit_action,
                 name='&File'),
            ## Menu(advanced_action, name='&Settings'),
            Menu(about_action, user_manual_action, name='&Help'),
            ),
        handler=MainViewHandler
        )


if __name__ == '__main__':
    import numpy as np
    from tests.conftest import all_dsc
    logging.basicConfig(level=logging.DEBUG)
    logger.info('Start interactive')

    mother = MainUi(dsc=all_dsc())
    with np.errstate(invalid='ignore'):
        ui = mother.configure_traits()
