# coding=utf-8


# Enthought imports
from enthought.traits.ui.api import View, Group, Item
from enthought.traits.ui.menu import OKButton, CancelButton

# Local imports
from ds import DataSet





dsview = View(
    Item(name = '_internalName'),
    Item(name = '_displayName'),
    Item(name = '_datasetType'),
    Item(name = '_matrixColumnHeader'),
    Item(name = '_isCalculated'),
    buttons = [OKButton, CancelButton])


ds_list_tab = View(
    Item(name = '_displayName'),
    Item(name = '_datasetType'),
    Item(name = 'nRows', style = 'readonly'),
    Item(name = 'nCols', style = 'readonly'),
    )




# Application entry point.
if __name__ == "__main__":
    tv = DataSet()
    tv.importDataset('./testdata/Ost.txt', True)
    tv._displayName = 'Oste test'
    tv.configure_traits(view=ds_list_tab)
