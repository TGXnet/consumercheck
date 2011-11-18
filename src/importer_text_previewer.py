
# StdLib imports
import os.path
import logging
# Log everything, and send it to stderr.
# http://docs.python.org/howto/logging-cookbook.html
logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.WARNING)

# Enthought imports
from traits.api import HasTraits, Str, Int, Bool, File, List, Enum
from traitsui.api import View, Group, Item, TabularEditor, EnumEditor, Handler
from traitsui.menu import OKButton, CancelButton
from traitsui.tabular_adapter import TabularAdapter

# Local imports


class ImportFileParameters(HasTraits):
    file_path = File()
    separator = Enum('\t', ',', ' ')
    decimal_mark = Enum('period', 'comma')
    transpose = Bool(False)
    have_var_names = Bool(True)
    have_obj_names = Bool(True)
    ds_id = Str()
    ds_name = Str()
    ds_type = Enum(
        ('Design variable',
         'Sensory profiling',
         'Consumer liking',
         'Consumer attributes',
         'Hedonic attributes',)
        )


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
        self._make_ds_name(info.object)
        self._probe_read(info.object)

    def object_separator_changed(self, info):
        preview_matrix = [line.split(info.object.separator) for line in self._raw_lines]
        longest = 0
        for row in preview_matrix:
            longest = max(longest, len(row))
        self._parsed_data = self._fix_preview_matrix(preview_matrix, longest)
        preview_table.adapter.ncols = longest

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

    def _make_ds_name(self, obj):
        # FIXME: Find a better more general solution
        fn = os.path.basename(obj.file_path)
        fn = fn.partition('.')[0]
        fn = fn.lower()
        obj.ds_id = obj.ds_name = fn



pre_view = View(
    Group(
        Item('file_path', style='readonly'),
        Item('handler._parsed_data',
             id='table',
             editor=preview_table),
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
    handler=FilePreviewer(),
    kind='livemodal',
    )


# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    test = ImportFileParameters()
    test.file_path = 'datasets/A_labels.txt'
    test.configure_traits(view=pre_view)
