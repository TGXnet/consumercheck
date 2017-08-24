
# Scipy libs imports
import numpy as _np
import pandas as _pd

# Local imports
from dataset import DataSet
from plugin_base import Result


def adapt_oto_pca(pca, dsx, res_name):
    res = Result('PCA {0}'.format(res_name))

    # Scores
    mT = pca.X_scores()
    res.scores = DataSet(
        mat=_pd.DataFrame(
            data=mT,
            index=dsx.obj_n,
            columns=["PC-{0}".format(i+1) for i in range(mT.shape[1])],
        ),
        # FIXME: should not asign subs here
        subs=dsx.subs,
        display_name='Scores')

    # Loadings
    mP = pca.X_loadings()
    res.loadings = DataSet(
        mat=_pd.DataFrame(
            data=mP,
            index=dsx.var_n,
            columns=["PC-{0}".format(i+1) for i in range(mP.shape[1])],
        ),
        display_name='Loadings')

    # Correlation loadings
    mCL = pca.X_corrLoadings()
    res.corr_loadings = DataSet(
        mat=_pd.DataFrame(
            data=mCL,
            index=dsx.var_n,
            columns=["PC-{0}".format(i+1) for i in range(mCL.shape[1])],
        ),
        display_name='Correlation loadings')

    # Explained variance
    cal = pca.X_calExplVar()
    cum_cal = pca.X_cumCalExplVar()[1:]
    val = pca.X_valExplVar()
    cum_val = pca.X_cumValExplVar()[1:]
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
    resids = pca.X_residuals()

    # predicted matrices Xhat from calibration after each computed PC.
    # FIXME: Is this X_predCal()
    # cal_pred_x = pca.calPredX()

    #validated matrices Xhat from calibration after each computed PC.
    # val_pred_x = pca.valPredX()

    # MSEE from cross validation after each computed PC.
    msee = pca.X_MSEE()

    # MSEE from cross validation after each computed PC for each variable.
    ind_var_msee = pca.X_MSEE_indVar()

    # MSECV from cross validation after each computed PC.
    msecv = pca.X_MSECV()

    # MSECV from cross validation after each computed PC for each variable.
    ind_var_msecv = pca.X_MSECV_indVar()

    return res



def adapt_sklearn_pca():
    pass



def adapt_oto_plsr(plsr, dsx, dsy):

    res = Result('PLSR {0}(X) & {1}(Y)'.format(dsx.display_name, dsy.display_name))

    # scores_x
    mT = plsr.X_scores()
    res.scores_x = DataSet(
        mat=_pd.DataFrame(
            data=mT,
            index=dsx.obj_n,
            columns=["PC-{0}".format(i+1) for i in range(mT.shape[1])],
        ),
        display_name='X scores')

    # loadings_x
    mP = plsr.X_loadings()
    res.loadings_x = DataSet(
        mat=_pd.DataFrame(
            data=mP,
            index=dsx.var_n,
            columns=["PC-{0}".format(i+1) for i in range(mP.shape[1])],
        ),
        display_name='X loadings')

    # loadings_y
    # Same as loading_x in external mapping?
    mQ = plsr.Y_loadings()
    res.loadings_y = DataSet(
        mat=_pd.DataFrame(
            data=mQ,
            index=dsy.var_n,
            columns=["PC-{0}".format(i+1) for i in range(mQ.shape[1])],
        ),
        display_name='Y loadings')

    # expl_var_x
    cal = plsr.X_calExplVar()
    cum_cal = plsr.X_cumCalExplVar()[1:]
    val = plsr.X_valExplVar()
    cum_val = plsr.X_cumValExplVar()[1:]
    res.expl_var_x = DataSet(
        mat=_pd.DataFrame(
            data=[cal, cum_cal, val, cum_val],
            index=['calibrated', 'cumulative calibrated', 'validated', 'cumulative validated'],
            columns=["PC-{0}".format(i+1) for i in range(len(cal))],
        ),
        display_name='Explained variance in X')

    # expl_var_y
    cal = plsr.Y_calExplVar()
    cum_cal = plsr.Y_cumCalExplVar()[1:]
    val = plsr.Y_valExplVar()
    cum_val = plsr.Y_cumValExplVar()[1:]
    res.expl_var_y = DataSet(
        mat=_pd.DataFrame(
            data=[cal, cum_cal, val, cum_val],
            index=['calibrated', 'cumulative calibrated', 'validated', 'cumulative validated'],
            columns=["PC-{0}".format(i+1) for i in range(len(cal))],
        ),
        display_name='Explained variance in Y')

    # X_corrLoadings()
    # corr_loadings_x
    mXcl = plsr.X_corrLoadings()
    res.corr_loadings_x = DataSet(
        mat=_pd.DataFrame(
            data=mXcl,
            index=dsx.var_n,
            columns=["PC-{0}".format(i+1) for i in range(mXcl.shape[1])],
        ),
        display_name='X & Y correlation loadings')

    # Y_corrLoadings()
    # corr_loadings_y
    mYcl = plsr.Y_corrLoadings()
    res.corr_loadings_y = DataSet(
        mat=_pd.DataFrame(
            data=mYcl,
            index=dsy.var_n,
            columns=["PC-{0}".format(i+1) for i in range(mXcl.shape[1])],
        ),
        display_name=dsy.display_name)

    # Y_predCal()
    # Return a dict with Y pred for each PC
    pYc = plsr.Y_predCal()
    ks = pYc.keys()
    pYcs = [_mk_pred_ds(pYc[k], k, dsy) for k in ks]
    res.pred_cal_y = pYcs

    # Y_predVal()
    # Return a dict with Y pred for each PC
    pYv = plsr.Y_predVal()
    ks = pYv.keys()
    pYvs = [_mk_pred_ds(pYv[k], k, dsy) for k in ks]
    res.pred_val_y = pYvs

    return res


