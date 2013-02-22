
# Std lib imports
import warnings
import itertools as _itr

# Num lib imports
import numpy as _np
import pandas as _pd

# ETS imports
import traits.api as _traits


DS_TYPES = ['Design variable',
            'Sensory profiling',
            'Consumer liking',
            'Consumer characteristics']


def deprecation(message):
    # stacklevel=3, relates the warning to the place in the code
    # that tries to use the deprecated interface
    warnings.warn(message, DeprecationWarning, stacklevel=3)


class DataSet(_traits.HasTraits):
    '''Dataset for holding one matrix

    and associated metadata
    '''
    _matrix = _traits.Instance(_pd.DataFrame, ())

    _id = _traits.Int()
    id = _traits.Property()
    new_id = _itr.count(start=101).next

    display_name = _traits.Str('Unnamed dataset')

    ds_type = _traits.Enum(DS_TYPES)

    # FIXME: This dataset has missing data
    # do you want to do somthing about it?
    # * throw rows/cols with missing data
    # * do imputation
    missing_data = _traits.Property(_traits.Bool)

    # FIXME: For backward compability
    n_cols = _traits.Property()
    n_rows = _traits.Property()
    variable_names = _traits.Property()
    object_names = _traits.Property()
    values = _traits.Property()
    matrix = _traits.Property()


    def _get_matrix(self):
        deprecation("Use values instead")
        return self._matrix.values


    def _get_values(self):
        return self._matrix.values


    def _set_matrix(self, value):
        self._matrix = value


    def _get_n_cols(self):
        return self._matrix.shape[1]


    def _get_n_rows(self):
        return self._matrix.shape[0]


    def _get_variable_names(self):
        return list(self._matrix.columns)


    def _get_object_names(self):
        return list(self._matrix.index)


    def __id_default(self):
        return DataSet.new_id()


    def _get_id(self):
        return str(self._id)


    def _get_missing_data(self):
        return _np.any(_np.isnan(self._matrix.values))


    def __eq__(self, other):
        return self.id == other


    def __ne__(self, other):
        return self.id != other

