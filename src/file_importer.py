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

# Scipy imports
from numpy import array, loadtxt
import xlrd

# Enthought imports
from traits.api import HasTraits, File, Str, Bool, Enum, Array, \
     List, Button, Instance
from traitsui.api import View, Item, UCustom, FileEditor
from traitsui.menu import OKButton, CancelButton
from pyface.api import FileDialog, OK

# Local imports
from dataset import DataSet
from config import AppConf

__all__ = ['FileImporter']


class FileImporter(HasTraits):
    """Importer class"""

    _conf = Instance(AppConf, AppConf('QPCPrefmap'))
    # FIXME: This will be moved into a DataImportSettings object
    _file_path = File()
    _files_path = List(File)
    _have_variable_names = Bool(True)
    _have_object_names = Bool(True)

    _dataset = Array()
    _datasets = List(DataSet)
    _variable_names = List()
    _object_names = List()
    _ds_id = Str()
    _ds_name = Str()
    _ds_type = Enum(
        ('Design variable',
         'Sensory profiling',
         'Consumer liking',
         'Consumer attributes',
         'Hedonic attributes',)
        )

    # FileSelectorView
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

    open_files = Button("Open Files...")

    many_view = View(
        Item('open_files'),
        )

    # FIXME: Part of DataPreviewer
    ds_options_view = View(
        Item('_ds_id', style='readonly', label='File name'),
        Item('_ds_name', label='Dataset name'),
        Item('_ds_type', label='Dataset type'),
        Item('_have_variable_names', label='Have variables names?',
             tooltip='Is first row variables names?'),
        Item('_have_object_names', label='Have object names?',
             tooltip='Is first column object names?'),
        kind='modal',
        buttons=[OKButton]
        )

    # FIXME: Will be part of an DataImporterTextFile class
    def import_data(self, file_path, have_variable_names = True, have_object_names = True):
        """Read file and return DataSet objekt"""
        self._file_path = file_path
        self._have_variable_names = have_variable_names
        self._have_object_names = have_object_names
        self._do_import()
        self._make_ds_name()
        return self._make_dataset()

    def dialog_import_data(self):
        """Open dialog for selecting a file, import and return the DataSet"""
        self._file_path = self._conf.read_work_dir()
        self.configure_traits(view='one_view')
        self._do_import()
        self._conf.save_work_dir(self._file_path)
        self._make_ds_name()
        return self._make_dataset()

    def dialog_multi_import(self):
        """Open dialog for selecting multiple files and return a list of DataSet's"""
        self._file_path = self._conf.read_work_dir()
        # For stand alone testing
        # self.configure_traits(view='many_view')
        self._open_files_changed()
        for filen in self._files_path:
            self._file_path = filen
            self._make_ds_name()
            self.configure_traits(view='ds_options_view')
            self._do_import()
            self._datasets.append(self._make_dataset())
        self._conf.save_work_dir(self._file_path)
        return self._datasets

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
            self._read_txt_file()
        elif fext == 'xls':
            self._read_xls_file()

    def _identify_filetype(self):
        fn = os.path.basename(self._file_path)
        return fn.partition('.')[2].lower()

    def _make_dataset(self):
        return DataSet(
            matrix=self._dataset,
            _source_file=self._file_path,
            variable_names=self._variable_names,
            object_names=self._object_names,
            _ds_id=self._ds_id,
            _ds_name=self._ds_name,
            _dataset_type=self._ds_type,
            )

    def _make_ds_name(self):
        # FIXME: Find a better more general solution
        fn = os.path.basename(self._file_path)
        fn = fn.partition('.')[0]
        fn = fn.lower()
        self._ds_id = self._ds_name = fn

    def _read_txt_file(self):
        if self._have_object_names:
            self._read_matrix_with_obj_names()
        else:
            # FIXME: May fail if file not foud
            # No, supose to fail if file not found
            skips = 0
            if self._have_variable_names:
                skips = 1
                self._read_variable_names()
            # FIXME: Except open file error and dataformat error
            self._dataset = loadtxt(
                fname = self._file_path,
                delimiter = '\t',
                skiprows = skips)

    def _read_variable_names(self):
        """Read Matrix column header from text file"""
        # Open file and read headers
        fp = open(self._file_path, 'rU')
        line = fp.readline()
        fp.close()
        # Remove newline char
        line = line.rstrip()
        self._variable_names = line.split('\t')

    def _read_matrix_with_obj_names(self):
        # File is opened using name that is given by
        # the file-open dialog in the main file.
        fp = open(self._file_path, 'rU')

        # All the data is read into a list.
        # FIXME: Prefer to operate on line by line basis to save memory.
        text = fp.readlines()

        # Initiate lists that will hold variable names, object names
        # and data.
        data = []

        obj_names = []

        # Loop through text and extract variable names, object names and
        # data.
        for ind, row in enumerate(text):

            # Get variable names from first row
            if ind == 0:
                heading_fields = row.split('\t')
                heading_fields[-1] = heading_fields[-1].rstrip()
                self._variable_names = heading_fields[1:]

            # Split remaining rows into object names and data
            else:
                row_fields = row.split('\t')
                obj_names.append(row_fields[0])
                row_fields.pop(0)

                # Convert strings into floats
                floats = []
                for item in row_fields:
                    floats.append(float(item))

                data.append(floats)

        # Make variable names, object names and data available as
        # class variables.
        self._object_names = obj_names
        self._dataset = array(data)

    def _read_xls_file(self):
        wb = xlrd.open_workbook(self._file_path, encoding_override=None)
        # wb.sheet_names()
        # sh = wb.sheet_by_name(name)
        sh = wb.sheet_by_index(0)
        ## nested_list = [sh.row_values(i) for i in range(sh.nrows)]
        ## # nested_list = [x for x in nested_list if len(x) == sh.ncols]
        ## self._dataset = array(nested_list, dtype=object)
        nested_list = []
        for row in range(sh.nrows):
            if row < 1:
                continue
            else:
                values = sh.row_values(row, 1)
                nested_list.append(values)
        self._dataset = array(nested_list, dtype=float)
        self._object_names = [
            unicode(x).encode('ascii', 'ignore') for x in sh.col_values(0, 1)]
        self._variable_names = [
            unicode(x).encode('ascii', 'ignore') for x in sh.row_values(0, 1)]


if __name__ == '__main__':
    fi = FileImporter()
    dsl = fi.dialog_multi_import()
    for ds in dsl:
        ds.print_traits()
