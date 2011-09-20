
# Enthought imports
from enthought.traits.ui.api import View, Item
from enthought.traits.ui.menu import OKButton, CancelButton


dsview = View(
    Item(name = '_ds_id'),
    Item(name = '_ds_name'),
    Item(name = '_datasetType'),
    Item(name = 'variableNames'),
    Item(name = 'objectNames'),
    Item(name = '_isCalculated'),
    buttons = [OKButton, CancelButton])


ds_list_tab = View(
    Item(name = '_ds_name'),
    Item(name = '_datasetType'),
    Item(name = 'nRows', style = 'readonly'),
    Item(name = 'nCols', style = 'readonly'),
    )
