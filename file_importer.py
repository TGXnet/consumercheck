"""Reading and import of datasets.

Read a file and make a dataset object.

"""
# Stdlib imports
import os.path
import sys
from os import getcwd, environ

# Scipy imports
from numpy import array, loadtxt
import xlrd

# Enthought imports
from enthought.traits.api import HasTraits, File, Str, Bool, Array, List
from enthought.traits.ui.api import View, Item, UItem, Custom, UCustom, Label, Heading, FileEditor
from enthought.traits.ui.menu import OKButton, CancelButton

# Local imports
from dataset import DataSet

APPNAME = "ConsumerCheck"

class FileImporter(HasTraits):
    """Importer class"""
    _file_uri = File()
    _haveVarNames = Bool(True)
    _haveObjNames = Bool(True)

    _dataset = Array()
    _variableNames = List()
    _objectNames = List()
    _internalName = Str()
    _displayName = Str()

    def import_noninteractive(self, fileUri, haveVarNames = True, haveObjNames = True):
        """Read file and return DataSet objekt"""
        self._file_uri = fileUri
        self._haveVarNames = haveVarNames
        self._haveObjNames = haveObjNames
        self._do_import()
        return self._make_dataset()

    def import_interactive(self):
        """Open dialog for selecting file, import and return DataSet object"""
        self._getWorkingPath()
        self.configure_traits()
        self._do_import()
        self._saveWorkingPath()
        return self._make_dataset()

    def _do_import(self):
        fext = self._det_filetype()
        if fext == 'txt':
            self._read_txt_file()
        elif fext == 'xls':
            self._read_xls_file()
        self._make_name()

    def _det_filetype(self):
        fn = os.path.basename(self._file_uri)
        return fn.partition('.')[2].lower()

    def _make_dataset(self):
        return DataSet(
            matrix=self._dataset,
            _sourceFile=self._file_uri,
            variableNames=self._variableNames,
            objectNames=self._objectNames,
            _internalName=self._internalName,
            _displayName=self._displayName)

    def _make_name(self):
        # FIXME: Find a better more general solution
        fn = os.path.basename(self._file_uri)
        fn = fn.partition('.')[0]
        fn = fn.lower()
        self._internalName = self._displayName = fn

    def _read_txt_file(self):
        if self._haveObjNames:
            self._read_matrix_with_obj_names()
        else:
            # FIXME: May fail if file not foud
            # No, supose to fail if file not found
            skips = 0
            if self._haveVarNames:
                skips = 1
                self._readVarNames()
            # FIXME: Except open file error and dataformat error
            self._dataset = loadtxt(
                fname = self._file_uri,
                delimiter = '\t',
                skiprows = skips)

    def _read_var_names(self):
        """Read Matrix column header from text file"""
        # Open file and read headers
        fp = open(self._file_uri, 'rU')
        line = fp.readline()
        fp.close()
        # Remove newline char
        line = line.rstrip()
        self._variableNames = line.split('\t')

    def _read_matrix_with_obj_names(self):
        # File is opened using name that is given by
        # the file-open dialog in the main file.
        dataFile = open(self._file_uri, 'rU')

        # All the data is read into a list.
        # FIXME: Prefer to operate on line by line basis to save memory.
        allText = dataFile.readlines()

        # Initiate lists that will hold variable names, object names
        # and data.
        data = []

        obj_names = []

        # Loop through allText and extract variable names, object names and
        # data.
        for ind, row in enumerate(allText):

            # Get variable names from first row
            if ind == 0:
                firstRowList = row.split('\t')
                firstRowList[-1] = firstRowList[-1].rstrip()
                self._variableNames = firstRowList[1:]

            # Split remaining rows into object names and data
            else:
                rowObjectsList = row.split('\t')
                obj_names.append(rowObjectsList[0])
                rowObjectsList.pop(0)

                # Convert strings into floats
                floatList = []
                for item in rowObjectsList:
                    floatList.append(float(item))

                data.append(floatList)

        # Make variable names, object names and data available as
        # class variables.
        self._objectNames = obj_names
        self._dataset = array(data)

    def _read_xls_file(self):
        wb = xlrd.open_workbook(self._file_uri, encoding_override=None)
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
        self._objectNames = [unicode(x).encode('ascii', 'ignore') for x in sh.col_values(0, 1)]
        varName = sh.row_values(0, 1)
        self._variableNames = [unicode(x).encode('ascii', 'ignore') for x in sh.row_values(0, 1)]

    def _getWorkingPath(self):
        try:
            fp = open(self._getConfFileName(), 'r')
            uri = fp.readline()
            fp.close()
        except IOError:
            self._file_uri = getcwd()
        else:
            self._file_uri = uri.strip()

    def _saveWorkingPath(self):
        dir_path = os.path.dirname(self._file_uri) + '\n'
        fp = open(self._getConfFileName(), 'w')
        fp.write(dir_path)
        fp.close()

    def _getConfFileName(self):
        if sys.platform == 'darwin':
            from AppKit import NSSearchPathForDirectoriesInDomains
            # http://developer.apple.com/DOCUMENTATION/Cocoa/Reference/Foundation/Miscellaneous/Foundation_Functions/Reference/reference.html#//apple_ref/c/func/NSSearchPathForDirectoriesInDomains
            # NSApplicationSupportDirectory = 14
            # NSUserDomainMask = 1
            # True for expanding the tilde into a fully qualified path
            appdata = os.path.join(NSSearchPathForDirectoriesInDomains(14, 1, True)[0], APPNAME + '.cfg')
        elif sys.platform == 'win32':
            appdata = os.path.join(environ['APPDATA'], APPNAME + '.cfg')
        else:
            appdata = os.path.expanduser(os.path.join("~", ".config", APPNAME + '.cfg'))
        return appdata


    view = View(
        UCustom(
            name='_file_uri',
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


if __name__ == '__main__':
    fi = FileImporter()
    ## ds = fi.import_interactive()
    ## ds.print_traits()
