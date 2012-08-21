
# StdLib imports
import os.path
from StringIO import StringIO
from codecs import open as unicode_open
import logging
# Log everything, and send it to stderr.
# http://docs.python.org/howto/logging-cookbook.html
# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.WARNING)

# About text encoding
# There are 2 ways of determin the encodings for text files.
# 1. To know in advance
# 2. To make a correct guess

# SciPy imports
from numpy import genfromtxt

# Enthought imports
from traits.api import HasTraits, Event, Str, Unicode, Int, Bool, File, List, Enum, Property
from traitsui.api import View, Group, Item, TabularEditor, EnumEditor, Handler
from traitsui.menu import OKButton, CancelButton
from traitsui.tabular_adapter import TabularAdapter
from traits.api import implements

# Local imports
from dataset import DataSet
from importer_interfaces import IDataImporter


class RawLineAdapter(TabularAdapter):
    ncols = Int()
    
    #Temporary column to avoid crash
    columns = ['tmp']
    
    have_var_names = Bool(True)
    
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
        info.object.make_ds_name()
        self._probe_read(info.object)
        self._decode_chars(info.object.char_encoding)


    def object_have_var_names_changed(self, info):
        preview_table.adapter.have_var_names = info.object.have_var_names
        preview_table.update_cells = True


    def object_separator_changed(self, info):
        self._split_table(info.object.separator)


    def _split_table(self, separator):
        preview_matrix = [line.split(separator) for line in self._unicode_lines]
        max_cols = 7
        for row in preview_matrix:
            max_cols = min(max_cols, len(row))
        self._parsed_data = self._fix_preview_matrix(preview_matrix, max_cols)
        preview_table.adapter.ncols = max_cols


    def object_char_encoding_changed(self, info):
        self._decode_chars(info.object.char_encoding)
        self._split_table(info.object.separator)


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
    separator = Enum('\t', ',', ' ')
    decimal_mark = Enum('period', 'comma')
    char_encoding = Enum(
        ('ascii', 'utf_8', 'latin_1')
        )
    transpose = Bool(False)
    have_var_names = Bool(True)
    have_obj_names = Bool(True)
    ds_id = Str()
    ds_name = Str()
    ds_type = Str()
    ds_type_list = List(['Design variable', 'Sensory profiling', 'Consumer liking', 'Consumer attributes'])

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

        # Read data from file
        with unicode_open(self.file_path,
                          encoding=self.char_encoding,
                          errors='strict') as fp:
            unicode_data = fp.read()
        utf_8_data = unicode_data.encode('utf-8', 'strict')

        # Preprocess file utf_8_data
        if self.decimal_mark == 'comma':
            if self.separator == ',':
                raise Exception('Ambiguous fileformat')
            utf_8_data = utf_8_data.replace(',', '.')

        # Do we have variable names
        names = None
        skip_header = 0
        if self.have_var_names:
            # names = True
            fl, rest = utf_8_data.split('\n', 1)
            names = fl.split(self.separator)
            skip_header = 1

        pd = genfromtxt(
            StringIO(utf_8_data),
            dtype=None,
            delimiter=self.separator,
            skip_header = skip_header,
            names=names)

        if self.have_var_names:
            varnames = list(pd.dtype.names)
            if self.have_obj_names:
                corner = varnames.pop(0)
                objnames = pd[corner].view().reshape(len(pd),-1)
                objnames = objnames[:,0].tolist()
                self.ds.object_names = [unicode(on).decode('utf-8') for on in objnames]

            dt = pd[varnames[0]].dtype
            pd = pd[varnames].view(dt).reshape(len(pd),-1)
            self.ds.variable_names = [vn.decode('utf-8') for vn in varnames]

        self.ds.matrix = pd
        return self.ds

    pre_view = View(
        Group(
            Item('file_path', style='readonly'),
            Item('handler._parsed_data',
                 id='table',
                 editor=preview_table),
            Item('char_encoding'),
            Item('separator',
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
            Item('ds_id', style='readonly', label='File name'),
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
    test = ImporterTextFile()
    test.file_path = 'datasets/Variants/ObjVarNames.txt'
    # test.file_path = 'datasets/Variants/Names_UTF-8.txt'
    # test.file_path = 'datasets/Variants/Names_iso-8859-1.txt'
    test.configure_traits()
    ds = test.import_data()
    ds.print_traits()
