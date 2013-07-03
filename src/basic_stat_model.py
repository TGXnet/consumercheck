'''Module for basic statistics analysis

This module gives:
 * Data for box plots
 * Histogram data
'''
# Scipy imports
import numpy as _np
import pandas as _pd

# ETS imports
import traits.api as _traits

# Local imports
from dataset import DataSet
from plugin_base import Model, Result


class BasicStat(Model):
    '''Basic statitstics model object.

    This model calculates:
     * mean
     * std
     * min
     * max
    In adition i makes data for plotting histograms.

    The *summary_axis* attribute decides if the calculation is done for the
    row or column axis.
    '''
    ds = DataSet()
    summary_axis = _traits.Enum(('Row-wise', 'Column-wise'))


    def _get_res(self):
        res = Result('Basic stat')
        res.summary = self._calc_summary()
        res.hist = self._calc_histogram()

        return res


    def _calc_summary(self):
        mat = self.ds.values
        if self.summary_axis == 'Row-wise':
            ax = 1
            idx = self.ds.obj_n
        else:
            ax = 0
            idx = self.ds.var_n
        sy = _pd.DataFrame(index=idx)
        sy['min'] = _np.percentile(mat, 0, axis=ax)
        sy['perc25'] = _np.percentile(mat, 25, axis=ax)
        sy['med'] = _np.percentile(mat, 50, axis=ax)
        sy['perc75'] = _np.percentile(mat, 75, axis=ax)
        sy['max'] = _np.percentile(mat, 100, axis=ax)

        return DataSet(mat=sy, display_name="Summary")


    def _calc_histogram(self):
        # NOTE: astype(np.int16) due to some bincount() bug in v1.6.2 on window
        # https://github.com/numpy/numpy/issues/823
        mat = self.ds.values.astype(_np.int16)
        end = mat.max() + 2

        if self.ds.missing_data:
            hl = []
            if self.summary_axis == 'Row-wise':
                idx = self.ds.obj_n
                dr = 1
                for i in range(mat.shape[0]):
                    row = mat[i, ~mat[i].mask]
                    hr = list(_np.bincount(row, minlength=end))
                    hl.append(hr)
            else:
                idx = self.ds.var_n
                dr = 0
                for i in range(mat.shape[1]):
                    row = mat[~mat[:, i].mask, i]
                    hr = list(_np.bincount(row, minlength=end))
                    hl.append(hr)
        else:
            if self.summary_axis == 'Row-wise':
                idx = self.ds.obj_n
                it = [(i, Ellipsis) for i in range(mat.shape[0])]
            else:
                idx = self.ds.var_n
                it = [(Ellipsis, i) for i in range(mat.shape[1])]

            hl = [list(_np.bincount(mat[i], minlength=end)) for i in it]

        ht = _pd.DataFrame(hl, index=idx)
        if self.ds.missing_data:
            ht['missing'] = _np.ma.count_masked(mat, axis=dr)

        return DataSet(mat=ht, display_name="Histogram")
