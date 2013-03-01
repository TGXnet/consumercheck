
# Scipy imports
import numpy as _np
import pandas as _pd

# ETS imports
import traits.api as _traits

# Local imports
from dataset_ng import DataSet
from dataset_container import DatasetContainer


class BasicStat(_traits.HasTraits):
    id = _traits.Str()
    ds = DataSet()
    summary_axis = _traits.Enum(('Row-wise', 'Column-wise'))
    stat_res = _traits.Property()


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

        if self.summary_axis == 'Row-wise':
            idx = self.ds.obj_n
            it = [(i,Ellipsis) for i in range(mat.shape[0])]
        else:
            idx = self.ds.var_n
            it = [(Ellipsis,i) for i in range(mat.shape[1])]

        hl = [list(_np.bincount(mat[i], minlength=end)) for i in it]

        ht = _pd.DataFrame(hl, index=idx)
        return DataSet(mat=ht, display_name="Histogram")


    def __eq__(self, other):
        return self.id == other


    def __ne__(self, other):
        return self.id != other



def extract_summary(basic_stat_res):
    return basic_stat_res.summary


def extract_histogram(basic_stat_res):
    return basic_stat_res.hist



class BasicStatPlugin(_traits.HasTraits):
    dsc = _traits.Instance(DatasetContainer)
    tasks = _traits.List(_traits.HasTraits)


    def add(self, task):
        self.tasks.append(task)


    def make_model(self, ds_id):
        ds = self.dsc[ds_id]
        bs = BasicStat(id=ds_id, ds=ds)
        return bs


    def remove(self, task_id):
        del(self.tasks[self.tasks.index(task_id)])
