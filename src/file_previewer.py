
# stdlib imports
import logging
# Log everything, and send it to stderr.
# http://docs.python.org/howto/logging-cookbook.html
logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.WARNING)

from traits.api \
    import HasTraits, Str, Int, Bool, File, List, Enum, on_trait_change

from traitsui.api \
    import View, Group, Item, TabularEditor, EnumEditor, ModelView

from traitsui.tabular_adapter \
    import TabularAdapter

#-- Tabular Adapter Definition -------------------------------------------------


class ImportFileParameters(HasTraits):
    file_path = File()
    separator = Enum(' ', '\t', ',')
    decimal_mark = Enum('period', 'comma')
    transpose = Bool()
    have_var_names = Bool(True)
    have_obj_names = Bool(True)
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


class FilePreviewer(ModelView):
    _raw_lines = List(Str)
    _parsed_data = List()
    adapter=RawLineAdapter()
    preview_table = TabularEditor(
        adapter=adapter,
        operations=[],
        )


    def init(self, info):
        self._probe_read()
        self._parse(self, 'no', self.model.separator)

    @on_trait_change('model:separator')
    def _parse(self, obj, name, new):
        self._parsed_data = [line.split(new) for line in self._raw_lines]
        self.adapter.ncols = len(self._parsed_data[1])

    def _probe_read(self, no_lines=7, length=35):
        lines = []
        with open(self.model.file_path, 'rU') as fp:
            for i in range(no_lines):
                line = fp.readline(length)
                if not ('\r' in line or '\n' in line):
                    fp.readline()
                logging.debug("linje {}: {}".format(i, line.rstrip('\n')))
                lines.append(line.rstrip('\n'))
        self._raw_lines = lines


    pre_view = View(
        Group(
            Item('_parsed_data',
                 id='table',
                 editor=preview_table),
            Item('model.separator',
                 editor=EnumEditor(
                     values={
                         ' ' : '1:Space',
                         '\t': '2:Tab',
                         ',' : '3:Comma',
                         }),
                 style='custom',
                 ),
            Item('model.decimal_mark'),
            Item('model.have_var_names'),
            Item('model.have_obj_names'),
            Item('model.transpose'),
            show_labels=True,
            ),
        title='Raw data preview',
        width=0.60,
        height=0.70,
        resizable=True,
        )


# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    test = ImportFileParameters()
    test.file_path = 'datasets/A_labels.txt'
    demo = FilePreviewer()
    demo.model = test
    demo.configure_traits()
