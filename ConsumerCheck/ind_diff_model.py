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
from hoggorm import nipalsPCA as PCA
from hoggorm import nipalsPLS2 as PLSR
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

    # Standardise
    standardise_x = _traits.Bool()

    # Calculated PCA for the response variable
    pca_L = _traits.Property()

    settings = _traits.WeakRef()
    # checkbox bool for standardised results
    calc_n_pc = _traits.Int()
    min_pc = 2
    max_pc = 10

    # Selection of variables to dummify
    dummify_variables = _traits.ListUnicode()
    consumer_variables = _traits.ListUnicode()

    # Liking PC to use in PLS
    selected_liking_pc = _traits.List(_traits.Int)
    n_Y_pc = _traits.List([(0,'PC-1'),(1,'PC-2'),(2,'PC-3')])
    selected_segments = _traits.Instance(ds.Factor)
    num_segments = _traits.Int(0)

    # Export buttons
    ev_export_dummified = _traits.Button("Export dummified variables to 'Data sets' tab")
    ev_export_segments = _traits.Button("Export consumer segments to 'Data sets' tab")
    ev_remove_segments = _traits.Button("Remove segments")

    min_std = _traits.Float(0.001)
    L_zero_std = _traits.List()


    @_traits.on_trait_change('ev_remove_segments')
    def _zero(self, obj, name, old, new):
        calc = self.owner.calculations[0].model
        calc.selected_segments.levels = {}


    @_traits.on_trait_change('ev_export_segments')
    def _one(self, obj, name, old, new):
        calc = self.owner.calculations[0].model
        dsy_sd = calc.make_liking_dummy_segmented(calc.selected_segments)
        dsy_sd.display_name += '_segments'
        self.owner.dsc.add(dsy_sd)


    @_traits.on_trait_change('ev_export_dummified')
    def _two(self, obj, name, old, new):
        calc = self.owner.calculations[0].model
        dummy = calc.ds_X
        dummy.display_name += '_dummified'
        self.owner.dsc.add(dummy)


    @_traits.on_trait_change('selected_segments:levels')
    def track_segments(self, obj, name, old, new):
        self.settings.num_segments = len(obj.levels)


    def _get_pca_L(self):
        if self._L_have_zero_std_var():
            raise InComputeable(
                'Matrix have variables with zero variance', self.L_zero_std)
        cpca = PCA(self.ds_L.values, numComp=3, Xstand=False, cvType=["loo"])
        return ra.adapt_oto_pca(cpca, self.ds_L, self.ds_L.display_name)


    def _L_have_zero_std_var(self):
        self.L_zero_std = self._check_zero_std(self.ds_L)
        return bool(self.L_zero_std)


    def _check_zero_std(self, ds):
        zero_std_var = []
        sv = ds.values.std(axis=0)
        dm = sv < self.min_std
        if _np.any(dm):
            vv = _np.array(ds.var_n)
            zero_std_var = list(vv[_np.nonzero(dm)])
        return zero_std_var


    def calc_pls_raw_liking(self):
        n_pc = 2
        dsx = self.ds_X
        dsy = self.ds_Y
        plsr = PLSR(dsx.values, dsy.values, numComp=n_pc, cvType=["loo"], Xstand=self.standardise_x, Ystand=False)
        title = 'PLSR({0} ~ {1})'.format(dsx.display_name, dsy.display_name)
        return ra.adapt_oto_plsr(plsr, dsx, dsy, title)


    def calc_pls_pc_likings(self, pc_sel):
        n_pc = 2
        dsx = self.ds_X
        dsy = self.pca_L.loadings
        dsy.mat = dsy.mat.iloc[:,pc_sel]
        plsr = PLSR(dsx.values, dsy.values, numComp=n_pc, cvType=["loo"], Xstand=self.standardise_x, Ystand=False)
        title = 'PLSR({0} ~ {1})'.format(dsx.display_name, dsy.display_name)
        return ra.adapt_oto_plsr(plsr, dsx, dsy, title)


    def calc_plsr_da(self, segments):
        '''Process
        Add a row for each segments
        Loop throu each segment row and set 1 where we have index and 0 for the rest
        do this via property - no then segments have to be part of model
        Hmmm
        Add dummy segments to attr array as vel
        '''
        if len(segments) < 1:
            # FIXME: Show warning, no segments defined
            return

        dsx = segments.get_combined_levels_subset(self.ds_X, axis=0)

        dsy = self.make_liking_dummy_segmented(segments)
        dsy = dsy.copy(transpose=True)

        n_pc = 2
        plsr = PLSR(dsx.values, dsy.values, numComp=n_pc, cvType=["loo"], Xstand=self.standardise_x, Ystand=False)
        title = 'PLSR-DA({0} ~ {1})'.format(dsx.display_name, dsy.display_name)
        return ra.adapt_oto_plsr(plsr, dsx, dsy, title)


    def make_liking_dummy_segmented(self, segments):
        dsy_sd = segments.get_combined_levels_subset(self.ds_Y, axis=0)

        index = segments.levels.keys()
        columns = segments.get_combined_levels_labels(self.ds_Y, axis=0)
        segs = _pd.DataFrame(0, index=index, columns=columns)
        for lvn, lv in segments.levels.iteritems():
            cols = lv.get_labels(self.ds_Y, 0)
            segs.loc[lvn,cols] = 1

        dsy_sd.mat = segs
        return dsy_sd


    def _get_res(self):
        return None


    def _get_ds_X(self):
        """Get the independent variable X that is the consumer attributes"""
        varn = [str(v) for v in self.settings.dummify_variables]
        dsa = self.ds_A.copy(transpose=False)
        dsx = df.dummify(dsa, varn)
        return dsx


    def _get_ds_Y(self):
        """Get the response variable that is the consumer liking"""
        return self.ds_L.copy(transpose=True)


    def _calc_n_pc_default(self):
        return self.max_pc
