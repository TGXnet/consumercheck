"""Reading and import of datasets.

Read a file and make a dataset object.

"""
# Stdlib imports
import os.path

# import logging
# Log everything, and send it to stderr.
# http://docs.python.org/howto/logging-cookbook.html
# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.WARNING)
# Log what the importe is going to do
# And log operation completed if success

# Enthought imports
from traits.api import HasTraits, Bool, File, List, Instance, Str
from traitsui.api import View, UCustom, FileEditor, Item
from traitsui.menu import OKButton, CancelButton
from pyface.api import FileDialog, OK, CANCEL

# Local imports
import cc_config as conf
from dataset import DataSet
from importer_text_file import ImporterTextFile
from importer_xls_file import ImporterXlsFile
from importer_xlsx_file import ImporterXlsxFile

__all__ = ['ImporterMain']


class ImporterMain(HasTraits):
    """Importer class"""

    _last_open_path = File()
    _files_path = List(File)
    # _datasets = List(DataSet)
    _notice_shown = Bool(False)


    def import_data(self, file_path, have_variable_names = True, have_object_names = True, sep='\t'):
        """Read file and return DataSet objekt"""
        importer = self._make_importer(file_path)
        importer.have_var_names = have_variable_names
        importer.have_obj_names = have_object_names
        importer.delimiter = sep
        importer.kind = self._pick_kind(file_path)
        ds = importer.import_data()
        return ds


    def dnd_import_data(self, path):
        """Open dialog for selecting a file, import and return the DataSet"""
        importer = self._make_importer(path)
        importer.edit_traits()
        ds = importer.import_data()
        return ds


    def dialog_multi_import(self):
        """Open dialog for selecting multiple files and return a list of DataSet's"""
        self._last_open_path = conf.get_option('work_dir')
        if not self._notice_shown:
            notice = ImportNotice()
            notice.edit_traits()
            self._notice_shown = True
        status = self._show_file_selector()
        if status == CANCEL:
            return []
        datasets = []
        for filen in self._files_path:
            importer = self._make_importer(filen)
            importer.kind = self._pick_kind(filen)
            importer.edit_traits()
            ds = importer.import_data()
            datasets.append(ds)
        conf.set_option('work_dir', filen)
        return datasets


    # For select multi file dialog
    def _show_file_selector(self):
        dlg = FileDialog(
            action='open files',
            default_directory=self._last_open_path,
            title='Import data')
        status = dlg.open()
        if status == OK:
            print(dlg.paths)
            print(self._files_path)
            self._files_path = dlg.paths
        elif status == CANCEL:
            pass
        return status


    def _make_importer(self, path):
        fext = self._identify_filetype(path)
        if fext in ['txt', 'csv']:
            return ImporterTextFile(file_path=path)
        elif fext in ['xls']:
            return ImporterXlsFile(file_path=path)
        elif fext in ['xlsx', 'xlsm']:
            return ImporterXlsxFile(file_path=path)
        else:
            return ImporterTextFile(file_path=path)


    def _pick_kind(self, filen):
        '''Available types:
         * Design variable
         * Sensory profiling
         * Consumer liking
         * Consumer characteristics
        Defined in dataset.py
        '''
        filen = filen.lower()
        if 'design' in filen:
            return 'Design variable'
        elif 'liking' in filen:
            return 'Consumer liking'
        elif 'attr' in filen:
            return 'Consumer characteristics'
        elif 'sensory' in filen:
            return 'Sensory profiling'
        elif 'qda' in filen:
            return 'Sensory profiling'
        return 'Sensory profiling'


    def _identify_filetype(self, path):
        fn = os.path.basename(path)
        return fn.partition('.')[2].lower()


class ImportNotice(HasTraits):
    message = Str('''
This program allows for importing four different types of data:
 * Qualitative descriptive analysis (QDA); rows: samples - columns: sensory attributes.
 * Consumer acceptance data; rows: samples - columns: consumers.
 * Consumer characteristics; rows: consumers - columns: characteristics.
 * Experimental design; rows: samples - columns: design variables.

Preference mapping: the two last one will not be used.
Conjoint analysis: the first one will not be used.
'''
        )

    traits_view = View(
        Item('message', show_label=False, springy=True, style='custom' ),
        title='Data import notice',
        height=300,
        width=600,
        resizable=True,
        buttons=[OKButton],
        kind='modal',
        )


#Instantiate DND
DND = ImporterMain()


if __name__ == '__main__':
    fi = ImporterMain()
    dsc = fi.dialog_multi_import()
    for ds in dsc:
        ds.print_traits()
