
# Scipy libs imports
import pandas as _pd

# ETS imports
import traits.api as _traits

# Local imports
from plsr import nipalsPLS2 as PLSR
from pcr import nipalsPCR as PCR
from dataset import DataSet
from plugin_base import Model, Result


class Prefmap(Model):
    """Represent the Prefmap model between one X and Y dataset."""

    # Consumer liking
    ds_C = DataSet()
    # Sensory profiling
    ds_S = DataSet()
    ds_X = _traits.Property()
    ds_Y = _traits.Property()

    #checkbox bool for standardised results
    standardise_x = _traits.Bool(False)
    standardise_y = _traits.Bool(False)
    int_ext_mapping = _traits.Enum('Internal', 'External')
    prefmap_method = _traits.Enum('PLSR', 'PCR')
    calc_n_pc = _traits.Int()
    min_pc = 2
    max_pc = _traits.Property()


    def _get_res(self):
        if self.prefmap_method == 'PLSR':
            pls = PLSR(self.ds_X.values, self.ds_Y.values,
                      numPC=self.calc_n_pc, cvType=["loo"],
                      Xstand=self.standardise_x, Ystand=self.standardise_y)
            return self._pack_res(pls)
        elif self.prefmap_method == 'PCR':
            pcr = PCR(self.ds_X.values, self.ds_Y.values,
                      numPC=self.calc_n_pc, cvType=["loo"],
                      Xstand=self.standardise_x, Ystand=self.standardise_y)
            return self._pack_res(pcr)


    def _get_ds_X(self):
        if self.int_ext_mapping == 'Internal':
            return self.ds_C
        else:
            return self.ds_S


    def _get_ds_Y(self):
        if self.int_ext_mapping == 'Internal':
            return self.ds_S
        else:
            return self.ds_C


    def _get_max_pc(self):
        if self.int_ext_mapping == 'Internal':
            return max((min(self.ds_C.n_objs, self.ds_C.n_vars, 12) - 2), self.min_pc)
        else:
            return max((min(self.ds_S.n_objs, self.ds_S.n_vars, 12) - 2), self.min_pc)


    def _calc_n_pc_default(self):
        return self.max_pc


    def _pack_res(self, pls_obj):
        res = Result('Prefmap')

        # Scores X
        mT = pls_obj.X_scores()
        res.scores_x = DataSet(
            mat=_pd.DataFrame(
                data=mT,
                index=self.ds_X.obj_n,
                columns=["PC-{0}".format(i+1) for i in range(mT.shape[1])],
                ),
            display_name=self.ds_X.display_name)

        # loadings_x
        mP = pls_obj.X_loadings()
        res.loadings_x = DataSet(
            mat=_pd.DataFrame(
                data=mP,
                index=self.ds_X.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mP.shape[1])],
                ),
            display_name=self.ds_X.display_name)

        # loadings_y
        # Same as loading_x in external mapping?
        mQ = pls_obj.Y_loadings()
        res.loadings_y = DataSet(
            mat=_pd.DataFrame(
                data=mQ,
                index=self.ds_Y.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mQ.shape[1])],
                ),
            display_name=self.ds_Y.display_name)

        # expl_var_x
        cal = pls_obj.X_calExplVar()
        val = pls_obj.X_valExplVar()
        res.expl_var_x = DataSet(
            mat=_pd.DataFrame(
                data=[cal, val],
                index=['cal', 'val'],
                columns=["PC-{0}".format(i+1) for i in range(len(cal))],
                ),
            display_name=self.ds_X.display_name)

        # expl_var_y
        cal = pls_obj.Y_calExplVar()
        val = pls_obj.Y_valExplVar()
        res.expl_var_y = DataSet(
            mat=_pd.DataFrame(
                data=[cal, val],
                index=['cal', 'val'],
                columns=["PC-{0}".format(i+1) for i in range(len(cal))],
                ),
            display_name=self.ds_Y.display_name)

        # X_corrLoadings()
        # corr_loadings_x
        mXcl = pls_obj.X_corrLoadings()
        res.corr_loadings_x = DataSet(
            mat=_pd.DataFrame(
                data=mXcl,
                index=self.ds_X.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mXcl.shape[1])],
                ),
            display_name=self.ds_X.display_name)

        # Y_corrLoadings()
        # corr_loadings_y
        mYcl = pls_obj.Y_corrLoadings()
        res.corr_loadings_y = DataSet(
            mat=_pd.DataFrame(
                data=mYcl,
                index=self.ds_Y.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mXcl.shape[1])],
                ),
            display_name=self.ds_Y.display_name)

        return res
