"""Dataset matrix module.

"""

# Enthought imports
from enthought.traits.api import \
    HasTraits, Array, Str, Enum, File, ListStr, Bool, Property


class DataSet(HasTraits):
    """One data matirx

    Consist of matrix and metadata

    Members
    =======

    matrix
      The data matrix
    internalName
      Internal technical name
    displayName
      Userfriendly display name
    datasetType
      Type of data classification
    isCalculated
      Is this dataset calculated in this application
    sourceFile
      Data source (file name)
    variableNames
      Column headers
    objectNames
      Row headers
    nRows
      Number of objects
    nCols
      Number of variables

    """
    matrix = Array(desc = 'Data matrix')
    # FIXME: Public
    _ds_id = Str('unnamed', label = 'Dict key name')
    # FIXME: Public
    _displayName = Str(
        'Unnamed dataset',
        desc = 'User friendly display name',
        label = 'Dataset name')
    _datasetType = Enum(
        ('Design variable',
         'Sensory profiling',
         'Consumer liking',
         'Consumer attributes',
         'Hedonic attributes',),
        desc = 'Classify dataset',
        label = 'Dataset type')
    _sourceFile = File(label = 'Source file')
    variableNames = ListStr(desc = 'Variable names')
    objectNames = ListStr(desc = 'Object names')
    _isCalculated = Bool(False, lable='Calculated?')
    nRows = Property(label = 'Rows', desc = 'Number of objects')
    nCols = Property(label = 'Cols', desc = 'Number of variables')

    def _get_nRows(self):
        if self.matrix.shape[0]>0:
            return self.matrix.shape[0]
        else:
            return 0

    def _get_nCols(self):
        if self.matrix.shape[0]>0:
            return self.matrix.shape[1]
        else:
            return 0

    def isEqDisplayName(self, name):
        return name == self._displayName

#end DataSet
