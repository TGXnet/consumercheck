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

'''Dataset represent a matrix

Design notes:
When a group is related to a dataset (matrix) the group is either for row (index) or columns
selection. The selection list should be index based and not label based. A group or a
grouping (collection of groups) can be taken from on dataset and be applied to another dataset.

TODO: API:
 + get at dataset to return at subset by providing group name
 + create a dummyfi dataset from a factor
 + Create a factor from a row or column in the dataset
 + various methods to check alignment with a different dataset


From numpy doc:

row-major
A way to represent items in a N-dimensional array in the 1-dimensional computer memory.
In row-major order, the rightmost index 'varies the fastest'. Row-major order is also
known as the C order, as the C programming language uses it. New NumPy arrays are by
default in row-major order.

axis
A 2-dimensional array has two corresponding axes: the first running
vertically downwards across rows (axis 0), and the second running
horizontally across columns (axis 1).
'''

# Std lib imports
import warnings
import itertools as _itr

# Num lib imports
import numpy as _np
import pandas as _pd

# ETS imports
import traits.api as _traits
from enable.api import ColorTrait

# Local import
from utilities import rnd_color


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

    display_name = _traits.Unicode('Unnamed data set')

    kind = _traits.Enum(DS_TYPES)

    # FIXME: Only color
    style = _traits.Instance('VisualStyle', ())

    # Example: {'species': [SubSet, SubSet], 'location': [SubSet, SubSet]}
    subs = _traits.Dict(_traits.Unicode, _traits.List)

    row_factors = _traits.List()
    col_factors = _traits.List()

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
    # FIXME: Is this needed, can i use ColorTrait directly?
    fg_color = ColorTrait('black')
    # bg_color = ColorTrait('white')


class Level(_traits.HasTraits):
    '''Represent a level in a factor

    If we have gender as a factor, the levels can be for instance male or female.
    If we have a age group factor, the levels can bel for instance 1, 2, 3.
    '''
    # Require name
    name = _traits.Unicode()
    # Accept list of integers or numpy vector (1 dim array) that we convert to list
    selector = _traits.List(_traits.Int)
    # Autoasign unique style if style is not explicit specified
    # style = VisualStyle()
    color = ColorTrait()

    def __init__(self, idx, name, color=None):
        '''Create level group

        idx: list of numerical indexes to make selection from matrix
        name: name for this group
        style: color tuple (r, g, b, a) to color this level in plots
        '''
        self.selector = list(idx)
        self.name = name
        if color is None:
            self.color = rnd_color()
        else:
            self.color = color


    def get_values(self, dataset, axis=0):
        '''Get selected row or columns values

        dataset: the dataset to get from
        axis: 0 - vertical, columns labels, 1 - horizontal, row labels

        '''
        if axis == 0:
            return dataset.mat[self.selector,:]
        elif axis == 1:
            return dataset.mat[:,self.selector]
        raise ValueError('Illegale value for axis')


    def get_labels(self, dataset, axis=0):
        '''Get selected row or columns labels

        dataset: the dataset to get from
        axis: 0 - vertical, columns labels, 1 - horizontal, row labels

        '''
        if axis == 0:
            return dataset.mat.index[self.selector]
        elif axis == 1:
            return dataset.mat.columns[:,self.selector]
        raise ValueError('Illegale value for axis')


    def __eq__(self, other):
        return self.name == other.name


    def __ne__(self, other):
        return self.name != other.name


    # def __hash__(self):
    #     pass


