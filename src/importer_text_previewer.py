
# StdLib imports
import os.path
from StringIO import StringIO
import logging
# Log everything, and send it to stderr.
# http://docs.python.org/howto/logging-cookbook.html
# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.WARNING)

# SciPy imports
from numpy import array, loadtxt, genfromtxt

# Enthought imports
from traits.api import HasTraits, Str, Int, Bool, File, List, Enum
from traitsui.api import View, Group, Item, TabularEditor, EnumEditor, Handler
from traitsui.menu import OKButton, CancelButton
from traitsui.tabular_adapter import TabularAdapter
from traits.api import implements



# Local imports
from dataset import DataSet
from importer_interfaces import IDataImporter


class ImportFileParameters(HasTraits):
    implements(IDataImporter)

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

        # Read data from file
        with open(self.file_path, 'rU') as fp:
            data = fp.read()

        # Preprocess file data
        if self.decimal_mark == 'comma':
            if self.separator == ',':
                raise Exception('Ambiguous fileformat')
            data = data.replace(',', '.')

        # Do we have variable names
        if self.have_var_names:
            names = True
        else:
            names = None

        pd = genfromtxt(
            StringIO(data),
            dtype=None,
            delimiter=self.separator,
            names=names)

        if self.have_var_names:
            varnames = list(pd.dtype.names)
            if self.have_obj_names:
                corner = varnames.pop(0)
                objnames = pd[corner].view().reshape(len(pd),-1)
                objnames = objnames[:,0].tolist()
                self.ds.object_names = objnames
            dt = pd[varnames[0]].dtype
            pd = pd[varnames].view(dt).reshape(len(pd),-1)
            self.ds.variable_names = varnames

        self.ds.matrix = pd
        return self.ds




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
    test.file_path = 'datasets/Vine/A_labels.txt'
    test.configure_traits(view=pre_view)
