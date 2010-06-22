# coding=utf-8

# Python stdlib imports
from os import path

# Enthought imports
from numpy import array, ndarray, zeros
from enthought.traits.api import \
    HasTraits, Array, String, Str, Enum, File, ListStr, Bool, Property


# Local imports
from file_importer import FileImporter


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
    """

    # The data read from the file
    _matrix = Array(desc = 'Data matrix')

    # Used as dictionary index
    _internalName = String('unnamed', label = 'Dict key name')

    # Displayed to the user
    _displayName = Str(
        'Unnamed dataset',
        desc = 'User friendly display name',
        label = 'Dataset name')

    # Type of data (classification) indicated by the user
    _datasetType = Enum(
        ('Design variable',
         'Sensory profiling',
         'Consumer liking',
         'Consumer attributes',
         'Hedonic attributes',),
        desc = 'Classify dataset',
        label = 'Dataset type')

    # Where the matrix is imported from (datasource)
    _sourceFile = File(label = 'Source file')

    # List of sting containing column headers for matrix
    variableNames = ListStr(desc = 'Variable names')
    objectNames = ListStr(desc = 'Object names')

    # Is this dataset result of calculation in this application
    _isCalculated = Bool(False, lable='Calculated?')

    # Matrix dimensions
    nRows = Property(label = 'Rows', desc = 'Number of objects')
    nCols = Property(label = 'Cols', desc = 'Number of variables')


    def importDataset(self, fileUri, haveVarNames = True, haveObjNames = False):
        """ Initiaze dataimport from file"""
        self._sourceFile = fileUri
        txtImporter = FileImporter(self._sourceFile, haveVarNames, haveObjNames)
        txtImporter.readFile()
        self._matrix = txtImporter.getMatrix()

        if haveVarNames:
            self.variableNames = txtImporter.getVariableNames()
        if haveObjNames:
            self.objectNames = txtImporter.getObjectNames()

        # FIXME: Find a better more general solution
        fn = path.basename(fileUri)
        fn = fn.partition('.')[0]
        fn = fn.lower()
        self._internalName = self._displayName = fn


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


    def isEqDisplayName(self, name):
        return name == self._displayName


#end DataSet