class Factor(_traits.HasTraits):
    '''Represent different factors as independent variables

    FIXME: is the order of levels important, the uniqueness?
    looks more like a mapping type than a sequences type
    '''
    name = _traits.Unicode()
    levels = _traits.Dict(_traits.Unicode, Level)
    # Can be used to check if this can be used for a given dataset
    size = _traits.Property()
    _size = _traits.Int()
    default_ds_axis = _traits.Enum(("row", "col"))


    def __init__(self, name, size, *levels, **kwargs):
        '''Create a factor object

        name: The factor name
        levels: none, one or several level objects
        check_idx: check index strategy; no, toss_overlaping
        '''
        check_idx = kwargs.pop('check_idx', "no")
        super(Factor, self).__init__(name=name, size=size, **kwargs)
        for level in levels:
            self.add_level(level, check_idx)


    def add_level(self, level, check_idx="no"):
        '''Add level

        level: a level object
        check_idx: "no", "toss_overlaping", "excpet_overlapping", "return_overlapping"
        '''
        self.name_check(level.name)
        self.bound_check(level.selector)
        if check_idx == "no":
            self.levels[level.name] = level
        elif check_idx == "toss_overlaping":
            self.toss_overlaping(level)
            self.levels[level.name] = level
        else:
            msg = "Not valid value for check_idx: {0}".format(check_idx)
            raise ValueError(msg)


    def name_check(self, new_name):
        if new_name in self.levels:
            msg = "Level name collision. Name: {0} already exist in factor: {1}".format(
                new_name, self.name)
            raise ValueError(msg)


    def bound_check(self, selector):
        if self.size <= max(selector):
            msg = "Index in level out of bounds"
            raise IndexError(msg)


    def toss_overlaping(self, level):
        '''
        FIXME: This will mainpulate an existing object. Is that unproblematic?
        '''
        existing_idx = []
        for lv in self.levels.itervalues():
            existing_idx.extend(lv.selector)
        exist = set(existing_idx)
        unique  = set(level.selector).difference(exist)
        level.selector = list(unique)


    def get_values(self, dataset, name, axis=None):
        '''Return numpy subarray
        '''
        idx = self.levels[name].selector
        if axis is not None:
            if axis == 0:
                return dataset.mat.values[idx,:]
            elif axis == 1:
                return dataset.mat.values[:,idx]
            raise ValueError('Illegale value for axis')
        else:
            if self.default_ds_axis == "row":
                return dataset.mat.values[idx,:]
            else:
                return dataset.mat.values[:,idx]


    def get_labels(self, dataset, name, axis=None):
        '''Return list of selected labels
        '''
        idx = self.levels[name].selector
        if axis is not None:
            if axis == 0:
                return dataset.mat.index[idx]
            elif axis == 1:
                return dataset.mat.columns[idx]
            raise ValueError('Illegale value for axis')
        else:
            if self.default_ds_axis == "row":
                return dataset.mat.index[idx]
            else:
                return dataset.mat.columns[idx]


    def _get_nonleveled(self, dataset, axis):
        '''Return all indexed for ann array that is not in a level
        '''
        lvs = set(_itr.chain.from_iterable([lv.selector for lv in self.levels.itervalues()]))
        return list(set(range(dataset.mat.shape[axis])).difference(lvs))


    def get_rest_values(self, dataset, axis=None):
        '''Return numpy subarray
        '''
        if axis is not None:
            if axis == 0:
                idx = self._get_nonleveled(dataset, 0)
                return dataset.mat.values[idx,:]
            elif axis == 1:
                idx = self._get_nonleveled(dataset, 1)
                return dataset.mat.values[:,idx]
            raise ValueError('Illegale value for axis')
        else:
            if self.default_ds_axis == "row":
                idx = self._get_nonleveled(dataset, 0)
                return dataset.mat.values[idx,:]
            else:
                idx = self._get_nonleveled(dataset, 1)
                return dataset.mat.values[:,idx]


    def get_rest_labels(self, dataset, axis=None):
        '''Return list of selected labels
        '''
        if axis is not None:
            if axis == 0:
                idx = self._get_nonleveled(dataset, 0)
                return dataset.mat.index[idx]
            elif axis == 1:
                idx = self._get_nonleveled(dataset, 1)
                return dataset.mat.columns[idx]
            raise ValueError('Illegale value for axis')
        else:
            if self.default_ds_axis == "row":
                idx = self._get_nonleveled(dataset, 0)
                return dataset.mat.index[idx]
            else:
                idx = self._get_nonleveled(dataset, 1)
                return dataset.mat.columns[idx]


    def __len__(self):
        return len(self.levels)


    # def __getitem__(self, key):
    #     pass


    # def __setitem__(self, key, value):
    #     pass


    # def __iter__(self):
    #     pass


    def _set_size(self, sz):
        self._size = sz


    def _get_size(self):
        return self._size



class SubSet(_traits.HasTraits):
    '''FIXME: deprecated by Level'''
    id = _traits.Str()
    name = _traits.Unicode()
    row_selector = _traits.List()
#     col_selector = _traits.List(_traits.Int())
    gr_style = VisualStyle()
