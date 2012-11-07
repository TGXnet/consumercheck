
# Import necessary modules
import os
import string
import pyper
import numpy as np
from threading import Thread


def asciify(names):
    """Take a list of unicodes an tur each elemet into ascii strings"""
    return [n.encode('ascii', 'ignore') for n in names]


class ConjointCalcThread(Thread):

    def run(self):
        self.run_state.is_done = False
        self.run_state.messages = 'Starts calculating\n'
        rCommand_runAnalysis = 'res.gm <- conjoint(structure={0}, consum.attr=consum.attr, design.matr=design.matr, list.consum.liking=list.consum.liking, response, fixed, random, facs)'.format(self.structure)
        self.run_state.messages += self.r(rCommand_runAnalysis)
        self.run_state.messages += 'End calculation\n'
        self.run_state.is_done = True



class ConjointMachine(object):


    def __init__(self, run_state=None):
        # Set root folder for R
        self.r_origo = os.path.dirname(os.path.abspath(__file__))
        ## self.r_origo = os.getcwd()

        if run_state:
            self.run_state=run_state
        else:
            self.run_state=None
        self.conjoint_calc_thread = None
        self._start_r_interpreter()
        self._load_conjoint_resources()


    def _start_r_interpreter(self):
        Rbin = os.path.join(self.r_origo, 'R-2.15.1', 'bin', 'R.exe')
        try:
            self.r = pyper.R(Rbin)
        # On MSWIN is an WindowsError which is a subclass of OSError raised.
        except OSError:
            self.r = pyper.R()


    def _load_conjoint_resources(self):
        self.r('library(MixMod)')
        self.r('library(Hmisc)')
        self.r('library(lme4)')
        # Set R working directory independent of Python working directory
        self.r('setwd("{0}")'.format(self.r_origo))
        self.r('source("pgm/conjoint.r")'.format(self.r_origo))
        print(self.r('.libPaths()'))
        print(self.r('search()'))
        print(self.r('objects()'))


    def synchronous_calculation(self, structure,
                             consAtts, selected_consAtts,
                             design, selected_designVars,
                             consLiking):
        pass
        """Doc here"""
        self.structure = structure
        self.consAtts = consAtts
        self.selected_consAtts = asciify(selected_consAtts)
        self.design = design
        self.selected_designVars = asciify(selected_designVars)
        self.consLiking = consLiking

        # Generate consumer liking tag acceptable for R
        # Make list of character to trow away
        throw_chrs = string.maketrans(string.ascii_letters, ' '*len(string.ascii_letters))
        # Filter dataset name
        liking_name = consLiking._ds_name.encode('ascii', 'ignore')
        self.consLikingTag = liking_name.translate(None, throw_chrs)

        self._copy_values_into_r_env()
        self._run_conjoint()
        return self.get_result()




    def schedule_calculation(self, structure,
                             consAtts, selected_consAtts,
                             design, selected_designVars,
                             consLiking):
        """Doc here"""
        self.structure = structure
        self.consAtts = consAtts
        self.selected_consAtts = asciify(selected_consAtts)
        self.design = design
        self.selected_designVars = asciify(selected_designVars)
        self.consLiking = consLiking

        # Generate consumer liking tag acceptable for R
        # Make list of character to trow away
        throw_chrs = string.maketrans(string.ascii_letters, ' '*len(string.ascii_letters))
        # Filter dataset name
        liking_name = consLiking._ds_name.encode('ascii', 'ignore')
        self.consLikingTag = liking_name.translate(None, throw_chrs)

        self._copy_values_into_r_env()

        if self.conjoint_calc_thread and self.conjoint_calc_thread.is_alive():
            print("Calculation is already running")
        else:
            self.conjoint_calc_thread = ConjointCalcThread(target=None, args=(), kwargs={})
            self.conjoint_calc_thread.r = self.r
            self.conjoint_calc_thread.run_state = self.run_state
            self.conjoint_calc_thread.structure = self.structure
            self.conjoint_calc_thread.start()
        # self._run_conjoint()


    def _copy_values_into_r_env(self):
        self.r['consAttMat'] = self.consAtts.matrix
        self.r['consAttVars'] = asciify(self.consAtts.variable_names)
        self.r['consAttObj'] = asciify(self.consAtts.object_names)
        self.r('consum.attr <- as.data.frame(consAttMat)')
        self.r('colnames(consum.attr) <- consAttVars')
        self.r('rownames(consum.attr) <- consAttObj')

        self.r['designMat'] = self.design.matrix
        self.r['designVars'] = asciify(self.design.variable_names)
        self.r['designObj'] = asciify(self.design.object_names)
        self.r('design.matr <- as.data.frame(designMat)')
        self.r('colnames(design.matr) <- designVars')
        self.r('rownames(design.matr) <- designObj')

        self.r['consLikingMat'] = self.consLiking.matrix
        self.r['consLikingVars'] = asciify(self.consLiking.variable_names)
        self.r['consLikingObj'] = asciify(self.consLiking.object_names)
        self.r('cons.liking <- as.data.frame(consLikingMat)')
        self.r('colnames(cons.liking) <- consLikingVars')
        self.r('rownames(cons.liking) <- consLikingObj')

        # Construct a list in R space that holds data and names of liking matrices
        rCommand_buildLikingList = 'list.consum.liking <- list(matr.liking=list({0}), names.liking=c("{1}"))'.format('cons.liking', self.consLikingTag)
        self.r(rCommand_buildLikingList)

        # Construct R list with R lists of product design variables as well as
        # consumer attributes.

        # Construct string holding design variables that is needed for 
        # construction of rCommand_fixedFactors
        for desInd, desVar in enumerate(self.selected_designVars):

            if desInd == 0:
                selDesVarStr = '"{0}"'.format(self.selected_designVars[desInd])

            else:
                newStrPart = '"{0}"'.format(self.selected_designVars[desInd])
                selDesVarStr = selDesVarStr + ',' + newStrPart

        # Construct string holding consumer attributes that is needed for 
        # construction of rCommand_fixedFactors
        for consInd, consAtt in enumerate(self.selected_consAtts):

            if consInd == 0:
                selConsAttStr = '"{0}"'.format(self.selected_consAtts[consInd])

            else:
                newStrPart = '"{0}"'.format(self.selected_consAtts[consInd])
                selConsAttStr = selConsAttStr + ',' + newStrPart

        rCommand_fixedFactors = 'fixed <- list(Product=c({0}), Consumer={1})'.format(selDesVarStr, selConsAttStr)
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



    def _run_conjoint(self):
        rCommand_runAnalysis = 'res.gm <- conjoint(structure={0}, consum.attr=consum.attr, design.matr=design.matr, list.consum.liking=list.consum.liking, response, fixed, random, facs)'.format(self.structure)
        print(self.r(rCommand_runAnalysis))


    def get_result(self):
        result = {}
        result['randomTable'] = self._randomTable()
        result['anovaTable'] = self._anovaTable()
        result['lsmeansTable'] = self._lsmeansTable()
        result['lsmeansDiffTable'] = self._lsmeansDiffTable()
        result['residualsTable'] = self._residualsTable()

        return result


    def _randomTable(self):
        """
        Returns random table from R conjoint function.
        """
        self.r('randTab <- res.gm[[1]][1]')

        randTableDict = {}
        randTableDict['data'] = self.r['randTab']['rand.table']
        randTableDict['colNames'] = self.r['colnames(randTab$rand.table)']
        randTableDict['rowNames'] = self.r['rownames(randTab$rand.table)']

        return randTableDict


    def _anovaTable(self):
        """
        Returns ANOVA table from R conjoint function.
        """
        self.r('anovaTab <- res.gm[[1]][2]')

        anovaTableDict = {}
        anovaTableDict['data'] = self.r['anovaTab']['anova.table']
        anovaTableDict['colNames'] = self.r['colnames(anovaTab$anova.table)']
        anovaTableDict['rowNames'] = self.r['rownames(anovaTab$anova.table)']

        return anovaTableDict


    def _lsmeansTable(self):
        """
        Returns LS means table from R conjoint function.
        """
        self.r('lsmeansTab <- res.gm[[1]][3]')

        lsmeansTableDict = {}
        lsmeansTableDict['data'] = self.r['lsmeansTab']['lsmeans.table']
        lsmeansTableDict['colNames'] = self.r['colnames(lsmeansTab$lsmeans.table)']
        lsmeansTableDict['rowNames'] = self.r['rownames(lsmeansTab$lsmeans.table)']

        return lsmeansTableDict


    def _lsmeansDiffTable(self):
        """
        Returns table of differences between LS means from R conjoint function.
        """
        self.r('lsmeansDiffTab <- res.gm[[1]][4]')

        lsmeansDiffTableDict = {}
        lsmeansDiffTableDict['data'] = self.r['lsmeansDiffTab']['diffs.lsmeans.table']
        lsmeansDiffTableDict['colNames'] = self.r['colnames(lsmeansDiffTab$diffs.lsmeans.table)']
        lsmeansDiffTableDict['rowNames'] = self.r['rownames(lsmeansDiffTab$diffs.lsmeans.table)']

        return lsmeansDiffTableDict


    def _residualsTable(self):
        """
        Returns residuals from R conjoint function.
        """
        # Get size of liking data array. 
        numRows, numCols = np.shape(self.consLiking.matrix)

        self.r('residTab <- res.gm[[1]][5]')

        residTableDict = {}
        residTableDict['data'] = np.reshape(
            self.r['residTab']['residuals'],
            (numRows, numCols))

        residTableDict['rowNames'] = self.consLiking.object_names
        residTableDict['colNames'] = self.consLiking.variable_names

        return residTableDict


if __name__ == '__main__':
    print("Hello World")
    cm = ConjointMachine()
