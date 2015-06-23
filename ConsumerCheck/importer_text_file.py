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

# StdLib imports
import logging
logger = logging.getLogger('tgxnet.nofima.cc.'+__name__)

# SciPy imports
import pandas as _pd

# Enthought imports
from traits.api import Event, Str, Unicode, Int, List, Enum
from traitsui.api import View, Group, Item, TabularEditor, EnumEditor, Handler
from traitsui.menu import OKButton, CancelButton
from traitsui.tabular_adapter import TabularAdapter
from traits.api import implements

# Local imports
from dataset import DataSet
from importer_interfaces import IDataImporter
from importer_file_base import ImporterFileBase


class RawLineAdapter(TabularAdapter):
    ncols = Int()
    
    #Temporary column to avoid crash
    columns = ['tmp']
    
    width = 70
    # have_var_names = Bool(True)
    
#    # font = 'Courier 10'
#    bg_color  = Property()
#    
#    def _get_bg_color(self):
#        if self.have_var_names and self.row == 0:
#            return (230, 123, 123)
#        elif self.row == 0:
#            return (255, 255, 255)


    def _ncols_changed(self, info):
        self.columns = [("col{}".format(i), i) for i in range(self.ncols)]


class PreviewTableEditor(TabularEditor):
    update_cells = Event()


preview_table = PreviewTableEditor(
    adapter = RawLineAdapter(),
    operations = [],
    # Can the user edit the values?
    show_titles = True,
    # show_row_titles = False,
    editable = False,
    # The optional extended name of the trait used to indicate that a complete
    # table update is needed:
    update = 'update_cells',
    # Should the table update automatically when the table item's contents
    # change? Note that in order for this feature to work correctly, the editor
    # trait should be a list of objects derived from HasTraits. Also,
    # performance can be affected when very long lists are used, since enabling
    # this feature adds and removed Traits listeners to each item in the list.
    # auto_update = Bool( False ),
    # TabularEditorEvent
    )



class FilePreviewer(Handler):
    _raw_lines = List(Str)
    _unicode_lines = List(Unicode)
    _parsed_data = List()


    def init(self, info):
        self._probe_read(info.object)
        self._decode_chars(info.object.char_encoding)


    def object_have_var_names_changed(self, info):
        # preview_table.adapter.have_var_names = info.object.have_var_names
        preview_table.update_cells = True


    def object_delimiter_changed(self, info):
        self._split_table(info.object.delimiter)


    def _split_table(self, delimiter):
        preview_matrix = [line.split(delimiter) for line in self._unicode_lines]
        max_cols = 7
        for row in preview_matrix:
            max_cols = min(max_cols, len(row))
        self._parsed_data = self._fix_preview_matrix(preview_matrix, max_cols)
        preview_table.adapter.ncols = max_cols


    def object_char_encoding_changed(self, info):
        self._decode_chars(info.object.char_encoding)
        self._split_table(info.object.delimiter)


    def _decode_chars(self, encoding):
        self._unicode_lines = [line.decode(encoding, errors='replace') for line in self._raw_lines]


    def _fix_preview_matrix(self, preview_matrix, length):
        for i, row in enumerate(preview_matrix):
            if len(row) < length:
                preview_matrix[i] += ['']*(length-len(row))
            elif len(row) > length:
                preview_matrix[i] = preview_matrix[i][0:length]

        return preview_matrix


    def _probe_read(self, obj, n_lines=100, length=200):
        lines = []
        with open(obj.file_path, 'rU') as fp:
            for i in range(n_lines):
                line = fp.readline(length)
                if not line:
                    break
                if not ('\r' in line or '\n' in line):
                    fp.readline()
                logger.debug("linje {}: {}".format(i, line.rstrip('\n')))
                lines.append(line.rstrip('\n'))
        self._raw_lines = lines


preview_handler = FilePreviewer()



class ImporterTextFile(ImporterFileBase):
    implements(IDataImporter)

    delimiter = Enum('\t', ',', ' ', ';')
    decimal_mark = Enum('period', 'comma')
    char_encoding = Enum(
        ('ascii', 'utf_8', 'latin_1')
        )


    def import_data(self):
        """Do the importing of a data set"""

        if self.have_var_names:
            header = 'infer'
        else:
            header = None
        if self.have_obj_names:
            index_col = 0
        else:
            index_col = None

        dsdf = _pd.read_csv(
            filepath_or_buffer=self.file_path,
            delimiter=self.delimiter,
            header=header,
            index_col=index_col,
            keep_default_na=True,
            na_values=['?'],
            encoding=self.char_encoding,
            )

        # FIXME: This is hackish
        # I have to know the matrix shape to use converters
        if self.decimal_mark == 'comma':

            def c2f(a_num):
                '''Alfanumeric with comma to float'''
                return float(a_num.replace(',', '.'))

            convs = {k: c2f for k in dsdf.columns}

            dsdf = _pd.read_csv(
                filepath_or_buffer=self.file_path,
                delimiter=self.delimiter,
                header=header,
                index_col=index_col,
                keep_default_na=True,
                na_values=['?'],
                encoding=self.char_encoding,
                converters=convs,
                )


        if not self.have_var_names:
            dsdf.columns = ["V{0}".format(i+1) for i in range(dsdf.shape[1])]
        if not self.have_obj_names:
            dsdf.index = ["O{0}".format(i+1) for i in range(dsdf.shape[0])]

        # Make DataSet
        ds = DataSet(
            mat=dsdf,
            display_name=self.ds_name,
            kind=self.kind,
            )
        return ds


    traits_view = View(
        Group(
            Item('file_path', style='readonly'),
            Item('handler._parsed_data',
                 editor=preview_table,
                 id='table',
                 show_label=False,
                 ),
            Item('char_encoding'),
            Item('delimiter',
                 editor=EnumEditor(
                     values={
                         '\t': '1:Tab',
                         ',': '2:Comma (,)',
                         ' ': '3:Space',
                         ';': '4:Semicolon (;)',
                         }),
                 style='custom',
                 ),
            Item('decimal_mark'),
            ## Item('transpose'),
            Item('ds_name', label='Data set name'),
            Item('kind', editor=EnumEditor(name='kind_list'), label='Data set type'),
            Item('have_var_names', label='Existing variable names',
                 tooltip='Is first row variable names?'),
            Item('have_obj_names', label='Existing object names',
                 tooltip='Is first column object names?'),
            show_labels=True,
            ),
        title='Raw data preview',
        width=0.45,
        height=0.6,
        resizable=True,
        buttons=[CancelButton, OKButton],
        handler=preview_handler,
        kind='livemodal',
        )


# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    itf = ImporterTextFile(
        file_path='datasets/Variants/CommaSeparated.csv',
        )
    itf.configure_traits()
    ds = itf.import_data()
    print(ds.display_name)
    print(ds.mat.shape)
    print(ds.mat.index)
    print(ds.mat.columns)
    print(ds.mat.dtypes)
