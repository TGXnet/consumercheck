
from traits.api import HasTraits, Str, List, Bool, Any, Event, on_trait_change
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
    # ck1, ck2, ...
    ck_ = Bool(False)


class CombinationTable(HasTraits):
    row_set = List()
    col_set = List()
    rows = List(Row)
    cols = List()
    selected_row = Any()
    combination_updated = Event()


    def get_selected_combinations(self):
        combinations = []
        for row in self.rows:
            for i, cn in enumerate(self.col_set):
                an = 'ck{0}'.format(i)
                if getattr(row, an):
                    cmb = (row.name, cn)
                    combinations.append(cmb)
        return combinations


    @on_trait_change('selected_row')
    def _selection_changed(self, new):
        if new:
            self.combination_updated = True


    @on_trait_change('combination_updated')
    def _comb_upd(self):
        print(self.get_selected_combinations())


    @on_trait_change('row_set,col_set')
    def _update_combinations(self):
        self._generate_combinations()
        self._define_columns()


    def _generate_combinations(self):
        self.rows = []
        for row in self.row_set:
            ro = Row()
            ro.name = row
            for i in range(len(self.col_set)):
                an = 'ck{0}'.format(i)
                setattr(ro, an, False)
            self.rows.append(ro)


    def _define_columns(self):
        self.cols = []
        oc = ObjectColumn(name='name')
        self.cols.append(oc)
        for i, cn in enumerate(self.col_set):
            cc = CheckboxColumn()
            cc.name = 'ck{0}'.format(i)
            cc.label = cn
            self.cols.append(cc)


    traits_view = View(
        Item('rows',
             editor=table_editor,
             show_label=False),
        resizable=True,
        ## width=300,
        ## height=200,
        )


if __name__ == '__main__':
    print("Test start")
    row = ['alfa', 'bravo', 'charlie']
    col = ['one', 'two', 'three']
    comb = CombinationTable(
        row_set=row,
        col_set=col
        )
    comb.configure_traits()
