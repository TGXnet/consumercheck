"""Dataset matrix module.

"""

# Enthought imports
from traits.api import \
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
    is_calculated
      Is this dataset calculated in this application
    source_file
      Data source (file name)
    variable_names
      Column headers
    object_names
      Row headers
    n_rows
      Number of objects
    n_cols
      Number of variables

    """
    matrix = Array(desc = 'Data matrix')
    # FIXME: Public
    _ds_id = Str('unnamed', label = 'Dict key name')
    # FIXME: Public
    _ds_name = Str(
        'Unnamed dataset',
        desc = 'User friendly display name',
        label = 'Dataset name')
    _dataset_type = Enum(
        ('Design variable',
         'Sensory profiling',
         'Consumer liking',
         'Consumer attributes',
         'Hedonic attributes',),
        desc = 'Classify dataset',
        label = 'Dataset type')
    _source_file = File(label = 'Source file')
    variable_names = ListStr(desc = 'Variable names')
    object_names = ListStr(desc = 'Object names')
    _is_calculated = Bool(False, lable='Calculated?')
    n_rows = Property(label = 'Rows', desc = 'Number of objects')
    n_cols = Property(label = 'Cols', desc = 'Number of variables')

    def _get_n_rows(self):
        if self.matrix.shape[0] > 0:
            return self.matrix.shape[0]
        else:
            return 0

    def _get_n_cols(self):
        if self.matrix.shape[0] > 0:
            return self.matrix.shape[1]
        else:
            return 0

#end DataSet
