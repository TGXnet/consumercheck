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

# Std lib imports
import logging
logger = logging.getLogger('tgxnet.nofima.cc.'+__name__)
import __builtin__
import os.path as op
import string
from threading import Thread
from itertools import combinations

# Scipy imports
import pyper
import numpy as np
import pandas as _pd

# Local imports
from dataset import DataSet
from plugin_base import Result


# Monkey patch PypeR to allow numeric axis names
# FIXME: I should instead file a bugfix for PypeR
def CCPandasDataFrameStr(obj):
	# DataFrame will be converted to data.frame, have to explicitly name columns
	# return 'data.frame(%s, row.names=%s)' % (', '.join(map(lambda a,b=obj:a+'='+getVec(obj[a]), obj)), getVec(obj.index))
	cp = ["'{0}'={1}".format(p, getVec(q)) for p, q in obj.iteritems()]
	cols = ', '.join(cp)
	return 'data.frame({0}, row.names={1}, check.names=FALSE)'.format(cols, getVec(obj.index))

# FIXM: Do i realy need to do this
# Think is was to allow numeric column and index names
# pyper.PandasDataFrameStr = CCPandasDataFrameStr


class ConjointMachine(object):

    def __init__(self, run_state=None, start_r=True):
        # Set root folder for R
        # When this is bbfreeze'ed this file is packed into the
        # library.zip file
        # self.r_origo = op.dirname(op.dirname(op.abspath(__file__)))
        # cc_base_dir from __builtin__ set in consumercheck
        if hasattr(__builtin__, "cc_base_dir"):
            self.r_origo = __builtin__.cc_base_dir
        else:
            self.r_origo = op.dirname(op.abspath(__file__))

        if run_state:
            self.run_state=run_state
        else:
            self.run_state=None
        self.conjoint_calc_thread = None
        if start_r:
            self._start_r_interpreter()
            self._load_conjoint_resources()
            logger.info("R env setup completed")


    def _start_r_interpreter(self):
        Rwbin = op.join(self.r_origo, 'R-3.0.2', 'bin', 'R.exe')
        Rubin = op.join(self.r_origo, 'R-3.0.2', 'bin', 'R')
        Rlib = op.join(self.r_origo, 'R-3.0.2', 'library')
        logger.info("Try Windows R path: {0}".format(Rwbin))
        logger.info("Try Mac OSX R path: {0}".format(Rubin))
        if op.exists(Rwbin):
            logger.info("R.exe found")
            self.r = pyper.R(RCMD=Rwbin, use_pandas=True)
            self.r('.libPaths("{0}")'.format(Rlib))
        elif op.exists(Rubin):
            logger.info("R found")
            self.r = pyper.R(RCMD=Rubin, use_pandas=True)
            self.r('.libPaths("{0}")'.format(Rlib))
        else:
            Rbin = 'R'
            logger.info("R.exe not found, so we are depending on system wide R installation")
            self.r = pyper.R(RCMD=Rbin, use_pandas=True)


    def _load_conjoint_resources(self):
        self.r('library(Hmisc)')
        self.r('library(lmerTest)')
        # Set R working directory independent of Python working directory
        r_wd = op.join(self.r_origo, "rsrc")
        self.r('setwd("{0}")'.format(r_wd))
        self.r('source("conjoint.r")')
        # Diagnostic to loggin system
        r_env = 'R environment\n'
        r_env += self.r('sessionInfo()')
        r_env += self.r('getwd()')
        r_env += self.r('.libPaths()')
        r_env += self.r('search()')
        r_env += self.r('objects()')
        logger.info(r_env)


    def synchronous_calculation(self, design, selected_designVars,
                                consLiking, structure=1,
                                consAtts=None, selected_consAtts=[]):
        """Starts a conjoint calculation and return when the result is ready
        Parameters:
         * structure: 1, 2 or 3
         * consAttrs: ds type
         * selected_consAttrs: List with consAttrs column names
         * design: ds type
         * selected_designVars: List with design column names
         * consLiking: ds type
         in python or in R.
        """
        self._prepare_data(structure, consAtts, selected_consAtts,
                           design, selected_designVars, consLiking)

        ## print(self.headerList)
        ## np.set_printoptions(threshold=100, edgeitems=10)
        ## print(self.finalData)
        self._copy_values_into_r_env()
        self._run_conjoint()
        return self.get_result()


    def schedule_calculation(self, design, selected_designVars,
                             consLiking, structure=1,
                             consAtts=None, selected_consAtts=[]):
        """Starts a conjoint calculation and return when the result is ready
        Parameters:
         * structure: 1, 2 or 3
         * consAttrs: ds type
         * selected_consAttrs: List with consAttrs column names
         * design: ds type
         * selected_designVars: List with design column names
         * consLiking: ds type
         in python or in R.
        """

        if self.conjoint_calc_thread and self.conjoint_calc_thread.is_alive():
            print("Calculation is already running")
        else:
            self._prepare_data(structure, consAtts, selected_consAtts,
                               design, selected_designVars, consLiking)
            self._copy_values_into_r_env()
            self.conjoint_calc_thread = ConjointCalcThread(target=None, args=(), kwargs={})
            self.conjoint_calc_thread.conj = self
            self.conjoint_calc_thread.run_state = self.run_state
            self.conjoint_calc_thread.start()


    def _prepare_data(self, structure, consAtts, selected_consAtts,
                      design, selected_designVars, consLiking):

        self.structure = structure
        self.consAtts = consAtts
        self.selected_consAtts = asciify(selected_consAtts)
        self.design = design
        self.selected_designVars = asciify(selected_designVars)
        self.consLiking = consLiking
        self.consLikingTag = only_letters(consLiking.display_name)

        # self._check_completeness()
        self._data_merge()


    def _check_completeness(self):
        '''FIXME: What is a proper name for this'''
        for comb in combinations(self.selected_consAtts, 2):
            self._check2d_interaction(*comb)


    def _check2d_interaction(self, attr1, attr2):
        from pprint import pprint
        print(attr1, attr2)
        vns = self.consAtts.var_n
        mat = self.consAtts.values
        ind1 = vns.index(attr1)
        ind2 = vns.index(attr2)
        uniq1 = np.unique(mat[:,ind1])
        uniq2 = np.unique(mat[:,ind2])
        if len(uniq1) < len(uniq2):
            xuniq, yuniq = uniq1, uniq2
        else:
            yuniq, xuniq = uniq1, uniq2
        hist = []
        for val in xuniq:
            mask = mat[:,ind1] == val
            vec = mat[mask,ind2]
            hst = np.bincount(vec, minlength=(len(yuniq)+1))
            hist.append(hst[1:])
        up = np.array(hist)
        pprint(up)
        if not np.all(up, axis=None):
            print("Feilet test")
            fm = np.all(up, axis=0)
            fm = np.logical_not(fm)
            print(up[:,fm])



    def _numeric_category_vector(self, str_categories):
        """FIXME: Not used yet"""
        # Categories Set
        cs = frozenset(str_categories)
        # Check if all categories is unique
        if len(cs) == len(str_categories):
            return range(len(str_categories))
        # Unique Categories List
        ucl = list(cs)
        # FIXME: I should try to implements som quasi string numeric sorting
        # to handle values like:
        # u'E-1', u'E-2', u'E-3',...,u'E-118'
        ucl.sort()
        return [ucl.index(el) for el in str_categories]


    def _data_merge(self):
        # Merge data from the following data arrays: consumer liking,
        # consumer attributes and design
        
        # Get content from design array
        desData = self.design.values
        desVarNames = self.design.var_n
        
        # Get content form cosumer liking array
        consData = self.consLiking.values
        consVarNames = self.consLiking.var_n
        
        # Get content from consumer attributes array
        if self.consAtts and not self.consAtts.mat.empty:
            attrData = self.consAtts.values
            attrVarNames = self.consAtts.var_n
        
        # Make list with column names
        self.headerList = ['Consumer', self.consLikingTag]
        self.headerList.extend(desVarNames)
        if self.consAtts and not self.consAtts.mat.empty:
            self.headerList.extend(attrVarNames)

        # Now construct conjoint values
        # -----------------------------
        allConsList = []
        consRows = np.shape(desData)[0]
        
        # First loop through all consumers
        for consInd, cons in enumerate(consVarNames):
            consList = []
            
            # Construct and append ID for the specific consumer
            consIDvec = np.array([consInd] * consRows).reshape(-1,1)
            consList.append(consIDvec)
            
            # Append liking of the specific consumer
            consList.append(consData[:,consInd].reshape(-1,1))
            
            # Append design matrix
            consList.append(desData)
        
            # Append consumer attributes for each row (there are as many rows as there
            # are products for the specific consumer)   
            attrBlockList = []
            if self.consAtts and not self.consAtts.mat.empty:
                attrList = attrData[consInd,:]
                for rowInd in range(consRows):
                    attrBlockList.append(attrList)
                consList.append(np.vstack(attrBlockList))
            
            # Convert consumer specific entry to an array and collect in allConsList
            consArr = np.hstack(consList)
            allConsList.append(consArr)
        
        # Put all information into the final data array
        self.finalData = _pd.DataFrame(np.vstack(allConsList), columns=self.headerList)


    def _copy_values_into_r_env(self):
        # R merge
        self.r['conjDF'] = self.finalData

        # Construct R list with R lists of product design variables as well as
        # consumer attributes.

        # Construct string holding design variables that is needed for 
        # construction of rCommand_fixedFactors
        selDesVarStr = ', '.join(
            ['"{0}"'.format(var) for var in self.selected_designVars])

        # Construct string holding consumer attributes that is needed for 
        # construction of rCommand_fixedFactors
        selConsAttStr = ', '.join(
            ['"{0}"'.format(attr) for attr in self.selected_consAtts])

        ## if len(self.selected_consAtts) == 1:
        ##     rCommand_fixedFactors = 'fixed <- list(Product=c({0}), Consumer={1})'.format(selDesVarStr, selConsAttStr)
        ## else:
        ##     rCommand_fixedFactors = 'fixed <- list(Product=c({0}), Consumer=c({1}))'.format(selDesVarStr, selConsAttStr)
        rCommand_fixedFactors = 'fixed <- list(Product=c({0}), Consumer=c({1}))'.format(selDesVarStr, selConsAttStr)

        self.r(rCommand_fixedFactors)

        # Define which factors are random and construct R list with all
        # factors, both random and fixed. Define also response since the
        # name will be used in result tables.
        self.r['random'] = 'Consumer'
        self.r['response'] = self.consLikingTag

        facs = ['Consumer']
        facs.extend(self.selected_designVars)
        facs.extend(self.selected_consAtts)
        self.r['facs'] = facs
        # Diagnostics
        r_state = 'Object in R after all data is transferred\n'
        r_state += self.r('objects()')
        logger.info(r_state)


    def _run_conjoint(self):
        rCommand_runAnalysis = self.get_conj_r_cmd()
        r_resp = self.r(rCommand_runAnalysis)
        logger.info(r_resp)
        # Diagnostics
        r_state = 'Object in R after calculation is done\n'
        r_state += self.r('objects()')
        logger.info(r_state)


    def get_conj_r_cmd(self):
        rCommand_runAnalysis = 'res <- conjoint(structure={0}, conjDF, response, fixed, random, facs)'.format(self.structure)
        return rCommand_runAnalysis


    def get_result(self):
        result = Result('Conjoint {0}'.format(self.design.display_name))
        result.randomTable = self._r_res_to_ds(
            'res[[1]][1]$rand.table',
            'ANOVA table for random effects')
        result.anovaTable = self._r_res_to_ds(
            'res[[1]][2]$anova.table',
            'ANOVA table for fixed effects')
        result.lsmeansDiffTable = self._r_res_to_ds(
            'res[[1]][4]$diffs.lsmeans.table',
            'Pair-wise differences')
        result.lsmeansTable = self._lsMeansTable()
        result.residualsTable = self._residualsTable()
        result.residIndTable = self._residIndTable()
        result.meanLiking = self._calcMeanLiking()

        return result


    def _cn_strip(self, r_expr):
        '''R conjoint returns some arrays with spaces around variable names
        
        This function strips this spaces out.
        This is required if i use PypeR 1.1.2
        '''
        df = self.r.get(r_expr)
        df.columns = [cn.strip() for cn in df.columns]
        return df


    def _r_res_to_ds(self, r_ref, ds_name):
        df = self._cn_strip(r_ref)
        return DataSet(mat=df, display_name=ds_name)


    def _lsMeansTable(self):
        ls1 = self._cn_strip('res[[1]][3]$lsmeans.table')
        ls2 = ls1.drop(['p-value'], axis=1)
        return DataSet(mat=ls2, display_name='LS means (main effect and interaction)')


    def _residualsTable(self):
        """
        Returns residuals from R conjoint function.
        """
        # Get size of liking data array. 
        n_rows, n_cols = np.shape(self.consLiking.values)

        r_vec = self.r.get('res[[1]][5]$residuals')
        vals = np.reshape(r_vec, (n_rows, n_cols))
        val_df = _pd.DataFrame(vals, index=self.consLiking.obj_n, columns=self.consLiking.var_n)
        res_ds = DataSet(mat=val_df, display_name='Full model residuals')

        return res_ds


    def _residIndTable(self):
        """
        Returns residuals from R conjoint function.
        """
        # Get size of liking data array. 
        n_rows, n_cols = np.shape(self.consLiking.values)

        # r_vec = self.r.get('res[[1]][6]$residuals_Indiv')
        r_vec = self.r.get('res[[1]][6]$residualsDoubleCentered')
        vals = np.reshape(r_vec, (n_rows, n_cols))
        val_df = _pd.DataFrame(vals, index=self.consLiking.obj_n, columns=self.consLiking.var_n)
        res_ds = DataSet(mat=val_df, display_name='Double centred residuals')

        return res_ds


    def _calcMeanLiking(self):
        return np.mean(self.consLiking.values)


