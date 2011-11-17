# StdLib imports
from StringIO import StringIO

# SciPy imports
from numpy import array, loadtxt, genfromtxt

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

        # Read data from file
        with open(self.imp_s.file_path, 'rU') as fp:
            data = fp.read()

        # Preprocess file data
        if self.imp_s.decimal_mark == 'comma':
            if self.imp_s.separator == ',':
                raise Exception('Ambiguous fileformat')
            data = data.replace(',', '.')

        # Do we have variable names
        if self.imp_s.have_var_names:
            names = True
        else:
            names = None

        pd = genfromtxt(
            StringIO(data),
            dtype=None,
            delimiter=self.imp_s.separator,
            names=names)

        if self.imp_s.have_var_names:
            varnames = list(pd.dtype.names)
            if self.imp_s.have_obj_names:
                corner = varnames.pop(0)
                objnames = pd[corner].view().reshape(len(pd),-1)
                objnames = objnames[:,0].tolist()
                self.ds.object_names = objnames
            pd = pd[varnames].view(float).reshape(len(pd),-1)
            self.ds.variable_names = varnames

        self.ds.matrix = pd
        return self.ds
