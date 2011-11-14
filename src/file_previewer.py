from traits.api \
    import HasTraits, Str, Int, List, Instance, Property, Bool, Color, Enum, on_trait_change

from traitsui.api \
    import View, Group, Item, TabularEditor, EnumEditor, ModelView

from traitsui.tabular_adapter \
    import TabularAdapter

#-- Tabular Adapter Definition -------------------------------------------------


class RawLineAdapter(TabularAdapter):
    columns = []
    ncols = Int()
    # font = 'Courier 10'

    def _ncols_changed(self, info):
        self.columns = ["col{}".format(i) for i in range(self.ncols)]


class FilePreviewer(ModelView):

    parsed_data = List()
    separator = Enum(' ', '\t', ',')
    decimal_mark = Enum('period', 'comma')
    var_names = Bool()
    obj_names = Bool()
    transpose = Bool()

    adapter=RawLineAdapter()
    preview_table = TabularEditor(
        adapter=adapter,
        operations=[],
        )


    def init(self, info):
        self._parse(self, 'no', self.separator)

    @on_trait_change('separator')
    def _parse(self, obj, name, new):
        obj.parsed_data = [line.split(new) for line in obj.model._raw_lines]
        obj.adapter.ncols = len(obj.parsed_data[1])

    pre_view = View(
        Group(
            Item('parsed_data',
                 id='table',
                 editor=preview_table),
            Item('separator',
                 editor=EnumEditor(
                     values={
                         ' ' : '1:Space',
                         '\t': '2:Tab',
                         ',' : '3:Comma',
                         }),
                 style='custom',
                 ),
            Item('decimal_mark'),
            Item('var_names'),
            Item('obj_names'),
            Item('transpose'),
            show_labels=True,
            ),
        title='Raw data preview',
        width=0.60,
        height=0.70,
        resizable=True,
        )


class TestDummy(HasTraits):
    _raw_lines = List(Str)


# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    test = TestDummy()
    test._raw_lines = [
        'KIDEN\tREPOS1\tREPOS2\tREPOS3\tREPOS4\tR',
        '2EL\t3.07\t3.00\t2.71\t2.28\t1.96',
        '1CHA\t2.96\t2.82\t2.38\t2.28\t1.68',
        '1FON\t2.86\t2.93\t2.56\t1.96\t2.08',
        '1VAU\t2.81\t2.59\t2.42\t1.91\t2.16',
        '1DAM\t3.61\t3.43\t3.15\t2.15\t2.04',
        '2BOU\t2.86\t3.11\t2.58\t2.04\t2.08'
        ]
    demo = FilePreviewer(model=test)
    demo.configure_traits()
