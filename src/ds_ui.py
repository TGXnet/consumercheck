
# Enthought imports
from traits.api import Button
from traitsui.api import Handler, View, Item
from traitsui.menu import OKButton, CancelButton

# Local imports
from dataset import DataSet
from ds_matrix_view import matrix_view
from ds_slicer_view import ds_slicer_view


class DSListTabHandler(Handler):
    show_matrix = Button('Show data matrix')
    show_slicer = Button('Variables and objects selection')

    def handler_show_matrix_changed(self, info):
        info.object.edit_traits(view=matrix_view)

    def handler_show_slicer_changed(self, info):
        info.object.edit_traits(view=ds_slicer_view)


ds_list_tab = View(
    Item('_ds_name'),
    Item('_dataset_type'),
    Item('n_rows', style='readonly'),
    Item('n_cols', style='readonly'),
    Item('handler.show_matrix'),
    Item('handler.show_slicer'),
    handler=DSListTabHandler(),
    )


if __name__ == '__main__':
    from importer_main import ImporterMain
    fi = ImporterMain()
    ds = fi.import_data('./datasets/Vine/A_labels.txt', True, True)
    ds.configure_traits(view=ds_list_tab)
