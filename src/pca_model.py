
# Scipy libs imports
import numpy as _np
import pandas as _pd

# Enthought imports
import traits.api as _traits

# Local imports
from pca import nipalsPCA as PCA
from dataset import DataSet
from dataset_container import DatasetContainer


class InComputeable(Exception):
    pass


class Pca(_traits.HasTraits):
    """Represent the PCA model of a dataset."""
    id = _traits.Str()
    ds = DataSet()
    # List of variable names with zero variance in the data vector
    zero_variance = _traits.List()

    #checkbox bool for standardised results
    standardise = _traits.Bool(False)
    calc_n_pc = _traits.Int()
    min_pc = 2
    max_pc = _traits.Property()
    min_std = _traits.Float(0.001)

    # depends_on
    pca_res = _traits.Property()


    def _get_max_pc(self):
        return max((min(self.ds.n_objs, self.ds.n_vars, 12) - 2), self.min_pc)


    def _calc_n_pc_default(self):
        return self.max_pc


    def _check_std_dev(self):
        sv = self.ds.values.std(axis=0)
        dm = sv < self.min_std
        if _np.any(dm):
            vv = _np.array(self.ds.var_n)
            self.zero_variance = list(vv[_np.nonzero(dm)])
        else:
            self.zero_variance = []


    def _get_pca_res(self):
        '''Does the PCA calculation and gets the results

        This return an results object that holds copies of the
        various result data. Each result set i an DataSet containing
        all metadata necessary for presenting the result.
        '''
        std_ds = 'cent'
        if self.standardise:
            std_ds = 'stand'
        self._check_std_dev()
        if self.zero_variance and self.standardise:
            raise InComputeable('Matrix have variables with zero variance', self.zero_variance)
        pca = PCA(self.ds.values,
                  numPC=self.calc_n_pc,
                  mode=std_ds,
                  cvType=["loo"])

        return self._pack_pca_res(pca)


    def _pack_pca_res(self, pca_obj):

        class PcaRes(object):
            pass

        res = PcaRes()

        # Scores
        mT = pca_obj.scores()
        res.scores = DataSet(
            mat=_pd.DataFrame(
                data=mT,
                index=self.ds.obj_n,
                columns=["PC-{0}".format(i+1) for i in range(mT.shape[1])],
                ),
            display_name=self.ds.display_name)

        # Loadings
        mP = pca_obj.loadings()
        res.loadings = DataSet(
            mat=_pd.DataFrame(
                data=mP,
                index=self.ds.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mP.shape[1])],
                ),
            display_name=self.ds.display_name)

        # Correlation loadings
        mCL = pca_obj.corrLoadings()
        res.corr_loadings = DataSet(
            mat=_pd.DataFrame(
                data=mCL,
                index=self.ds.var_n,
                columns=["PC-{0}".format(i+1) for i in range(mCL.shape[1])],
                ),
            display_name=self.ds.display_name)

        # Explained variance
        cal = pca_obj.calExplVar()
        val = pca_obj.valExplVar()
        res.expl_var = DataSet(
            mat=_pd.DataFrame(
                data=[cal, val],
                index=['cal', 'val'],
                columns=["PC-{0}".format(i+1) for i in range(len(cal))],
                ),
            display_name=self.ds.display_name)

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



class PcaPlugin(_traits.HasTraits):
    dsc = _traits.Instance(DatasetContainer)
    tasks = _traits.List(_traits.HasTraits)


    def add(self, task):
        self.tasks.append(task)


    def make_model(self, ds_id):
        ds = self.dsc[ds_id]
        bs = Pca(id=ds_id, ds=ds)
        return bs


    def remove(self, task_id):
        del(self.tasks[self.tasks.index(task_id)])
