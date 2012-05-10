# -*- coding: utf-8 -*-
"""
Created on Apr 19 14:46:17 2012

@author: oliver.tomic

@purpose:
Wraps Alexandra's conjoint function and accesses it via pyper
"""

# Import necessary modules
import pyper
import numpy as np

# Set up Pyper for accessing conjoint R function
r = pyper.R()

# Import R packages that are needed for compuations
# r('.libPaths("C:/Program Files/R/R-2.13.2/library")') # SPECIFIC FOR OLI'S PC
r('library(MixMod)')
r('library(Hmisc)')
r('library(lme4)')

# Set working directory where latest version of Alexandra's conjoint package
# is stored. SPECIFIC FOR OLI'S PC 
# r('dir<-"//ad.local/dfs/AAS-Users/oliver.tomic/Documents/Work/ConsumerCheck/ConjointConsumerCheck/ConjointClass"')
r('dir<-"/home/thomas/TGXnet/Prosjekter/2009-13-ConsumerCheck/ConJoint/OliverMøte_2012-05-04/ConjointConsumerCheck_27_04_2012"')
r('setwd(dir)')
r('source(paste(getwd(),"/pgm/conjoint.r",sep=""))')



class RConjoint:
    """
    A wrapper around Alexandra's conjoint function in R
    """
    
    def __init__(self, structure, \
                 consAtts, selected_consAtts, \
                 design, selected_designVars, \
                 consLiking, consLikingTag):
        """
        Input:
        ======
        
        type <structure>: integer (may take value 1, 2 or 3)
        
        type <consAtt>: class arrayIO from statTools
        
        type <selected_consAtts>: list holding strings
        
        type <design>: class arrayIO from statTools
        
        type <selected_designVars>: list holding strings
        
        type <consLiking>: class arrayIO from statTools
        
        type <consLikngTag>: string (data array tag from ConsumerCheck)
        """
        
        print; print '----- 1 -----'; print
        
        print; print 'MODEL SETTINGS' 
        print '--------------'
        print 'Structure =', structure
        print 'Consumer attributes:', selected_consAtts
        print 'Design variables:', selected_designVars
        print 'Response:', consLikingTag
        
        print; print '----- 2 -----'; print
        
        # Transfer consumer attribute data from Python to R and build data 
        # frame in R space
        r['consAttMat'] = consAtts.data
        r['consAttVars'] = consAtts.varNames
        r['consAttObj'] = consAtts.objNames
        r('consum.attr <- as.data.frame(consAttMat)')
        r('colnames(consum.attr) <- consAttVars')
        r('rownames(consum.attr) <- consAttObj')
        print(r('consum.attr'))
        
        print; print '----- 3 -----'; print
        
        r['designMat'] = design.data
        r['designVars'] = design.varNames
        r['designObj'] = design.objNames
        r('design.matr <- as.data.frame(designMat)')
        r('colnames(design.matr) <- designVars')
        r('rownames(design.matr) <- designObj')
        print(r('design.matr'))
        
        print; print '----- 4 -----'; print
        
        # Transfer odour/flavour liking data from Python to R and build data 
        # frame in R space
        r['consLikingMat'] = consLiking.data
        r['consLikingVars'] = consLiking.varNames
        r['consLikingObj'] = consLiking.objNames
        r('cons.liking <- as.data.frame(consLikingMat)')
        r('colnames(cons.liking) <- consLikingVars')
        r('rownames(cons.liking) <- consLikingObj')
        
        # Make row and column names for class function '.residualsTable',
        # since the R function provides only a long vector instad of an array
        # with row and column names.
        self.consLiking = consLiking
        
                
        print; print '----- 5 -----'; print

        # Construct a list in R space that holds data and names of liking matrices
        rCommand_buildLikingList = 'list.consum.liking <- list(matr.liking=list({0}), names.liking=c("{1}"))'.format('cons.liking', consLikingTag)
        print rCommand_buildLikingList
        r(rCommand_buildLikingList)
        
        
        print; print '----- 6 -----'; print
        
        # Construct R list with R lists of product design variables as well as
        # consumer attributes.        
        
        # Construct string holding design variables that is needed for 
        # construction of rCommand_fixedFactors
        for desInd, desVar in enumerate(selected_designVars):
            
            if desInd == 0:
                selDesVarStr = '"{0}"'.format(selected_designVars[desInd])
            
            else:
                newStrPart = '"{0}"'.format(selected_designVars[desInd])
                selDesVarStr = selDesVarStr + ',' + newStrPart
        
       
        # Construct string holding consumer attributes that is needed for 
        # construction of rCommand_fixedFactors
        for consInd, consAtt in enumerate(selected_consAtts):
            
            if consInd == 0:
                selConsAttStr = '"{0}"'.format(selected_consAtts[consInd])
            
            else:
                newStrPart = '"{0}"'.format(selected_consAtts[consInd])
                selConsAttStr = selConsAttStr + ',' + newStrPart
        
            
        rCommand_fixedFactors = 'fixed <- list(Product=c({0}), Consumer={1})'.format(selDesVarStr, selConsAttStr)
        print rCommand_fixedFactors
        r(rCommand_fixedFactors)
        print(r('fixed'))
        

        print; print '----- 7 -----'; print

        
        # Define which factors are random and construct R list with all
        # factors, both random and fixed. Define also response since the
        # name will be used in result tables.
        r['random'] = 'Consumer'
        r['response'] = consLikingTag
        
        facs = ['Consumer']
        facs.extend(selected_designVars)
        facs.extend(selected_consAtts)
        r['facs'] = facs
        
        print(r('random'))
        print(r('response'))
        print(r('facs'))
        
        print; print '----- 8 -----'; print
        
        rCommand_runAnalysis = 'res.gm <- conjoint(structure={0}, consum.attr=consum.attr, design.matr=design.matr, list.consum.liking=list.consum.liking, response, fixed, random, facs)'.format(structure)
        print rCommand_runAnalysis
        r(rCommand_runAnalysis)
        
        
        print; print '----- 9 -----'; print
        
        print(r('res.gm'))  
    
    
    def randomTable(self):
        """
        Returns random table from R conjoint function.
        """
        r('randTab <- res.gm[[1]][1]')
        
        randTableDict = {}
        randTableDict['data'] = r['randTab']['rand.table']
        randTableDict['colNames'] = r['colnames(res.gm$odourflavour$rand.table)']
        randTableDict['rowNames'] = r['rownames(res.gm$odourflavour$rand.table)']
        
        return randTableDict
    
    
    def anovaTable(self):
        """
        Returns ANOVA table from R conjoint function.
        """
        r('anovaTab <- res.gm[[1]][2]')
        
        anovaTableDict = {}
        anovaTableDict['data'] = r['anovaTab']['anova.table']
        anovaTableDict['colNames'] = r['colnames(res.gm$odourflavour$anova.table)']
        anovaTableDict['rowNames'] = r['rownames(res.gm$odourflavour$anova.table)']

        return anovaTableDict
        
        
    def lsmeansTable(self):
        """
        Returns LS means table from R conjoint function.
        """
        r('lsmeansTab <- res.gm[[1]][3]')
        
        lsmeansTableDict = {}
        lsmeansTableDict['data'] = r['lsmeansTab']['lsmeans.table']
        lsmeansTableDict['colNames'] = r['colnames(res.gm$odourflavour$lsmeans.table)']
        lsmeansTableDict['rowNames'] = r['rownames(res.gm$odourflavour$lsmeans.table)']
        
        return lsmeansTableDict
        
    
    def lsmeansDiffTable(self):
        """
        Returns table of differences between LS means from R conjoint function.
        """
        r('lsmeansDiffTab <- res.gm[[1]][4]')
        
        lsmeansDiffTableDict = {}
        lsmeansDiffTableDict['data'] = r['lsmeansDiffTab']['diffs.lsmeans.table']
        lsmeansDiffTableDict['colNames'] = r['colnames(res.gm$odourflavour$diffs.lsmeans.table)']
        lsmeansDiffTableDict['rowNames'] = r['rownames(res.gm$odourflavour$diffs.lsmeans.table)']
        
        return lsmeansDiffTableDict
        
        
    def residualsTable(self):
        """
        Returns residuals from R conjoint function.
        """
        # Get size of liking data array. 
        numRows, numCols = np.shape(self.consLiking.data)
        #print 'number of rows:', numRows
        #print 'number of cols:', numCols
        
        r('residTab <- res.gm[[1]][5]')
        
        residTableDict = {}
        residTableDict['data'] = np.reshape(r['residTab']['residuals'], \
                (numRows, numCols))
        
        residTableDict['rowNames'] = self.consLiking.objNames
        residTableDict['colNames'] = self.consLiking.varNames
        
        return residTableDict
