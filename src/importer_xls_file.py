# StdLib imports
import xlrd

# Enthought imports
from traits.api import implements

# Local imports
from importer_interfaces import IDataImporter
from dataset import DataSet


class XlsFileImporter(object):
    implements(IDataImporter)

    def import_data(self, import_settings):
        return dataset

    def _make_dataset(self):
        return DataSet(
            matrix=self._dataset,
            _source_file=self._import_settings.file_path,
            variable_names=self._variable_names,
            object_names=self._object_names,
            _ds_id=self._import_settings.ds_id,
            _ds_name=self._import_settings.ds_name,
            _dataset_type=self._import_settings.ds_type,
            )

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