def adapt_sklearn_pls(pls, dsx, dsy, yname):

    res = Result('IndDiff {0}(X) & {1}(Y)'.format(
        dsx.display_name, yname))

    # Scores X
    mT = pls.x_scores_
    res.scores_x = DataSet(
        mat=_pd.DataFrame(
            data=mT,
            index=dsx.obj_n,
            columns=["PC-{0}".format(i+1) for i in range(mT.shape[1])],
        ),
        # subs=dsx.subs,
        display_name='X scores')

    # loadings_x
    mP = pls.x_loadings_
    res.loadings_x = DataSet(
        mat=_pd.DataFrame(
            data=mP,
            index=dsx.var_n,
            columns=["PC-{0}".format(i+1) for i in range(mP.shape[1])],
        ),
        display_name='X loadings')

    # loadings_y
    # Same as loading_x in external mapping?
    mQ = pls.y_loadings_
    res.loadings_y = DataSet(
        mat=_pd.DataFrame(
            data=mQ,
            # index=dsy.var_n,
            columns=["PC-{0}".format(i+1) for i in range(mQ.shape[1])],
        ),
        display_name='Y loadings')
    # print(res.scores_x.mat)
    # print(res.loadings_x.mat)
    # res.loadings_y.print_traits()

    # expl_var_x
    # cal = pls.X_calExplVar()
    # cum_cal = pls.X_cumCalExplVar()[1:]
    # val = pls.X_valExplVar()
    # cum_val = pls.X_cumValExplVar()[1:]
    # res.expl_var_x = DataSet(
    #     mat=_pd.DataFrame(
    #         data=[cal, cum_cal, val, cum_val],
    #         index=['calibrated', 'cumulative calibrated', 'validated', 'cumulative validated'],
    #         columns=["PC-{0}".format(i+1) for i in range(len(cal))],
    #     ),
    #     display_name='Explained variance in X')

    # # expl_var_y
    # cal = pls.Y_calExplVar()
    # cum_cal = pls.Y_cumCalExplVar()[1:]
    # val = pls.Y_valExplVar()
    # cum_val = pls.Y_cumValExplVar()[1:]
    # res.expl_var_y = DataSet(
    #     mat=_pd.DataFrame(
    #         data=[cal, cum_cal, val, cum_val],
    #         index=['calibrated', 'cumulative calibrated', 'validated', 'cumulative validated'],
    #         columns=["PC-{0}".format(i+1) for i in range(len(cal))],
    #     ),
    #     display_name='Explained variance in Y')

    # # X_corrLoadings()
    # # corr_loadings_x
    # mXcl = pls.X_corrLoadings()
    # res.corr_loadings_x = DataSet(
    #     mat=_pd.DataFrame(
    #         data=mXcl,
    #         index=dsx.var_n,
    #         columns=["PC-{0}".format(i+1) for i in range(mXcl.shape[1])],
    #     ),
    #     display_name='X & Y correlation loadings')

    # # Y_corrLoadings()
    # # corr_loadings_y
    # mYcl = pls.Y_corrLoadings()
    # res.corr_loadings_y = DataSet(
    #     mat=_pd.DataFrame(
    #         data=mYcl,
    #         index=dsy.var_n,
    #         columns=["PC-{0}".format(i+1) for i in range(mXcl.shape[1])],
    #     ),
    #     display_name=dsy.display_name)

    # # Y_predCal()
    # # Return a dict with Y pred for each PC
    # pYc = pls.Y_predCal()
    # ks = pYc.keys()
    # pYcs = [_mk_pred_ds(pYc[k], k) for k in ks]
    # res.pred_cal_y = pYcs

    # # Y_predVal()
    # # Return a dict with Y pred for each PC
    # pYv = pls.Y_predVal()
    # ks = pYv.keys()
    # pYvs = [_mk_pred_ds(pYv[k], k) for k in ks]
    # res.pred_val_y = pYvs

    return res



def adapt_oto_pcr():
    pass


def _mk_pred_ds(pred_mat, npc, dsy):
    pred_ds = DataSet(
        mat=_pd.DataFrame(
            data=pred_mat,
            index=dsy.obj_n,
            columns=dsy.var_n,
        ),
        display_name='Predicted after PC{}'.format(npc))
    return pred_ds
