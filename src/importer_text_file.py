# StdLib imports

# SciPy imports
from numpy import array, loadtxt

# Enthought imports
from traits.api import implements

# Local imports
from importer_interfaces import IDataImporter
from dataset import DataSet


class TextFileImporter(object):
    implements(IDataImporter)

    def import_data(self, import_settings):
        self.imp_s = import_settings
        self.ds = DataSet(
            _dataset_type=import_settings.ds_type,
            _ds_id=import_settings.ds_id,
            _ds_name=import_settings.ds_name,
            _source_file=import_settings.file_path)

        if self.imp_s.have_obj_names:
            self._read_matrix_with_obj_names()
        else:
            skips = 0
            if self.imp_s.have_var_names:
                skips = 1
                self._read_variable_names()
            # FIXME: Except open file error and dataformat error
            self.ds.matrix = loadtxt(
                fname = self.imp_s.file_path,
                delimiter = self.imp_s.separator,
                skiprows = skips)

        return self.ds

    def _read_variable_names(self):
        """Read Matrix column header from text file"""
        # Open file and read headers
        fp = open(self.imp_s.file_path, 'rU')
        line = fp.readline()
        fp.close()
        # Remove newline char
        line = line.rstrip()
        self.ds.variable_names = line.split(self.imp_s.separator)

    def _read_matrix_with_obj_names(self):
        # File is opened using name that is given by
        # the file-open dialog in the main file.
        fp = open(self.imp_s.file_path, 'rU')

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
                heading_fields = row.split(self.imp_s.separator)
                heading_fields[-1] = heading_fields[-1].rstrip()
                self.ds.variable_names = heading_fields[1:]

            # Split remaining rows into object names and data
            else:
                row_fields = row.split(self.imp_s.separator)
                obj_names.append(row_fields[0])
                row_fields.pop(0)

                # Convert strings into floats
                floats = []
                for item in row_fields:
                    floats.append(float(item))

                data.append(floats)

        # Make variable names, object names and data available as
        # class variables.
        self.ds.object_names = obj_names
        self.ds.matrix = array(data)
