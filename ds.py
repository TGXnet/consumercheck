# coding=utf-8

# Python SL imports
from os import path

# Enthought imports
from numpy import array, ndarray, zeros
from enthought.traits.api import \
    HasTraits, Array, String, Str, Enum, File, ListStr, Bool, Property


# Local imports
from file_import import FileData


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
    _internalName = String('test1',
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
    _sourceFile = File('./testdata/test.txt', label='Open file')

    # List of sting containing column headers for matrix
    _matrixColumnHeader = ListStr(desc='Matrix column headers')

    # Is this dataset result of calculation in this application
    _isCalculated = Bool(False, lable='Calculated?')

    # Matrix dimensions
    nRows = Property(label='Rows', desc='Number of objects')
    nCols = Property(label='Cols', desc='Number of variables')


    def importDataset(self, fileUri, colHead = True):
        """ Initiaze dataimport from file"""
        self._sourceFile = fileUri
        txtImporter = FileData(self._sourceFile, colHead)
        self._matrixColumnHeader = txtImporter.getColumnHeader()
        self._matrix = txtImporter.getMatrix()
        # FIXME: Find a better more general solution
        fn = path.basename(fileUri)
        fn = fn.partition('.')[0]
        fn = fn.lower()
        self._internalName = fn

    def _get_nRows(self):
        if self._matrix.shape[0]>0:
            return self._matrix.shape[0]
        else:
            return 0
        
    def _get_nCols(self):
        if self._matrix.shape[0]>0:
            return self._matrix.shape[1]
        else:
            return 0



# Application entry point.
if __name__ == "__main__":
    # import sys
    ts1 = DataSet()
    ts1.importDataset('./testdata/Ost.txt', True)
    ts1._displayName = 'Oste test'
    ts1.print_traits()
