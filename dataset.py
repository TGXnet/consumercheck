# coding=utf-8

# Enthought imports
from numpy import array, ndarray, zeros
from enthought.traits.api import \
    HasTraits, Array, String, Str, Enum, File, ListStr,\
    Bool, DelegatesTo, Instance
from enthought.traits.ui.api import View, Item, Group
from enthought.traits.ui.menu import OKButton, CancelButton

# Local imports
from import_data import FileData


class DataSet(HasTraits):
    """One dataset

    Dataset model class. Consist of matrix and various metadata:
    * Internal technical name
    * Userfriendly display name
    * Type of data classification
    * Named subset (FIXME: Maybe this shoud be classified as well?)
    * Is this dataset calculated in this application
    * Data source (file name)
    * Column headers
    * Active (FIXME: shoud be part of the specific algorithm/method)
    """

    # The data read from the file
    _matrix = Array(desc='Data matrix')

    # Used as dictionary index
    _internalName = String('',
                           label='Dict key name')

    # Displayed to the user
    _displayName = Str('Unamed dataset',
                       desc='User friendly display name',
                       label='Dataset name')

    # Type of data (classification) indicated by the user
    _datasetType = Enum(('Design variable',
                         'Sensory profiling',
                         'Consumer liking',
                         'Consumer attributes',
                         'Hedonic attributes',),
                        desc='Classify dataset',
                        label='Dataset type'
                        )

    # Where the matrix is imported from (datasource)
    _sourceFile = File('./Ost.txt', label='Open file')

    # List of sting containing column headers for matrix
    _matrixColumnHeader = ListStr(desc='Matrix column headers')

    # Is this dataset result of calculation in this application
    _isCalculated = Bool(False, lable='Calculated?')

    # Is this dataset part of the active calculation
    _isActive = Bool(True, label='Used in calculation?')



    def importDataset(self):
        """ Initiaze dataimport from file"""
        txtImporter = FileData(self._sourceFile)
        self._matrixColumnHeader = txtImporter.getColumnHeader()
        self._matrix = txtImporter.getMatrix()





datasetPanelView = View(Item(name = '_internalName'),
                        Item(name = '_displayName'),
                        Item(name = '_datasetType'),
                        Item(name = '_matrixColumnHeader'),
                        Item(name = '_isCalculated'),
                        Item(name = '_isActive'),
                        buttons = [OKButton, CancelButton])



dualView = View(
    Group(
        Group(Item('set1._internalName'),
              Item('set1._displayName'),
              Item('set1._datasetType'),
              Item('set1._matrixColumnHeader'),
              Item('set1._isCalculated'),
              Item('set1._isActive')
              ),
        Group(Item('set2._internalName'),
              Item('set2._displayName'),
              Item('set2._datasetType'),
              Item('set2._matrixColumnHeader'),
              Item('set2._isCalculated'),
              Item('set2._isActive')
              ),
        orientation = 'horizontal'
        ),
    title = 'Test Sets',
    buttons = [OKButton, CancelButton])





# Application entry point.
if __name__ == "__main__":
    # import sys
    ts1 = DataSet()
    ts2 = DataSet()
    ts1.configure_traits(view=dualView, context={'set1':ts1,
                                                 'set2':ts2})
