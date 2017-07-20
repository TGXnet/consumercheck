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
import sklearn.cross_decomposition

# ETS imports
import traits.api as _traits

# Local imports
import pca
import plsr
import dummify as df
import dataset as ds
import plugin_base as pb
import result_adapter as ra


class InComputeable(Exception):
    pass


class IndDiff(pb.Model):
    """Represent the IndDiff model between X and Y data set.

    A PLS model will try to find the multidimensional direction in the X space that
    explains the maximum multidimensional variance direction in the Y space.

    Consumer attributes is the independent predictors - observable variables X

    Liking datata is the respons - predicted variables Y, this can be dummified

    X is an n x m matrix of predictors
    Y is an n x p matrix of responses
    """

    # Consumer Liking
    ds_L = ds.DataSet()
    # Consumer Attributes
    ds_A = ds.DataSet()

    # predictors
    ds_X = _traits.Property()
    # responses
    ds_Y = _traits.Property()

    # Calculated PCA for the response variable
    pca_Y = _traits.Property()

    settings = _traits.WeakRef()
    # checkbox bool for standardised results
    calc_n_pc = _traits.Int()
    min_pc = 2
    # max_pc = _traits.Property()
    max_pc = 10

    # Selection of variables to dummify
    dummify_variables = _traits.ListUnicode()
    consumer_variables = _traits.ListUnicode()

    # Liking PC to use in PLS
    # liking_pc = _traits.List(_traits.Int)
    selected_liking_pc = _traits.List(_traits.Int)
    n_Y_pc = _traits.List([(0,'PC-1'),(1,'PC-2'),(2,'PC-3')])
    selected_segments = _traits.List()

    min_std = _traits.Float(0.001)
    C_zero_std = _traits.List()
    S_zero_std = _traits.List()


    def _get_pca_Y(self):
        cpca = pca.nipalsPCA(self.ds_Y.values, numPC=3, Xstand=False, cvType=["loo"])
        return ra.adapt_oto_pca(cpca, self.ds_Y, self.ds_Y.display_name)


    def calc_pls_raw_liking(self):
        n_pc = 2
        dsx = self.ds_X
        dsy = self.ds_Y
        pls = sklearn.cross_decomposition.PLSRegression(n_components=n_pc)
        pls.fit(dsx.values, dsy.values)
        return ra.adapt_sklearn_pls(pls, dsx, dsy, 'Tore<rename>')


    def calc_pls_pc_likings(self, pc_sel):
        n_pc = 2
        dsx = self.ds_X
        dsy = self.pca_Y.scores.mat.iloc[:,pc_sel]
        pls = sklearn.cross_decomposition.PLSRegression(n_components=n_pc)
        pls.fit(dsx.values, dsy.values)
        return ra.adapt_sklearn_pls(pls, dsx, dsy, 'Per<rename>')


    def calc_plsr_segments(self, selection):
        if self._have_zero_std():
            raise InComputeable('Matrix have variables with zero variance',
                                self.C_zero_std, self.S_zero_std)
        n_pc = 2
        sel = [str(e) for e in selection]
        pls = sklearn.cross_decomposition.PLSRegression(n_components=n_pc)
        dsx = self.ds_X
        dsx.mat = dsx.mat.loc[sel,:]
        dsy = self.pca_Y.loadings.mat
        dsy = dsy.loc[sel,:]
        pls.fit(dsx.values, dsy.values)
        return ra.adapt_sklearn_pls(pls, dsx, dsy, 'Tore')



    def calc_plsr_da(self, segments):
        '''Process
        Add a row for each segments
        Loop throu each segment row and set 1 where we have index and 0 for the rest
        do this via property - no then segments have to be part of model
        Hmmm
        Add dummy segments to attr array as vel
        '''
        every = []
        for seg in segments:
            every.extend(seg.member_index)

        dsx = self.ds_X
        dsx.mat = dsx.mat.loc[every,:]

        dsy = self.make_liking_dummy_segmented(segments)
        dsy = dsy.copy(transpose=True)

        n_pc = 2
        pls = sklearn.cross_decomposition.PLSRegression(n_components=n_pc)
        pls.fit(dsx.values, dsy.values)
        return ra.adapt_sklearn_pls(pls, dsx, dsy, 'PLS-DA')


    def make_liking_dummy_segmented(self, segments):
        dsy_sd = self.ds_Y

        if len(segments) < 1:
            # FIXME: Show warning, no segments defined
            return dsy_sd

        every = []
        for seg in segments:
            every.extend(seg.member_index)

        dsy_sd.mat = dsy_sd.mat.loc[:,every]

        segs = _pd.DataFrame(0, index=[seg.name for seg in segments], columns=every)
        for seg in segments:
            segs.loc[seg.name,seg.member_index] = 1

        # dsy_sd.mat = dsy_sd.mat.append(segs)
        dsy_sd.mat = segs

        return dsy_sd





    def _get_res(self):
        if self._have_zero_std():
            raise InComputeable('Matrix have variables with zero variance',
                                self.C_zero_std, self.S_zero_std)
        # n_pc = min(self.settings.calc_n_pc, self._get_max_pc())
        n_pc = 3
        # pls = plsr.nipalsPLS2(
        #     self.ds_X.values, self.ds_Y.values,
        #     numPC=n_pc, cvType=["loo"],
        #     Xstand=True, Ystand=True)
        # Must do manual centring and standardisation
        pls = sklearn.cross_decomposition.PLSRegression(n_components=n_pc)
        dsx = self.ds_X.copy(transpose=True)
        dsy = self.pca_Y.loadings.mat['PC-1']
        pls.fit(dsx.values, dsy.values)
        # return self._pack_res(pls)
        return ra.adapt_sklearn_pls(pls, dsx, dsy, 'Tore')


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
        """Get the independent variable X that is the consumer attributes"""
        varn = [str(v) for v in self.settings.dummify_variables]
        dsa = self.ds_A.copy(transpose=False)
        dsx = df.dummify(dsa, varn)
        return dsx


    def _get_ds_Y(self):
        """Get the response variable that is the consumer liking"""
        return self.ds_L.copy(transpose=True)


    def _get_max_pc(self):
        return max((min(self.ds_L.n_objs, self.ds_L.n_vars, 11) - 1), self.min_pc)


    def _calc_n_pc_default(self):
        return self.max_pc


    def _mk_pred_ds(self, pred_mat, npc):
        pred_ds = ds.DataSet(
            mat=_pd.DataFrame(
                data=pred_mat,
                index=self.ds_Y.obj_n,
                columns=self.ds_Y.var_n,
            ),
            display_name='Predicted after PC{}'.format(npc))
        return pred_ds


    def _pack_res(self, pls_obj):
        res = pb.Result('IndDiff {0}(X) & {1}(Y)'.format(
            self.ds_X.display_name, self.ds_Y.display_name))
        res.external_mapping = False

        # Scores X
        mT = pls_obj.X_scores()
        res.scores_x = ds.DataSet(
            mat=_pd.DataFrame(
                data=mT,
                index=self.ds_X.obj_n,
                columns=["PC-{0}".format(i+1) for i in range(mT.shape[1])],
            ),
            display_name='X scores')

        # loadings_x
        mP = pls_obj.X_loadings()
        res.loadings_x = ds.DataSet(
            mat=_pd.DataFrame(
                data=mP,
                index=self.ds_X.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mP.shape[1])],
            ),
            display_name='X loadings')

        # loadings_y
        # Same as loading_x in external mapping?
        mQ = pls_obj.Y_loadings()
        res.loadings_y = ds.DataSet(
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
        res.expl_var_x = ds.DataSet(
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
        res.expl_var_y = ds.DataSet(
            mat=_pd.DataFrame(
                data=[cal, cum_cal, val, cum_val],
                index=['calibrated', 'cumulative calibrated', 'validated', 'cumulative validated'],
                columns=["PC-{0}".format(i+1) for i in range(len(cal))],
            ),
            display_name='Explained variance in Y')

        # X_corrLoadings()
        # corr_loadings_x
        mXcl = pls_obj.X_corrLoadings()
        res.corr_loadings_x = ds.DataSet(
            mat=_pd.DataFrame(
                data=mXcl,
                index=self.ds_X.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mXcl.shape[1])],
            ),
            display_name='X & Y correlation loadings')

        # Y_corrLoadings()
        # corr_loadings_y
        mYcl = pls_obj.Y_corrLoadings()
        res.corr_loadings_y = ds.DataSet(
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
