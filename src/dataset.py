"""Dataset matrix module.

"""

# Enthought imports
from traits.api import (HasTraits, Array, Str, Int, Enum, File,
                        List, Bool, Property, on_trait_change)


class DataSet(HasTraits):
    """One data matrix

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
         'Consumer liking',),
        desc = 'Classify dataset',
        label = 'Dataset type')
    _source_file = File(label = 'Source file')
    variable_names = List(trait=Str, desc = 'Variable names')
    object_names = List(trait=Str, desc = 'Object names')
    active_variables = List(trait=Int)
    active_objects = List(trait=Int)
    _is_calculated = Bool(False, lable='Calculated?')
    n_rows = Property(label = 'Rows', desc = 'Number of objects')
    n_cols = Property(label = 'Cols', desc = 'Number of variables')


    @on_trait_change('matrix')
    def _all_active(self):
        self.active_variables = range(self.matrix.shape[1])
        self.active_objects = range(self.matrix.shape[0])

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

    def subset(self):
        mod_ds = super(DataSet, self).clone_traits()
        mod_ds.matrix = self.matrix[self.active_objects][:,self.active_variables]
        if self.variable_names:
            mod_ds.variable_names = [self.variable_names[i] for i in self.active_variables]
        if self.object_names:
            mod_ds.object_names = [self.object_names[i] for i in self.active_objects]
        return mod_ds


#end DataSet


if __name__ == '__main__':
    from importer_main import ImporterMain
    fi = ImporterMain()
    ds = fi.import_data('./datasets/Vine/A_labels.txt', True, True)
