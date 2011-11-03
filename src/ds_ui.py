
# Enthought imports
from traitsui.api import View, Item
from traitsui.menu import OKButton, CancelButton

# Local imports
from dataset import DataSet

dsview = View(
    Item(name = '_ds_id'),
    Item(name = '_ds_name'),
    Item(name = '_dataset_type'),
    Item(name = 'variable_names'),
    Item(name = 'object_names'),
    Item(name = '_is_calculated'),
    buttons = [OKButton, CancelButton])


ds_list_tab = View(
    Item(name = '_ds_name'),
    Item(name = '_dataset_type'),
    Item(name = 'n_rows', style = 'readonly'),
    Item(name = 'n_cols', style = 'readonly'),
    )
