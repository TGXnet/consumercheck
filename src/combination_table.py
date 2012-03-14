
from traits.api import HasTraits, Str, List, Bool, Any, Event, on_trait_change, Tuple
from traitsui.api import View, Item, TableEditor
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn


table_editor = TableEditor(
    columns_name='cols',
    editable=False,
    # show_row_labels=True,
    sortable=False,
    selection_mode='row',
    selected='selected_row',
    )


class Row(HasTraits):
    name = Str()
    nid = Str()
    # ck1, ck2, ...
    ck_ = Bool(False)


class CombinationTable(HasTraits):
    row_set = List(Tuple())
    col_set = List(Tuple())
    rows = List(Row)
    cols = List()
    selected_row = Any()
    combination_updated = Event()


    def __init__(self, *args, **kwargs):
        super(CombinationTable, self).__init__(*args, **kwargs)
        self._generate_combinations()


    def get_selected_combinations(self):
        combinations = []
        for row in self.rows:
            for i, cn in enumerate(self.col_set):
                an = 'ck{0}'.format(i)
                if getattr(row, an):
                    cmb = (row.nid, cn[0])
                    combinations.append(cmb)
        return combinations

    def update_names(self):
        for i in self.row_set:
            for row in self.rows:
                if row.nid == i[0]:
                    row.name = i[1]
        for i,col in enumerate(self.col_set):
            self.cols[i+1].label = col[1]

    @on_trait_change('selected_row')
    def _selection_changed(self, new):
        if new:
            self.combination_updated = True

    def _generate_combinations(self):
        if not self.row_set:
            self.row_set.append(('a',''))
        self.rows = []
        for row in self.row_set:
            ro = Row()
            ro.nid = row[0]
            ro.name = row[1]
            for i in range(len(self.col_set)):
                an = 'ck{0}'.format(i)
                setattr(ro, an, False)
            self.rows.append(ro)
        self._define_columns()


    def _define_columns(self):
        self.cols = []
        oc = ObjectColumn(name='name')
        self.cols.append(oc)
        for i, cn in enumerate(self.col_set):
            cc = CheckboxColumn()
            cc.name = 'ck{0}'.format(i)
            cc.label = cn[1]
            self.cols.append(cc)


    traits_view = View(
        Item('rows',
             editor=table_editor,
             show_label=False),
        resizable=True,
        )

    test_view = View(
        Item('rows',
             editor=table_editor,
             show_label=False),
        resizable=True,
        width=300,
        height=200,
        )


if __name__ == '__main__':
    print("Test start")
    row = ['alfa', 'bravo', 'charlie']
    col = ['one', 'two', 'three']
    comb = CombinationTable()
        ## row_set = row,
        ## col_set = col)
    comb.configure_traits(view='test_view')
