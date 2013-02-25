
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
    stat_res = _traits.Property()

    test_dummy = _traits.Bool()


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
        sy = _pd.DataFrame(index=self.ds.obj_n)
        sy['mean'] = mat.mean(axis=1)
        sy['std'] = mat.std(axis=1)
        sy['max'] = mat.max(axis=1)
        sy['min'] = mat.min(axis=1)

        return DataSet(mat=sy, display_name="Summary")


    def _calc_histogram(self):
        mat = self.ds.values
        end = mat.max()
        hl = []
        for l in mat:
            hl.append(list(_np.bincount(l, minlength=end+2)))

        ht = _pd.DataFrame(hl, index=self.ds.obj_n)
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
