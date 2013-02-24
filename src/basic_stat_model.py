

# Scipy imports
import numpy as np
import pandas as pd


# ETS imports
import traits.api as traits

# Local imports
from dataset_ng import DataSet


class BasicStatPlugin(traits.HasTraits):
    pass



class BasicStat(traits.HasTraits):
    ds = DataSet()

    stat_res = traits.Property()


    def _get_stat_res(self):
        class Res(object):
            def __init__(self, summary, hist):
                # mean, std, min, max, loci, hici
                self.summary = summary
                self.hist = hist


        sds = self._calc_summary()
        sdh = self._calc_histogram()

        res = Res(sds, sdh)

        return res


    def _calc_summary(self):
        mat = self.ds._matrix.values
        sy = pd.DataFrame(index=self.ds._matrix.index)
        sy['mean'] = mat.mean(axis=1)
        sy['std'] = mat.std(axis=1)
        sy['max'] = mat.max(axis=1)
        sy['min'] = mat.min(axis=1)

        return DataSet(matrix=sy, display_name="Summary")


    def _calc_histogram(self):
        mat = self.ds._matrix.values
        end = mat.max()
        hl = []
        for l in mat:
            hl.append(list(np.bincount(l, minlength=end+2)))

        ht = pd.DataFrame(hl, index=self.ds._matrix.index)
        return DataSet(matrix=ht, display_name="Histogram")



def extract_summary(basic_stat_res):
    return basic_stat_res.summary


def extract_histogram(basic_stat_res):
    return basic_stat_res.hist
