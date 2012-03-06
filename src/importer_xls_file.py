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
from traits.api import implements, HasTraits, File, Bool, Property, Str, Enum, Int, List, Color
from traitsui.api import View, Group, Item, TabularEditor, EnumEditor, Handler
from traitsui.tabular_adapter import TabularAdapter
from traitsui.menu import OKButton, CancelButton

# Local imports
from importer_interfaces import IDataImporter
from dataset import DataSet

#Import NumPy
import numpy as np


class RawLineAdapter(TabularAdapter):
    ncols = Int()
    have_var_names = Bool(True)
    bg_color  = Property()
    # font = 'Courier 10'

    def _get_bg_color(self):
        if self.have_var_names and self.row == 0:
            return (230, 123, 123)
        elif self.row == 0:
            return (255, 255, 255)


    def _ncols_changed(self, info):
        self.columns = ["col{}".format(i) for i in range(self.ncols)]

preview_table = TabularEditor(
    adapter=RawLineAdapter(),
    operations=[],
    )


class FilePreviewer(Handler):
    _raw_lines = List(List)
    _parsed_data = List()

    def init(self, info):
        info.object.make_ds_name()
        self._probe_read(info.object)

    def object_have_var_names_changed(self, info):
        preview_table.adapter.have_var_names = info.object.have_var_names
        
#    def object_have_obj_names_changed(self, info):
#        preview_table.adapter.have_obj_names = info.object.have_obj_names

    def _probe_read(self, obj, no_lines=100, length=7):
        lines = []  
        raw_data = xlrd.open_workbook(obj.file_path)
        data_sheet = raw_data.sheet_by_index(0)
        
        if data_sheet.nrows < no_lines:
            no_lines = data_sheet.nrows
        if data_sheet.ncols < length:
            length = data_sheet.ncols

        preview_table.adapter.ncols = length

        c_table = []
        for x in range(no_lines):
            c_row = []
            for y in range(length):
                c_row.append((data_sheet.cell_value(x,y)))
            c_table.append(c_row)
        self._parsed_data = self._raw_lines = c_table


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
                cell = data_sheet.cell_value(x,y)
                if isinstance( cell, basestring ):
                    cell = cell.encode("utf-8")
                c_row.append((cell))
            c_table.append(c_row)
        
        if self.have_obj_names:
            objnamelist = data_sheet.col_values(0)
            objnamelist.pop(0)
            
            for i in range(1,len(c_table)):
                c_table[i].pop(0)
            
            revised_list = []
            for sh in objnamelist:
                revised_list.append(sh)
            self.ds.object_names = revised_list
        
        if self.have_var_names:
            varnamelist = data_sheet.row_values(0)
            
            c_table.pop(0)
            
            revised_list = []
            for sh in varnamelist:
                revised_list.append(sh)
            self.ds.variable_names = revised_list

        full_table = np.array(c_table)

        self.ds.matrix = full_table
        return self.ds


    pre_view = View(
        Group(
            Item('file_path', style='readonly'),
            Item('handler._parsed_data',
                 id='table',
                 editor=preview_table),
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
        width=0.30,
        height=0.35,
        resizable=True,
        buttons=[CancelButton, OKButton],
        handler=preview_handler,
        kind='livemodal',
        )


# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    test = ImporterXlsFile()
    test.file_path = (os.path.join('datasets', 'Cheese', 'ConsumerLiking.xls'))
    test.configure_traits()
