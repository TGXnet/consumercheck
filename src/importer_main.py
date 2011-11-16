"""Reading and import of datasets.

Read a file and make a dataset object.

"""
# Stdlib imports
import os.path

# stdlib imports
import logging
# Log everything, and send it to stderr.
# http://docs.python.org/howto/logging-cookbook.html
logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.WARNING)

# Enthought imports
from traits.api import HasTraits, File, List, Button, Instance
from traitsui.api import View, Item, UCustom, FileEditor
from traitsui.menu import OKButton, CancelButton
from pyface.api import FileDialog, OK

# Local imports
from dataset import DataSet
from config import AppConf
from importer_text_previewer import ImportFileParameters, pre_view
from importer_text_file import TextFileImporter
from importer_xls_file import XlsFileImporter

__all__ = ['ImporterMain']


class ImporterMain(HasTraits):
    """Importer class"""

    _conf = Instance(AppConf, AppConf('QPCPrefmap'))
    _import_settings = ImportFileParameters()
    _text_file_reader = TextFileImporter()
    _xls_file_reader = XlsFileImporter()
    _file_path = File()
    _files_path = List(File)
    _datasets = List(DataSet)

    # Dialog for selecting single file
    one_view = View(
        UCustom(
            name='_file_path',
            editor=FileEditor(
                filter=['*.csv;*.txt;*.xls'],
                ),
            resizable=True,
            full_size=True,
            ),
        resizable=True,
        kind='modal',
        height=600,
        width=600,
        buttons=[OKButton, CancelButton],
        )

    # Button to open multiple files dialog
    open_files = Button("Open Files...")

    many_view = View(
        Item('open_files'),
        )

    def import_data(self, file_path, have_variable_names = True, have_object_names = True):
        """Read file and return DataSet objekt"""
        self._import_settings.file_path = file_path
        self._import_settings.have_var_names = have_variable_names
        self._import_settings.have_obj_names = have_object_names
        return self._do_import()

    def dialog_import_data(self):
        """Open dialog for selecting a file, import and return the DataSet"""
        self._file_path = self._conf.read_work_dir()
        self.configure_traits(view='one_view')
        self._import_settings.file_path = self._file_path
        self._conf.save_work_dir(self._import_settings.file_path)
        self._import_settings.configure_traits(view=pre_view)
        return self._do_import()

    def dialog_multi_import(self):
        """Open dialog for selecting multiple files and return a list of DataSet's"""
        self._file_path = self._conf.read_work_dir()
        # For stand alone testing
        # self.configure_traits(view='many_view')
        self._import_settings.file_path = self._file_path
        print(self._file_path)
        self._open_files_changed()
        for filen in self._files_path:
            self._import_settings.file_path = filen
            self._import_settings.configure_traits(view=pre_view)
            self._datasets.append(self._do_import())
        self._conf.save_work_dir(self._import_settings.file_path)
        return self._datasets

    # For select multi file dialog
    def _open_files_changed(self):
        dlg = FileDialog(
            action='open files',
            default_directory=self._file_path,
            title='Import data')
        if dlg.open() == OK:
            self._files_path = dlg.paths

    def _do_import(self):
        fext = self._identify_filetype()
        if fext == 'txt':
            return self._text_file_reader.import_data(self._import_settings)
        elif fext == 'xls':
            return self._xls_file_reader.import_data(self._import_settings)

    def _identify_filetype(self):
        fn = os.path.basename(self._import_settings.file_path)
        return fn.partition('.')[2].lower()


if __name__ == '__main__':
    fi = ImporterMain()
    dsl = fi.dialog_multi_import()
    for ds in dsl:
        ds.print_traits()
