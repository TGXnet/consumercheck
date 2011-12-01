# StdLib imports
import os.path
from StringIO import StringIO
import xlrd
import logging
# Log everything, and send it to stderr.
# http://docs.python.org/howto/logging-cookbook.html
# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.WARNING)


# Enthought imports
from traits.api import implements, HasTraits, File, Bool, Str, Enum, Int, List
from traitsui.api import View, Group, Item, TabularEditor, EnumEditor, Handler
from traitsui.tabular_adapter import TabularAdapter
from traitsui.menu import OKButton, CancelButton

# Local imports
from importer_interfaces import IDataImporter
from dataset import DataSet

#Import NumPy
import numpy as np


class RawLineAdapter(TabularAdapter):
    columns = []
    ncols = Int()
    # font = 'Courier 10'

    def _ncols_changed(self, info):
        self.columns = ["col{}".format(i) for i in range(self.ncols)]


preview_table = TabularEditor(
    adapter=RawLineAdapter(),
    operations=[],
    )


class FilePreviewer(Handler):
    _raw_lines = List(Str)
    _parsed_data = List()

    def init(self, info):
        info.object.make_ds_name()
        self._probe_read(info.object)

    def _fix_preview_matrix(self, preview_matrix, length):
        for i, row in enumerate(preview_matrix):
            if len(row) < length:
                preview_matrix[i] += ['']*(length-len(row))
        return preview_matrix

    def _probe_read(self, obj, no_lines=7, length=35):
        lines = []
        with open(obj.file_path, 'rU') as fp:
            for i in range(no_lines):
                line = fp.readline(length)
                if not ('\r' in line or '\n' in line):
                    fp.readline()
                logging.debug("linje {}: {}".format(i, line.rstrip('\n')))
                lines.append(line.rstrip('\n'))
        self._raw_lines = lines


preview_handler = FilePreviewer()




class ImporterXlsFile(HasTraits):
    implements(IDataImporter)
    file_path = File()
    transpose = Bool(False)
    have_var_names = Bool(True)
    have_obj_names = Bool(True)
    ds_id = Str()
    ds_name = Str()
    ds_type = Enum(
        ('Design variable',
         'Sensory profiling',
         'Consumer liking',)
        )

    def make_ds_name(self):
        # FIXME: Find a better more general solution
        fn = os.path.basename(self.file_path)
        fn = fn.partition('.')[0]
        fn = fn.lower()
        self.ds_id = self.ds_name = fn

    def import_data(self):
        self.ds = DataSet(
            _dataset_type=self.ds_type,
            _ds_id=self.ds_id,
            _ds_name=self.ds_name,
            _source_file=self.file_path)
        
        raw_data = xlrd.open_workbook(self.file_path)
        data_sheet = raw_data.sheet_by_index(0)
        c_table = []
        for x in range(data_sheet.nrows):
            c_row = []
            for y in range(data_sheet.ncols):
                c_row.append((data_sheet.cell_value(x,y)))
            c_table.append(c_row)
        
        if self.have_obj_names:
            objnamelist = data_sheet.col_values(0)
            objnamelist.pop(0)
            
            for i in range(0,len(c_table)):
                c_table[i].pop(0)
            
            revised_list = []
            for sh in objnamelist:
                revised_list.append(str(sh))
            self.ds.object_names = revised_list
        
        if self.have_var_names:
            varnamelist = data_sheet.row_values(0)
            varnamelist.pop(0)
            
            c_table.pop(0)
            
            revised_list = []
            for sh in varnamelist:
                revised_list.append(str(sh))
            self.ds.variable_names = revised_list

        full_table = np.array(c_table)

        self.ds.matrix = full_table
        return self.ds

#        if self.have_var_names:
#            varnames = list(pd.dtype.names)
#            if self.have_obj_names:
#                corner = varnames.pop(0)
#                objnames = pd[corner].view().reshape(len(pd),-1)
#                objnames = objnames[:,0].tolist()
#                self.ds.object_names = objnames
#                print objnames
#            dt = pd[varnames[0]].dtype
#            pd = pd[varnames].view(dt).reshape(len(pd),-1)
#            self.ds.variable_names = varnames
#            print varnames
#        print pd
#        self.ds.matrix = pd
#        return self.ds
#
#        if self.have_var_names:
#            varnames = list(pd.dtype.names)
#            if self.have_obj_names:
#                corner = varnames.pop(0)
#                objnames = pd[corner].view().reshape(len(pd),-1)
#                objnames = objnames[:,0].tolist()
#                self.ds.object_names = objnames
#                print objnames
#            dt = pd[varnames[0]].dtype
#            pd = pd[varnames].view(dt).reshape(len(pd),-1)
#            self.ds.variable_names = varnames
#            print varnames
#        print pd
#        self.ds.matrix = pd
#        return self.ds

        

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

    pre_view = View(
        Group(
            Item('file_path', style='readonly'),
            Item('handler._parsed_data',
                 id='table',
                 editor=preview_table),
#            Item('separator',
#                 editor=EnumEditor(
#                     values={
#                         '\t': '1:Tab',
#                         ',' : '2:Comma',
#                         ' ' : '3:Space',
#                         }),
#                 style='custom',
#                 ),
            #Item('decimal_mark'),
            ## Item('transpose'),
            Item('ds_id', style='readonly', label='File name'),
            Item('ds_name', label='Dataset name'),
            Item('ds_type', label='Dataset type'),
            Item('have_var_names', label='Have variables names?',
                 tooltip='Is first row variables names?'),
            Item('have_obj_names', label='Have object names?',
                 tooltip='Is first column object names?'),
            show_labels=True,
            ),
        title='Raw data preview',
        width=0.60,
        height=0.70,
        resizable=True,
        buttons=[CancelButton, OKButton],
        handler=preview_handler,
        kind='livemodal',
        )
    
# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    test = ImporterXlsFile(file_path=(os.path.join('datasets', 'Cheese', 'ConsumerValues.xls')))
    test.import_data()