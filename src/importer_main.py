"""Reading and import of datasets.

Read a file and make a dataset object.

"""
# Std lib imports
import logging
logger = logging.getLogger('tgxnet.nofima.cc.'+__name__)
import os.path

# Enthought imports
from traits.api import HasTraits, Bool, File, List, Str
from traitsui.api import View, Item
from traitsui.menu import OKButton
from pyface.api import FileDialog, OK, CANCEL

# Local imports
import cc_config as conf
from importer_text_file import ImporterTextFile
from importer_xls_file import ImporterXlsFile
# from importer_xlsx_file import ImporterXlsxFile

__all__ = ['ImporterMain']


class ImporterMain(HasTraits):
    """Importer class"""

    _last_open_path = File()
    _files_path = List(File)
    _notice_shown = Bool(False)


    def import_data(self, file_path, have_variable_names = True, have_object_names = True, sep='\t'):
        """Read file and return DataSet objekt

        Does not show any UI.
        """
        importer = self._make_importer(file_path)
        importer.have_var_names = have_variable_names
        importer.have_obj_names = have_object_names
        importer.delimiter = sep
        ds = importer.import_data()
        return ds


    def dnd_import_data(self, path):
        """Drag and drop reactor

        Open dialog for dragged file, import and return the DataSet
        """
        importer = self._make_importer(path)
        importer.edit_traits()
        ds = importer.import_data()
        return ds


    def dialog_multi_import(self):
        """Multi file import

        Open dialog for selecting multiple files.
        Shows a settings dialog for each selected file
        return a list of imported DataSet's
        """
        self._last_open_path = conf.get_option('work_dir')
        logger.debug('Last imported file: %s', self._last_open_path)

        # Show info about legal data format
        if not self._notice_shown:
            notice = ImportNotice()
            notice.edit_traits()
            self._notice_shown = True

        # Select files
        status = self._show_file_selector()
        if status == CANCEL:
            logger.info('Cancel file imports')
            return []
        datasets = []
        logger.debug('File(s) to import: \n%s', '\n'.join(self._files_path))

        for file_n in self._files_path:
            importer = self._make_importer(file_n)
            logger.info('Attempting to import %s with %s', file_n, type(importer))
            ui = importer.edit_traits()
            if ui.result:
                ds = importer.import_data()
                datasets.append(ds)
            else:
                continue
        conf.set_option('work_dir', file_n)
        return datasets


    # For select multi file dialog
    def _show_file_selector(self):
        dlg = FileDialog(
            action='open files',
            default_directory=self._last_open_path,
            title='Import data')
        status = dlg.open()
        if status == OK:
            self._files_path = dlg.paths
        elif status == CANCEL:
            pass
        return status


    def _make_importer(self, path):
        fext = self._identify_filetype(path)
        if fext in ['txt', 'csv']:
            return ImporterTextFile(file_path=path)
        elif fext in ['xls', 'xlsx', 'xlsm']:
            return ImporterXlsFile(file_path=path)
        else:
            return ImporterTextFile(file_path=path)


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

ConsumerCheck is not able to handle non-English characters in the row and column names.
If you experience problems when reading data from an Excel sheet; mark, copy, paste and save the actual data set in sheet 1 of a new Excel window.
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
    logging.basicConfig(level=logging.INFO)
    fi = ImporterMain()
    dsc = fi.dialog_multi_import()
    for ds in dsc:
        ds.print_traits()
        print(ds.mat.dtypes)
