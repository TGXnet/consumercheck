
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



def adapt_oto_pls():
    pass



def adapt_sklearn_pls():
    pass


def adapt_oto_pcr():
    pass
