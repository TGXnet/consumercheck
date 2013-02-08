"""
DataSet module
--------------

.. moduleauthor:: Thomas Graff <graff.thomas@gmail.com>

"""

# Enthought imports
from traits.api import (HasTraits, Array, Str, Int, Enum, File,
                        List, Bool, Property, on_trait_change)


DS_TYPES = ['Design variable',
            'Sensory profiling',
            'Consumer liking',
            'Consumer characteristics']


class DataSet(HasTraits):
    """Container for one array of related data.

    Consist of matrix and metadata

    Attributes:

    * matrix: The number array
    * _ds_id: *Technical* identity for this dataset.
    * _ds_name: Userfriendly name.
    * _dataset_type: Selection among predefined types
    * variable_names: List of column names
    * object_names: List of row names
    * active_variables: Index list of selected columns
    * active_objects: Index list of selected rows
    * n_rows: Number of rows in dataset
    * n_cols: Number of cols in dataset

    """
    matrix = Array(desc = 'Data matrix')
    """The number array"""
    
    # FIXME: Public
    _ds_id = Str('no_id', label = 'Dict key name')
    """A *technical* identity for this dataset.

    Should not be displayed to the user.

    """

    # FIXME: Public
    _ds_name = Str(
        'Unnamed dataset',
        desc = 'User friendly display name',
        label = 'Dataset name')

    _dataset_type = Enum(DS_TYPES,
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
        self.active_objects = range(self.matrix.shape[0])
        try:
            self.active_variables = range(self.matrix.shape[1])
        except IndexError:
            self.active_variables = range(len(self.matrix.dtype))


    def _get_n_rows(self):
        if self.matrix.shape[0] > 0:
            return self.matrix.shape[0]
        else:
            return 0

    def _get_n_cols(self):
        if self.matrix.shape[0] > 0:
            try:
                return self.matrix.shape[1]
            except IndexError:
                return len(self.matrix.dtype)
        else:
            return 0

    def subset(self):
        """Extract a subset of this dataset

        The subset is determined by the **active_[variables|objects]**.

        :returns: Object like this
        :rtype: DataSet

        """
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
