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
from plugin_tree_helper import Model


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
        class Res(object):
            '''Calculation result *struct*.

            Attributes:
             * summary
             * hist
            '''
            def __init__(self, summary, hist):
                # mean, std, min, max, loci, hici
                self.summary = summary
                self.hist = hist

        sds = self._calc_summary()
        sdh = self._calc_histogram()

        res = Res(sds, sdh)

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
        sy['mean'] = mat.mean(axis=ax)
        sy['std'] = mat.std(axis=ax)
        sy['min'] = mat.min(axis=ax)
        sy['max'] = mat.max(axis=ax)

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


def extract_summary(basic_stat_res):
    '''Returns the summary statistics from the result object'''
    return basic_stat_res.summary


def extract_histogram(basic_stat_res):
    '''Returns the histogram data from the result object'''
    return basic_stat_res.hist
