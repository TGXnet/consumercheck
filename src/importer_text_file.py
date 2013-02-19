
# StdLib imports
import os.path
import logging
# Log everything, and send it to stderr.
# http://docs.python.org/howto/logging-cookbook.html
# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.WARNING)

# SciPy imports
import pandas as _pd

# Enthought imports
from traits.api import HasTraits, Event, Str, Unicode, Int, Bool, File, List, Enum
from traitsui.api import View, Group, Item, TabularEditor, EnumEditor, Handler
from traitsui.menu import OKButton, CancelButton
from traitsui.tabular_adapter import TabularAdapter
from traits.api import implements

# Local imports
from dataset_ng import DS_TYPES, DataSet
from importer_interfaces import IDataImporter



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
    show_row_titles = False,
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


    def _probe_read(self, obj, no_lines=100, length=200):
        lines = []
        with open(obj.file_path, 'rU') as fp:
            for i in range(no_lines):
                line = fp.readline(length)
                if not line:
                    break
                if not ('\r' in line or '\n' in line):
                    fp.readline()
                logging.debug("linje {}: {}".format(i, line.rstrip('\n')))
                lines.append(line.rstrip('\n'))
        self._raw_lines = lines


preview_handler = FilePreviewer()



class ImporterTextFile(HasTraits):
    implements(IDataImporter)

    file_path = File()
    delimiter = Enum('\t', ',', ' ')
    decimal_mark = Enum('period', 'comma')
    char_encoding = Enum(
        ('ascii', 'utf_8', 'latin_1')
        )
    transpose = Bool(False)
    have_var_names = Bool(True)
    have_obj_names = Bool(True)
    ds_name = Str('Unnamed dataset')
    ds_type = Str('Design variable')
    ds_type_list = List(DS_TYPES)


    def import_data(self):
        """Do the importing of a dataset"""

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
        if self.decimal_mark == 'comma':

            def commatofloat(anum):
                return float(anum.replace(',', '.'))

            convs = {}
            for i in range(dsdf.shape[1]):
                convs[i] = commatofloat

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
            matrix=dsdf,
            display_name=self.ds_name,
            ds_type=self.ds_type,
            )
        return ds


    def _ds_name_default(self):
        # FIXME: Find a better more general solution
        fn = os.path.basename(self.file_path)
        fn = fn.partition('.')[0]
        fn = fn.lower()
        return fn


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
                         ',' : '2:Comma',
                         ' ' : '3:Space',
                         }),
                 style='custom',
                 ),
            Item('decimal_mark'),
            ## Item('transpose'),
            Item('ds_name', label='Dataset name'),
            Item('ds_type', editor=EnumEditor(name='ds_type_list'), label='Dataset type'),
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
    print(ds.matrix.shape)
    print(ds.matrix.index)
    print(ds.matrix.columns)
    print(ds.matrix.dtypes)
