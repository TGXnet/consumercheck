'''ConsumerCheck
'''
#-----------------------------------------------------------------------------
#  Copyright (C) 2014 Thomas Graff <thomas.graff@tgxnet.no>
#
#  This file is part of ConsumerCheck.
#
#  ConsumerCheck is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  ConsumerCheck is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ConsumerCheck.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------

# Std lib imports
import logging
logger = logging.getLogger('tgxnet.nofima.cc.'+__name__)
import os.path

# Scipy imports
# import numpy as np
import pandas as _pd
import xlrd

# Enthought imports
from traits.api import implements, HasTraits, File, Bool, Str, Int, List
from traitsui.api import View, Group, Item, TabularEditor, EnumEditor, Handler
from traitsui.tabular_adapter import TabularAdapter
from traitsui.menu import OKButton, CancelButton

# Local imports
from dataset import DataSet
from importer_interfaces import IDataImporter
from importer_file_base import ImporterFileBase


class RawLineAdapter(TabularAdapter):
    ncols = Int()
    
    #Temporary column to avoid crash
    columns = ['tmp']
    
    have_var_names = Bool(True)
    
#    bg_color  = Property()
#    # font = 'Courier 10'
#
#    def _get_bg_color(self):
#        if self.have_var_names and self.row == 0:
#            return (230, 123, 123)
#        elif self.row == 0:
#            return (255, 255, 255)


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
                c_row.append(data_sheet.cell_value(x,y))
            c_table.append(c_row)
        self._parsed_data = self._raw_lines = c_table


preview_handler = FilePreviewer()



class ImporterXlsFile(ImporterFileBase):
    implements(IDataImporter)


    def import_data(self):
        self.ds = DataSet(
            kind=self.kind,
            display_name=self.ds_name
            )

        xls = _pd.ExcelFile(self.file_path)
        sheet_name = xls.sheet_names[0]
        if self.have_obj_names:
            ic = 0
        else:
            ic = None
        if self.have_var_names:
            hd = 0
        else:
            hd = None
        matrix = xls.parse(sheet_name, header=hd, index_col=ic)
        self.ds.mat = matrix

        return self.ds


    pre_view = View(
        Group(
            Item('file_path', style='readonly'),
            Item('handler._parsed_data',
                 id='table',
                 editor=preview_table),
            ## Item('transpose'),
            Item('ds_name', label='Data set name'),
            Item('kind', editor=EnumEditor(name='kind_list'), label='Data set type'),
            Item('have_var_names', label='Existing variable names',
                 tooltip='Is first row variables names?'),
            Item('have_obj_names', label='Existing object names',
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