class ConjointCalcThread(Thread):

    def run(self):
        self.run_state.is_done = False
        self.run_state.messages = 'Starts calculating\n'
        rCommand_runAnalysis = self.conj.get_conj_r_cmd()
        self.run_state.messages += self.conj.r(rCommand_runAnalysis)
        self.run_state.messages += 'End calculation\n'
        self.run_state.is_done = True


def asciify(names):
    """Take a list of unicodes and turn each elemet into ascii strings"""
    return [str(n).encode('ascii', 'ignore') for n in names]


def only_letters(name):
    # Make list of character to trow away
    throw_chrs = string.maketrans(
        string.ascii_letters, ' '*len(string.ascii_letters))
    # Filter data set name
    ascii_name = name.encode('ascii', 'ignore')
    return ascii_name.translate(None, throw_chrs)


if __name__ == '__main__':
    print("Hello World")
    logging.basicConfig(level=logging.DEBUG)
    logger.info('Start interactive')
    from dataset_container import get_ds_by_name
    from tests.conftest import conjoint_dsc
    cm = ConjointMachine(start_r=True)

    selected_structure = 1
    dsc = conjoint_dsc()
    consAttr = get_ds_by_name('Consumers', dsc)
    odflLike = get_ds_by_name('Odour-flavor', dsc)
    consistencyLike = get_ds_by_name('Consistency', dsc)
    overallLike = get_ds_by_name('Overall', dsc)
    designVar = get_ds_by_name('Tine yogurt design', dsc)
    selected_consAttr = ['Sex']
    selected_designVar = ['Flavour', 'Sugarlevel']
    empty = DataSet()

#     res = cm.synchronous_calculation(designVar, selected_designVar, odflLike)
    res = cm.synchronous_calculation(designVar, selected_designVar,
                                     odflLike, selected_structure,
                                     empty, [])
    res.print_traits()
    print(res.residualsTable.mat)
    print(res.residIndTable.mat)
