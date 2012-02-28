"""Reading and import of datasets.

Read a file and make a dataset object.

"""
# Stdlib imports
import os.path

# stdlib imports
import logging
# Log everything, and send it to stderr.
# http://docs.python.org/howto/logging-cookbook.html
# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.WARNING)

# Enthought imports
from traits.api import HasTraits, File, List, Button, Instance
from traitsui.api import View, Item, UCustom, FileEditor
from traitsui.menu import OKButton, CancelButton
from pyface.api import FileDialog, OK

# Local imports
from dataset import DataSet
from config import AppConf
from importer_text_file import ImporterTextFile
from importer_xls_file import ImporterXlsFile
from importer_xlsx_file import ImporterXlsxFile

__all__ = ['ImporterMain']


class ImporterMain(HasTraits):
    """Importer class"""

    _conf = Instance(AppConf, AppConf('QPCPrefmap'))
    _file_path = File()
    _files_path = List(File)
    _datasets = List(DataSet)

    # Dialog for selecting single file
    one_view = View(
        UCustom(
            name='_file_path',
            editor=FileEditor(
                filter=['*.csv;*.txt;*.xls;*.xlsx'],
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
        importer = self._make_importer(file_path)
        # importer.configure_traits()
        importer.make_ds_name()
        importer.have_var_names = have_variable_names
        importer.have_obj_names = have_object_names
        ds = importer.import_data()
        ds = self._add_generic_name(ds, importer)
        return ds


    def dnd_import_data(self,path):
        """Open dialog for selecting a file, import and return the DataSet"""
        filen = path
        importer = self._make_importer(filen)
        importer.configure_traits()
        ds = importer.import_data()
        ds = self._add_generic_name(ds, importer)
        return ds


    def dialog_multi_import(self):
        """Open dialog for selecting multiple files and return a list of DataSet's"""
        self._file_path = self._conf.read_work_dir()
        # For stand alone testing
        # self.configure_traits(view='many_view')
        # Open multipe file selection dialog
        self._open_files_changed()
        for filen in self._files_path:
            importer = self._make_importer(filen)
            importer.configure_traits()
            ds = importer.import_data()
            ds = self._add_generic_name(ds, importer)
            self._datasets.append(ds)
        self._conf.save_work_dir(filen)
        return self._datasets


    def _add_generic_name(self, ds, importer):
        if not importer.have_var_names:
            for i in range(ds.n_cols):
                ds.variable_names.append('V{}'.format(i+1))
            importer.have_var_names = True
        if not importer.have_obj_names:
            for i in range(ds.n_rows):
                ds.object_names.append('O{}'.format(i+1))
            importer.have_obj_names = True

        if importer.have_var_names and ds.n_cols > len(ds.variable_names):
            raise Exception(
                'Not variable names for all columns',
                ds.n_cols, len(ds.variable_names))
        if importer.have_obj_names and ds.n_rows > len(ds.object_names):
            raise Exception(
                'Not object names for all rows',
                ds.n_rows, len(ds.object_names))
        return ds


    # For select multi file dialog
    def _open_files_changed(self):
        dlg = FileDialog(
            action='open files',
            default_directory=self._file_path,
            title='Import data')
        if dlg.open() == OK:
            self._files_path = dlg.paths


    def _make_importer(self, path):
        fext = self._identify_filetype(path)
        if fext in ['txt', 'csv']:
            return ImporterTextFile(file_path=path)
        elif fext in ['xls']:
            return ImporterXlsFile(file_path=path)
        elif fext in ['xlsx', 'xlsm']:
            return ImporterXlsxFile(file_path=path)


    def _identify_filetype(self, path):
        fn = os.path.basename(path)
        return fn.partition('.')[2].lower()

#Instantiate DND

DND = ImporterMain()

if __name__ == '__main__':
    fi = ImporterMain()
    ## dsl = fi.dialog_multi_import()
    ## for ds in dsl:
    ##     ds.print_traits()
    ds = fi.import_data('datasets/Cheese/ConsumerLiking.txt')
