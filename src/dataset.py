
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

    n_vars = _traits.Property()
    n_objs = _traits.Property()
    var_n = _traits.Property()
    obj_n = _traits.Property()
    values = _traits.Property()


    def _get_values(self):
        if self.missing_data:
            return _np.ma.masked_invalid(self.mat.values)
        else:
            return self.mat.values


    def _get_n_vars(self):
        return self.mat.shape[1]


    def _get_n_objs(self):
        return self.mat.shape[0]


    def _get_var_n(self):
        return list(self.mat.columns)


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

