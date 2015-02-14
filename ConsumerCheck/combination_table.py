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

from traits.api import HasTraits, Int, Str, List, Bool, Any, Event, on_trait_change, Tuple
from traitsui.api import View, Item, TableEditor
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn


table_editor = TableEditor(
    columns_name='cols',
    selection_mode='row',
    selected='selected_row',
    )


class CombCheck(CheckboxColumn):
    horizontal_alignment='center'


class Row(HasTraits):
    name = Str()
    nid = Any()
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


    # FIXME: Implement automatic update of table based on
    # change to row and col set. But I need to implemnt this
    # and to preserv the selection already made.
    #@on_trait_change('row_set, col_set', post_init=True)
    #def _update_table(self, obj, name, new):
    #    print("Name list changed")
    #    self._generate_combinations()
    #    self.update_names()


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


    @on_trait_change('rows.ck+')
    def _selection_changed(self, obj, name, old, new):
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
        oc = ObjectColumn(name='name', editable=False)
        self.cols.append(oc)
        for i, cn in enumerate(self.col_set):
            cc = CombCheck()
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
    def test_print():
        print(comb.get_selected_combinations())

    row = [(1, 'Alfa'), (2, 'Bravo'), (3, 'Charlie')]
    col = [(1, 'One'), (2, 'Two'), (3, 'Three')]
    comb = CombinationTable(
        row_set = row,
        col_set = col)
    comb.on_trait_change(test_print, 'combination_updated')
    comb.configure_traits(view='test_view')
