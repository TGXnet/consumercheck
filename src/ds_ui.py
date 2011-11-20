
# Enthought imports
from traits.api import Button
from traitsui.api import Handler, View, Item
from traitsui.menu import OKButton, CancelButton

# Local imports
from dataset import DataSet
from ds_matrix_view import matrix_view


class DSListTabHandler(Handler):
    show_matrix = Button('Show data matrix')

    def handler_show_matrix_changed(self, info):
        info.object.edit_traits(view=matrix_view)


ds_list_tab = View(
    Item('_ds_name'),
    Item('_dataset_type'),
    Item('n_rows', style='readonly'),
    Item('n_cols', style='readonly'),
    Item('handler.show_matrix'),
    handler=DSListTabHandler(),
    )


if __name__ == '__main__':
    from importer_main import ImporterMain
    fi = ImporterMain()
    ds = fi.import_data('./datasets/Vine/A_labels.txt', True, True)
    ds.configure_traits(view=ds_list_tab)
