
# Scipy libs imports
import numpy as _np
import pandas as _pd

# ETS imports
import traits.api as _traits

# Local imports
from pca import nipalsPCA as PCA
from dataset import DataSet
from dataset_container import DatasetContainer
from plugin_base import Model, Result


class InComputeable(Exception):
    pass


class Pca(Model):
    """Represent the PCA model of a dataset."""
    ds = DataSet()
    # List of variable names with zero variance in the data vector
    zero_variance = _traits.List()

    #checkbox bool for standardised results
    standardise = _traits.Bool(False)
    calc_n_pc = _traits.Int()
    min_pc = 2
    max_pc = _traits.Property()
    min_std = _traits.Float(0.001)


    def _get_res(self):
        '''Does the PCA calculation and gets the results

        This return an results object that holds copies of the
        various result data. Each result set i an DataSet containing
        all metadata necessary for presenting the result.
        '''
        if self.standardise:
            std_ds = True
        else:
            std_ds = False
        if self.standardise and self._have_zero_std_var():
            raise InComputeable('Matrix have variables with zero variance',
                                self.zero_variance)
        pca = PCA(self.ds.values,
                  numPC=self.calc_n_pc, stand=std_ds, cvType=["loo"])

        return self._pack_res(pca)


    def _have_zero_std_var(self):
        sv = self.ds.values.std(axis=0)
        dm = sv < self.min_std
        if _np.any(dm):
            vv = _np.array(self.ds.var_n)
            self.zero_variance = list(vv[_np.nonzero(dm)])
            return True
        else:
            self.zero_variance = []
            return False


    def _get_max_pc(self):
        return max((min(self.ds.n_objs, self.ds.n_vars, 12) - 2), self.min_pc)


    def _calc_n_pc_default(self):
        return self.max_pc


    def _pack_res(self, pca_obj):
        res = Result('PCA {0}'.format(self.ds.display_name))

        # Scores
        mT = pca_obj.scores()
        res.scores = DataSet(
            mat=_pd.DataFrame(
                data=mT,
                index=self.ds.obj_n,
                columns=["PC-{0}".format(i+1) for i in range(mT.shape[1])],
                ),
            display_name='Scores')

        # Loadings
        mP = pca_obj.loadings()
        res.loadings = DataSet(
            mat=_pd.DataFrame(
                data=mP,
                index=self.ds.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mP.shape[1])],
                ),
            display_name='Loadings')

        # Correlation loadings
        mCL = pca_obj.corrLoadings()
        res.corr_loadings = DataSet(
            mat=_pd.DataFrame(
                data=mCL,
                index=self.ds.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mCL.shape[1])],
                ),
            display_name='Correlation loadings')

        # Explained variance
        cal = pca_obj.calExplVar()
        val = pca_obj.valExplVar()
        res.expl_var = DataSet(
            mat=_pd.DataFrame(
                data=[cal, val],
                index=['calibrated', 'validated'],
                columns=["PC-{0}".format(i+1) for i in range(len(cal))],
                ),
            display_name='Explained variance')

        # Residuals E after each computed PC
        # Return a dictionary with arrays
        # I can put this into a Pandas Panel 3D structure
        resids = pca_obj.residuals()

        # predicted matrices Xhat from calibration after each computed PC.
        cal_pred_x = pca_obj.calPredX()

        #validated matrices Xhat from calibration after each computed PC.
        val_pred_x = pca_obj.valPredX()

        # MSEE from cross validation after each computed PC.
        msee = pca_obj.MSEE()

        # MSEE from cross validation after each computed PC for each variable.
        ind_var_msee = pca_obj.MSEE_indVar()

        # MSECV from cross validation after each computed PC.
        msecv = pca_obj.MSECV()

        # MSECV from cross validation after each computed PC for each variable.
        ind_var_msecv = pca_obj.MSECV_indVar()

        return res
