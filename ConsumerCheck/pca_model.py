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
from dataset import DataSet
from dataset_container import DatasetContainer
from plugin_base import Model, Result


class InComputeable(Exception):
    pass


class Pca(Model):
    """Represent the PCA model of a data set."""
    ds = DataSet()
    settings = _traits.WeakRef()
    # List of variable names with zero variance in the data vector
    zero_variance = _traits.List()

    #checkbox bool for standardised results
    standardise = _traits.Bool(False)
    calc_n_pc = _traits.Int()
    min_pc = 2
    # max_pc = _traits.Property()
    max_pc = 10
    min_std = _traits.Float(0.001)


    def _get_res(self):
        '''Does the PCA calculation and gets the results

        This return an results object that holds copies of the
        various result data. Each result set i an DataSet containing
        all metadata necessary for presenting the result.
        '''
        if self.settings.standardise:
            std_ds = True
        else:
            std_ds = False
        if std_ds and self._have_zero_std_var():
            raise InComputeable('Matrix have variables with zero variance',
                                self.zero_variance)
        pca = PCA(self.ds.values,
                  numPC=self.settings.calc_n_pc, Xstand=std_ds, cvType=["loo"])

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
        mT = pca_obj.X_scores()
        res.scores = DataSet(
            mat=_pd.DataFrame(
                data=mT,
                index=self.ds.obj_n,
                columns=["PC-{0}".format(i+1) for i in range(mT.shape[1])],
                ),
            display_name='Scores')

        # Loadings
        mP = pca_obj.X_loadings()
        res.loadings = DataSet(
            mat=_pd.DataFrame(
                data=mP,
                index=self.ds.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mP.shape[1])],
                ),
            display_name='Loadings')

        # Correlation loadings
        mCL = pca_obj.X_corrLoadings()
        res.corr_loadings = DataSet(
            mat=_pd.DataFrame(
                data=mCL,
                index=self.ds.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mCL.shape[1])],
                ),
            display_name='Correlation loadings')

        # Explained variance
        cal = pca_obj.X_calExplVar()
        cum_cal = pca_obj.X_cumCalExplVar()[1:]
        val = pca_obj.X_valExplVar()
        cum_val = pca_obj.X_cumValExplVar()[1:]
        res.expl_var = DataSet(
            mat=_pd.DataFrame(
                data=[cal, cum_cal, val, cum_val],
                index=['calibrated', 'cumulative calibrated', 'validated', 'cumulative validated'],
                columns=["PC-{0}".format(i+1) for i in range(len(cal))],
                ),
            display_name='Explained variance')

        # Residuals E after each computed PC
        # Return a dictionary with arrays
        # I can put this into a Pandas Panel 3D structure
        resids = pca_obj.X_residuals()

        # predicted matrices Xhat from calibration after each computed PC.
        # FIXME: Is this X_predCal()
        # cal_pred_x = pca_obj.calPredX()

        #validated matrices Xhat from calibration after each computed PC.
        # val_pred_x = pca_obj.valPredX()

        # MSEE from cross validation after each computed PC.
        msee = pca_obj.X_MSEE()

        # MSEE from cross validation after each computed PC for each variable.
        ind_var_msee = pca_obj.X_MSEE_indVar()

        # MSECV from cross validation after each computed PC.
        msecv = pca_obj.X_MSECV()

        # MSECV from cross validation after each computed PC for each variable.
        ind_var_msecv = pca_obj.X_MSECV_indVar()

        return res
