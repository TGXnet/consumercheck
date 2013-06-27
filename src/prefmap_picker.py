from traits.api import HasTraits, Int, Str, List, Bool, Any, Event, on_trait_change, Tuple, Button
from traitsui.api import View, Item, TableEditor, CheckListEditor, Group
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn


class PrefmapPicker(HasTraits):
    row_set = List(Tuple())
    col_set = List(Tuple())
    sel_row = List()
    sel_col = List()
    combinations = List(Tuple())
    combination_updated = Event()
    get_selected = Button('Update')


    def get_selected_combinations(self):
        return self.combinations


    traits_view = View(
        Group(
            Item('sel_row', editor=CheckListEditor(name='row_set'), style='custom'),
            Item('sel_col', editor=CheckListEditor(name='col_set'), style='custom'),
            orientation='horizontal',
        ),
        Item('get_selected'),
        resizable=True,
        )


    test_view = View(
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
    comb = PrefmapPicker(
        row_set = row,
        col_set = col)
    comb.on_trait_change(test_print, 'combination_updated')
    comb.configure_traits(view='traits_view')
