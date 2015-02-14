from traitsui.api import View, Item, CheckListEditor, Group, Label
from prefmap_picker import PrefmapPicker


class PlscrPicker(PrefmapPicker):

    traits_view = View(
        Group(
            Group(
                Label('Matrix X'),
                Item('sel_row', editor=CheckListEditor(name='row_set'),
                     style='simple', show_label=False),
                orientation='vertical',
                ),
            Group(
                Label('Matrix Y'),
                Item('sel_col', editor=CheckListEditor(name='col_set'),
                     style='simple', show_label=False),
                orientation='vertical',
                ),
            orientation='horizontal',
        ),
        resizable=True,
        )


if __name__ == '__main__':
    print("Test start")

    def test_print():
        print(comb.get_selected_combinations())

    row = [(1, 'Alfa'), (2, 'Bravo'), (3, 'Charlie')]
    col = [(1, 'One'), (2, 'Two'), (3, 'Three')]
    comb = PlscrPicker(
        row_set=row,
        col_set=col)
    comb.on_trait_change(test_print, 'combination_updated')
    comb.configure_traits(view='traits_view')
