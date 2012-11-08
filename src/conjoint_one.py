# -*- coding: utf-8 -*-
"""
Created on Apr 19 14:46:17 2012

@author: oliver.tomic

@purpose:
Wraps Alexandra's conjoint function and accesses it via pyper
"""

# Import necessary modules
import os.path
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
# r('dir<-"//ad.local/dfs/AAS-Users/oliver.tomic/Documents/Work/ConsumerCheck/ConjointConsumerCheck/ConjointClassNew"')
# r('dir<-"~/TGXnet/Prosjekter/2009-13-ConsumerCheck/Conjoint/ConjointConsumerCheck_27_04_2012"')
r_origo = os.path.dirname(os.path.abspath(__file__))
r('setwd("{0}")'.format(r_origo))
r('source("pgm/conjoint.r")')



class RConjoint:
    """
    A wrapper around Alexandra's conjoint function in R
    """
    
    def __init__(self, structure,
                 consAtts, selected_consAtts,
                 design, selected_designVars,
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

        self.structure = structure
        self.consAtts = consAtts
        self.selected_consAtts = selected_consAtts
        self.design = design
        self.selected_designVars = selected_designVars
        self.consLiking = consLiking
        self.consLikingTag = consLikingTag

        
        #print; print '----- 1 -----'; print
        
        print; print 'MODEL SETTINGS' 
        print '--------------'
        print 'Structure =', structure
        print 'Consumer attributes:', selected_consAtts
        print 'Design variables:', selected_designVars
        print 'Response:', consLikingTag
        
        #print; print '----- 2 -----'; print

        self._data_merge()
        # Oliver started to implement this
        # self._category_conversion()
        self._handle_missing_values()
        self._configure_conjoint()
        self._run_conjoint()



    def _data_merge(self):
        # Merge data from the following data arrays: consumer liking,
        # consumer attributes and design
        
        # Get content from design array
        desData = self.design.data
        desVarNames = self.design.varNames
        desObjNames = self.design.objNames
        
        # Get content form cosumer liking array
        consData = self.consLiking.data
        consVarNames = self.consLiking.varNames
        
        # Get content from consumer attributes array
        attrData = self.consAtts.data
        attrVarNames = self.consAtts.varNames
        
        # Make list with column names
        self.headerList = ['Consumer', self.consLikingTag]
        self.headerList.extend(desVarNames)
        self.headerList.extend(attrVarNames)


        # Now construct conjoint matrix
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
            attrList = attrData[consInd,:]
            for rowInd in range(consRows):
                attrBlockList.append(attrList)
            consList.append(np.vstack(attrBlockList))
            
            # Convert consumer specific entry to an array and collect in allConsList
            consArr = np.hstack(consList)
            allConsList.append(consArr)
        
        
        # Put all information into the final data array
        finalData = np.vstack(allConsList)
        self.finalData = finalData.copy()
        
        #print finalData

        #print; print '----- 3 -----'; print



    def _category_conversion(self):
        # The final data matrix needs to be numerical, when submitted to R via PypeR 
        # and should not be mixed with strings and numbers. Therefore the link between
        # the number representing a consumer ID, consumer attribute, design factor or
        # product name is stored here. 
        infoDict = {}
        infoDict['consumer ID'] = {}
        infoDict['consumer attributes'] = {}
        infoDict['product names'] = {}
        
        for ind, item in enumerate(consVarNames):
            infoDict['consumer ID'][item] = ind
        
        for ind, item in enumerate(desObjNames):
            infoDict['product names'][ind] = item
        
        self.infoLabelDict = infoDict



    def _handle_missing_values(self):

        # Now check if the array has missing values. If it has, then missing values 
        # need to replaced with some floats (1234.1234) before submission to R. 
        # PypeR does not handle missing values properly, which is why the 
        # missing values are replaced
        # with floats. The missing values are then re-inserted in R.
        fD_bool = np.isnan(self.finalData)
        
        # Make a copy of the original final data array that then will be submitted to
        # R. If it is without missing data it will be submitted as is. If missing 
        # values are present, then the copy of final data array will be modified. 
        finalData_copy = np.copy(self.finalData)
        
        if True in fD_bool:
            print 'There are missing values'
            
            # Generate an empty list that will hold positions of missing values. 
            nanPos = []
            
            # Loop through the construced array and detect where missing values are
            # positioned and replace missing value with a float in the copy of the
            # constructed matrix.
            for ind, item in np.ndenumerate(self.finalData):
                
                if np.isnan(item) == True:
                    nanPos.append([ind[0]+1, ind[1]+1])
                    finalData_copy[ind] = 1234.1234
            
            print nanPos
                
        else:
            print 'NO missing values'
        
        
        #print; print '----- 4 -----'; print
        
        # Transfer consumer attribute data from Python to R and build data 
        # frame in R space

        # TODO: new functionality
        
        # Transfer consumer attribute data from Python to R and build data 
        # frame in R space
        r['conjData'] = finalData_copy
        
        # Re-insert missing values if there were any
        if True in fD_bool:
            for pos in nanPos:
                print pos
                r('conjData[{0},{1}] <- NA'.format(pos[0],pos[1]))
        
        r['conjDataVarNames'] = self.headerList
        r('conjDF <- as.data.frame(conjData)')
        r('colnames(conjDF) <- conjDataVarNames')        
        

        # FIXME: Old non merge code
#        # Transfer data from Python to R and build data 
#        # frame in R space
#        r['dataMat'] = finalData
#        r['dataMat_colnames'] = headerList
#        r('finalDataFrame <- as.data.frame(dataMat)')
#        r('colnames(finalDataFrame) <- dataMat_colnames')
        
        #print(r('conjDF'))
        
#        # Transfer consumer attribute data from Python to R and build data 
#        # frame in R space
#        r['consAttMat'] = consAtts.data
#        r['consAttVars'] = consAtts.varNames
#        r['consAttObj'] = consAtts.objNames
#        r('consum.attr <- as.data.frame(consAttMat)')
#        r('colnames(consum.attr) <- consAttVars')
#        r('rownames(consum.attr) <- consAttObj')
#        #print(r('consum.attr'))
#        
#        print; print '----- 3 -----'; print
#        
#        r['designMat'] = design.data
#        r['designVars'] = design.varNames
#        r['designObj'] = design.objNames
#        r('design.matr <- as.data.frame(designMat)')
#        r('colnames(design.matr) <- designVars')
#        r('rownames(design.matr) <- designObj')
#        #print(r('design.matr'))
#        
#        #print; print '----- 4 -----'; print
#        
#        # Transfer odour/flavour liking data from Python to R and build data 
#        # frame in R space
#        r['consLikingMat'] = consLiking.data
#        r['consLikingVars'] = consLiking.varNames
#        r['consLikingObj'] = consLiking.objNames
#        r('cons.liking <- as.data.frame(consLikingMat)')
#        r('colnames(cons.liking) <- consLikingVars')
#        r('rownames(cons.liking) <- consLikingObj')
        
        # Make row and column names for class function '.residualsTable',
        # since the R function provides only a long vector instad of an array
        # with row and column names.
        


        #print; print '----- 5 -----'; print
        
#        # Construct a list in R space that holds data and names of liking matrices
#        rCommand_buildLikingList = 'list.consum.liking <- list(matr.liking=list({0}), names.liking=c("{1}"))'.format('cons.liking', consLikingTag)
#        print rCommand_buildLikingList
#        r(rCommand_buildLikingList)
        
        
        #print; print '----- 6 -----'; print
        
        # Construct R list with R lists of product design variables as well as
        # consumer attributes.


    def _configure_conjoint(self):
        # FIXME: New functionality
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
        
        if len(self.selected_consAtts) == 1:    
            rCommand_fixedFactors = 'fixed <- list(Product=c({0}), Consumer={1})'.format(selDesVarStr, selConsAttStr)
        else:
            rCommand_fixedFactors = 'fixed <- list(Product=c({0}), Consumer=c({1}))'.format(selDesVarStr, selConsAttStr)
        
        #print rCommand_fixedFactors
        r(rCommand_fixedFactors)
        #print(r('fixed')); print
        

        #print; print '----- 7 -----'; print

        
        # Define which factors are random and construct R list with all
        # factors, both random and fixed. Define also response since the
        # name will be used in result tables.
        r['random'] = 'Consumer'
        r['response'] = self.consLikingTag
        
        facs = ['Consumer']
        facs.extend(self.selected_designVars)
        facs.extend(self.selected_consAtts)
        r['facs'] = facs
        
        #print(r('random'))
        #print(r('response'))
        #print(r('facs'))
        
        #print; print '----- 8 -----'; print


    def _run_conjoint(self):
        rCommand_runAnalysis = 'res <- ConjointNoMerge(structure={0}, conjDF, response, fixed, random, facs)'.format(self.structure)


        #rCommand_runAnalysis = 'res.gm <- conjoint(structure={0}, consum.attr=consum.attr, design.matr=design.matr, list.consum.liking=list.consum.liking, response, fixed, random, facs)'.format(structure)
        #print rCommand_runAnalysis
        print(r(rCommand_runAnalysis))
        
        
        #print; print '----- 9 -----'; print
        
        #print(r('res'))
        print; print '-----   calculation finished   -----'        
    
    
    def randomTable(self):
        """
        Returns random table from R conjoint function.
        """
        r('randTab <- res[[1]][1]')
        
        randTableDict = {}
        randTableDict['data'] = r['randTab']['rand.table']
        randTableDict['colNames'] = r['colnames(res$odourflavour$rand.table)']
        randTableDict['rowNames'] = r['rownames(res$odourflavour$rand.table)']
        
        return randTableDict
    
    
    def anovaTable(self):
        """
        Returns ANOVA table from R conjoint function.
        """
        r('anovaTab <- res[[1]][2]')
        
        anovaTableDict = {}
        anovaTableDict['data'] = r['anovaTab']['anova.table']
        anovaTableDict['colNames'] = r['colnames(res$odourflavour$anova.table)']
        anovaTableDict['rowNames'] = r['rownames(res$odourflavour$anova.table)']

        return anovaTableDict
        
        
    def lsmeansTable(self):
        """
        Returns LS means table from R conjoint function.
        """
        r('lsmeansTab <- res[[1]][3]')
        
        lsmeansTableDict = {}
        lsmeansTableDict['data'] = r['lsmeansTab']['lsmeans.table']
        lsmeansTableDict['colNames'] = r['colnames(res$odourflavour$lsmeans.table)']
        lsmeansTableDict['rowNames'] = r['rownames(res$odourflavour$lsmeans.table)']
        
        return lsmeansTableDict
        
    
    def lsmeansDiffTable(self):
        """
        Returns table of differences between LS means from R conjoint function.
        """
        r('lsmeansDiffTab <- res[[1]][4]')
        
        lsmeansDiffTableDict = {}
        lsmeansDiffTableDict['data'] = r['lsmeansDiffTab']['diffs.lsmeans.table']
        lsmeansDiffTableDict['colNames'] = r['colnames(res$odourflavour$diffs.lsmeans.table)']
        lsmeansDiffTableDict['rowNames'] = r['rownames(res$odourflavour$diffs.lsmeans.table)']
        
        return lsmeansDiffTableDict
        
        
    def residualsTable(self):
        """
        Returns residuals from R conjoint function.
        """
        # Get size of liking data array. 
        numRows, numCols = np.shape(self.consLiking.data)
        #print 'number of rows:', numRows
        #print 'number of cols:', numCols
        
        r('residTab <- res[[1]][5]')
        
        residTableDict = {}
        residTableDict['data'] = np.reshape(r['residTab']['residuals'], \
                (numRows, numCols))
        
        residTableDict['rowNames'] = self.consLiking.objNames
        residTableDict['colNames'] = self.consLiking.varNames
        
        return residTableDict
        
        
    def infoDict(self):
        """
        Returns a dictionary holding information on lables for categories. 
        """
        return self.infoLabelDict
    
    
    def inputData(self):
        """
        Returns the final data array which is constructed from
        
        - consumer attributes array
        - consumer liking array
        - design array.
        
        This final data array is then submitted to R conjoint function.
        """
        return self.finalData
        
