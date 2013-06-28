from traits.api import HasTraits, List, Event, on_trait_change, Tuple, Button
from traitsui.api import View, Item, CheckListEditor, Group, Label


class PrefmapPicker(HasTraits):
    row_set = List(Tuple())
    col_set = List(Tuple())
    sel_row = List()
    sel_col = List()
    combinations = List(Tuple())
    combination_updated = Event()
    get_selected = Button('Add mapping')


    @on_trait_change('get_selected')
    def _new_selection(self, obj, name, old_value, new_value):
        sel = (self.sel_row[0], self.sel_col[0])
        print("The sel", sel)
        self.combinations.append(sel)
        self.sel_row = []
        self.sel_col = []
        self.combination_updated = True


    def get_selected_combinations(self):
        return self.combinations


    traits_view = View(
        Group(
            Group(
                Label('Liking data'),
                Item('sel_row', editor=CheckListEditor(name='row_set'),
                     style='simple', show_label=False),
                orientation='vertical',
                ),
            Group(
                Label('Sensory data'),
                Item('sel_col', editor=CheckListEditor(name='col_set'),
                     style='simple', show_label=False),
                orientation='vertical',
                ),
            orientation='horizontal',
        ),
        Item('get_selected', show_label=False),
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
