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

# Scipy libs imports
import numpy as _np
import pandas as _pd

# ETS imports
import traits.api as _traits

# Local imports
from pca import nipalsPCA as PCA
from plsr import nipalsPLS2 as PLSR
from dataset import DataSet
from plugin_base import Model, Result


class InComputeable(Exception):
    pass


class IndDiff(Model):
    """Represent the IndDiff model between one X and Y data set."""

    # Consumer Liking
    ds_L = DataSet()
    # Consumer Attributes
    ds_A = DataSet()
    # response and independent variables
    # predicted variables and the observable variables
    # Partial least squares Discriminant Analysis (PLS-DA) is a variant used when the Y is categorical.
    # A PLS model will try to find the multidimensional direction in the X space that explains the
    # maximum multidimensional variance direction in the Y space.
    # X is an n x m matrix of predictors
    # Y is an n x p matrix of responses
    # Some PLS algorithms are only appropriate for the case where Y is a column vector (PLS1)
    # general case of a matrix Y (PLS2)
    ds_X = _traits.Property()
    ds_Y = _traits.Property()
    pcax = _traits.Property()
    settings = _traits.WeakRef()
    # checkbox bool for standardised results
    calc_n_pc = _traits.Int()
    min_pc = 2
    # max_pc = _traits.Property()
    max_pc = 10
    min_std = _traits.Float(0.001)
    C_zero_std = _traits.List()
    S_zero_std = _traits.List()


    def _get_pcax(self):
        pca = PCA(self.ds_X.values, numPC=5, Xstand=True, cvType=["loo"])

        return self._pack_pca_res(pca)


    def _pack_pca_res(self, pca_obj):
        res = Result('PCA {0}'.format(self.ds_X.display_name))

        # Scores
        mT = pca_obj.X_scores()
        res.scores = DataSet(
            mat=_pd.DataFrame(
                data=mT,
                index=self.ds_X.obj_n,
                columns=["PC-{0}".format(i+1) for i in range(mT.shape[1])],
            ),
            subs=self.ds_X.subs,
            display_name='Scores')

        # Loadings
        mP = pca_obj.X_loadings()
        res.loadings = DataSet(
            mat=_pd.DataFrame(
                data=mP,
                index=self.ds_X.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mP.shape[1])],
            ),
            display_name='Loadings')

        return res



    def _get_res(self):
        if self._have_zero_std():
            raise InComputeable('Matrix have variables with zero variance',
                                self.C_zero_std, self.S_zero_std)
        # n_pc = min(self.settings.calc_n_pc, self._get_max_pc())
        n_pc = 5
        pls = PLSR(self.ds_X.values, self.ds_Y.values,
                   numPC=n_pc, cvType=["loo"],
                   Xstand=True, Ystand=True)
        return self._pack_res(pls)


    def _have_zero_std(self):
        self.C_zero_std = []
        self.S_zero_std = []
        rC = self._C_have_zero_std_var()
        rS = self._S_have_zero_std_var()
        return rC or rS


    def _C_have_zero_std_var(self):
        self.C_zero_std = self._check_zero_std(self.ds_L)
        return bool(self.C_zero_std)


    def _S_have_zero_std_var(self):
        self.S_zero_std = self._check_zero_std(self.ds_A)
        return bool(self.S_zero_std)


    def _check_zero_std(self, ds):
        zero_std_var = []
        sv = ds.values.std(axis=0)
        dm = sv < self.min_std
        if _np.any(dm):
            vv = _np.array(ds.var_n)
            zero_std_var = list(vv[_np.nonzero(dm)])
        return zero_std_var


    def _get_ds_X(self):
        return self.ds_L


    def _get_ds_Y(self):
        return self.ds_A


    def _get_max_pc(self):
        return max((min(self.ds_L.n_objs, self.ds_L.n_vars, 11) - 1), self.min_pc)


    def _calc_n_pc_default(self):
        return self.max_pc


    def _mk_pred_ds(self, pred_mat, npc):
        pred_ds = DataSet(
            mat=_pd.DataFrame(
                data=pred_mat,
                index=self.ds_Y.obj_n,
                columns=self.ds_Y.var_n,
            ),
            display_name='Predicted after PC{}'.format(npc))
        return pred_ds


    def _pack_res(self, pls_obj):
        res = Result('IndDiff {0}(X) & {1}(Y)'.format(self.ds_X.display_name, self.ds_Y.display_name))
        res.external_mapping = False

        # Scores X
        mT = pls_obj.X_scores()
        res.scores_x = DataSet(
            mat=_pd.DataFrame(
                data=mT,
                index=self.ds_X.obj_n,
                columns=["PC-{0}".format(i+1) for i in range(mT.shape[1])],
            ),
            display_name='X scores')

        # loadings_x
        mP = pls_obj.X_loadings()
        res.loadings_x = DataSet(
            mat=_pd.DataFrame(
                data=mP,
                index=self.ds_X.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mP.shape[1])],
            ),
            display_name='X loadings')

        # loadings_y
        # Same as loading_x in external mapping?
        mQ = pls_obj.Y_loadings()
        res.loadings_y = DataSet(
            mat=_pd.DataFrame(
                data=mQ,
                index=self.ds_Y.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mQ.shape[1])],
            ),
            display_name='Y loadings')

        # expl_var_x
        cal = pls_obj.X_calExplVar()
        cum_cal = pls_obj.X_cumCalExplVar()[1:]
        val = pls_obj.X_valExplVar()
        cum_val = pls_obj.X_cumValExplVar()[1:]
        res.expl_var_x = DataSet(
            mat=_pd.DataFrame(
                data=[cal, cum_cal, val, cum_val],
                index=['calibrated', 'cumulative calibrated', 'validated', 'cumulative validated'],
                columns=["PC-{0}".format(i+1) for i in range(len(cal))],
            ),
            display_name='Explained variance in X')

        # expl_var_y
        cal = pls_obj.Y_calExplVar()
        cum_cal = pls_obj.Y_cumCalExplVar()[1:]
        val = pls_obj.Y_valExplVar()
        cum_val = pls_obj.Y_cumValExplVar()[1:]
        res.expl_var_y = DataSet(
            mat=_pd.DataFrame(
                data=[cal, cum_cal, val, cum_val],
                index=['calibrated', 'cumulative calibrated', 'validated', 'cumulative validated'],
                columns=["PC-{0}".format(i+1) for i in range(len(cal))],
            ),
            display_name='Explained variance in Y')

        # X_corrLoadings()
        # corr_loadings_x
        mXcl = pls_obj.X_corrLoadings()
        res.corr_loadings_x = DataSet(
            mat=_pd.DataFrame(
                data=mXcl,
                index=self.ds_X.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mXcl.shape[1])],
            ),
            display_name='X & Y correlation loadings')

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

        # Y_predCal()
        # Return a dict with Y pred for each PC
        pYc = pls_obj.Y_predCal()
        ks = pYc.keys()
        pYcs = [self._mk_pred_ds(pYc[k], k) for k in ks]
        res.pred_cal_y = pYcs

        # Y_predVal()
        # Return a dict with Y pred for each PC
        pYv = pls_obj.Y_predVal()
        ks = pYv.keys()
        pYvs = [self._mk_pred_ds(pYv[k], k) for k in ks]
        res.pred_val_y = pYvs

        return res
