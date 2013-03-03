
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
    mat = _traits.Instance(_pd.DataFrame, ())

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
    # Deprecated; replaced by n_vars
    n_cols = _traits.Property()
    # Deprecated; replaced by n_objs
    n_rows = _traits.Property()
    n_vars = _traits.Property()
    n_objs = _traits.Property()
    # Deprecated; replaced by var_n
    variable_names = _traits.Property()
    var_n = _traits.Property()
    # Deprecated; replaced by obj_n
    object_names = _traits.Property()
    obj_n = _traits.Property()
    values = _traits.Property()
    # Deprecated by direct access to mat
    matrix = _traits.Property()


    def _get_matrix(self):
        deprecation("Use values instead")
        return self.mat.values


    def _get_values(self):
        if self.missing_data:
            return _np.ma.masked_invalid(self.mat.values)
        else:
            return self.mat.values


    def _set_matrix(self, value):
        deprecation("Use mat instead")
        self.mat = value


    def _get_n_cols(self):
        deprecation("Use n_vars instead")
        return self.mat.shape[1]


    def _get_n_vars(self):
        return self.mat.shape[1]


    def _get_n_rows(self):
        deprecation("Use n_objs instead")
        return self.mat.shape[0]


    def _get_n_objs(self):
        return self.mat.shape[0]


    def _get_variable_names(self):
        deprecation("Use var_n instead")
        return list(self.mat.columns)


    def _get_var_n(self):
        return list(self.mat.columns)


    def _get_object_names(self):
        deprecation("Use obj_n instead")
        return list(self.mat.index)


    def _get_obj_n(self):
        return list(self.mat.index)


    def __id_default(self):
        return DataSet.new_id()


    def _get_id(self):
        return str(self._id)


    def _get_missing_data(self):
        return _np.any(_np.isnan(self.mat.values))


    def __eq__(self, other):
        return self.id == other


    def __ne__(self, other):
        return self.id != other

