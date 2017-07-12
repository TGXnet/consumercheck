'''ConsumerCheck
'''
#-----------------------------------------------------------------------------
#  Copyright (C) 2014 Thomas Graff <thomas.graff@tgxnet.no>
#
#  This file is part of ConsumerCheck.
#
#  ConsumerCheck is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  ConsumerCheck is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ConsumerCheck.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------

# Std lib imports
import warnings
import itertools as _itr

# Num lib imports
import numpy as _np
import pandas as _pd

# ETS imports
import traits.api as _traits
from enable.api import ColorTrait


DS_TYPES = ['Product design',
            'Descriptive analysis / sensory profiling',
            'Consumer liking',
            'Consumer characteristics',
            'Other']


class DataSet(_traits.HasTraits):
    '''Data set for holding one matrix

    and associated metadata
    The reccomended access methods as properties for the DataSet object:
     * id: An identity string that is unique for each object
     * display_name: An human friendly name that for the datataset
     * kind: The data set type
     * missing_data: Boolean value indicatin if the data set have "holes"
     * n_vars: Number of variables
     * n_objs: Number of objects
     * var_n: List containing variable names
     * obj_n: List containing object names
     * values: The matrix values as an 2D Numpy array
     * mat: The matrix as an Pandas DataFrame
    '''
    mat = _traits.Instance(_pd.DataFrame, ())

    _id = _traits.Int()
    id = _traits.Property()
    new_id = _itr.count(start=101).next

    display_name = _traits.Str('Unnamed data set')

    kind = _traits.Enum(DS_TYPES)

    style = _traits.Instance('VisualStyle', ())

    # Example: {'species': [SubSet, SubSet], 'location': [SubSet, SubSet]}
    subs = _traits.Dict(unicode, list)

    # FIXME: This data set has missing data
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


    def __eq__(self, other):
        return self.id == other


    def __ne__(self, other):
        return self.id != other


    def _get_id(self):
        return str(self._id)


    def _get_missing_data(self):
        # FIXME: I must look more into this
        try:
            return _np.any(_np.isnan(self.mat.values))
        except TypeError:
            return False


    def get_subset_groups(self):
        return self.subs.keys()


    def get_subsets(self, group):
        return self.subs[group]


    def get_subset_rows(self, subset):
        ''' Return a subset from given subset id'''
        return self.mat.loc[list(subset.row_selector)]


    def copy(self, transpose=False):
        new = self.clone_traits(traits=['display_name', 'kind', 'style', 'subs'])
        if transpose:
            tmp = self.mat.copy()
            new.mat = tmp.transpose()
        else:
            new.mat = self.mat.copy()
        return new


class VisualStyle(_traits.HasTraits):
    fg_color = ColorTrait('black')
    bg_color = ColorTrait('white')


class SubSet(_traits.HasTraits):
    id = _traits.Str()
    name = _traits.Str()
    row_selector = _traits.List()
#     col_selector = _traits.List(_traits.Int())
    gr_style = VisualStyle()
