
# Num lib imports
import numpy as _np
import pandas as _pd
import itertools as _itr

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
    matrix = _traits.Instance(_pd.DataFrame)

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


    def __id_default(self):
        return DataSet.new_id()


    def _get_id(self):
        return str(self._id)


    def _get_missing_data(self):
        return _np.any(_np.isnan(self.matrix.values))
    


if __name__ == '__main__':
    print("Test run")
    td = _pd.DataFrame([[1, 2, _np.nan], [4, 5, 6]])
    ds = DataSet(matrix=td)
