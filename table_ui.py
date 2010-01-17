
# Enthought imports
# FIXME: Just for testing
from numpy import array, ndarray, zeros
from enthought.traits.api import Array

from enthought.traits.api \
    import HasTraits, Instance
from enthought.traits.ui.api \
    import View, Item
from enthought.traits.ui.menu \
    import OKButton
from enthought.traits.ui.ui_editors.array_view_editor \
    import ArrayViewEditor

#Local imports
from dataset import DataSet


class MatrixView(HasTraits):
    """Separate table view for the dataset matrix."""
    theDataset = Instance(DataSet)
#    _matrix = DelegatesTo('theDataset')
    _matrix = Array(value = array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))

    traits_view = View(Item(name='_matrix',
                            editor = ArrayViewEditor()
                            ),
                       resizable = True, 
                       buttons = [OKButton]
                       )

