# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 13:10:44 2011

@author: Oliver Tomic (OTO), <oliver.tomic@nofima.no>


@update 01: 09.06.2010 (OTO)
============================
- Implemented multiple key word agruments for PCA class (PCA can be run without
   providing some of parameters)

- new functions in PCA:
    > getCalExplainedVariance
    > getResidualsMatrices
    > getPredictedMatrices
    > getSettings


@update 02: 22.06.2010 (OTO)
============================
- new functions in PCA:
    > getCorrLoadings
    > getCorrLoadingsEllipses


@update 03: 30.06.2011 (OTO)
============================
- Attribute names were changed, removing "get"

- renamed module name from nipals.py to pca.py, which does not restrict
  implementation of other PCA algorithms (as for example kernel PCA, etc) at
  a later time

- the NIPALS based PCA class is now renamed to "nipalsPCA" from "PCA"

- removed attribute "calExplVar" and created instead:
    > .calExplVar_dict
    > .calExplVar_list
    > .cumCalExplVar_dict
    > .cumCalExplVar_list


@update 04: 12.07.2011 (OTO)
============================
- implemented cross validation and the following new class attributes:
    > .SEP
    > .MSEP
    > .RMSEP
    > .cumValExplVar_list
    > .cvTestAndTrainData


@update 05: 22.03.2012 (OTO)
============================
- rewrote large chunks of cross validation (total validated expl var was wrong)

- new functions:
    > .valExplVar_dict
    > .valExplVar_list
    > .cumValExplVar_dict
    > .cumValExplVar_list
    > .indVarCumCalExplVar_arr
    > .indVarCumValExplVar_arr
    > .MSEE_total
    > .MSEE_indVar
    > .MSECV_total
    > .MSECV_indVar


@update 06: 21.04.2012 (OTO)
============================
- removed mode 'raw' and all code regarding it.


@update 07: 31.07.2012 (OTO)
============================
Code cleaup and renaming of class functions to correspond more with PLSR
classes.
"""

# Import necessary modules
import numpy as np
import numpy.linalg as npla
import statTools as st
import cross_val as cv



class nipalsPCA:
    """
    GENERAL INFO:
    -------------
    This class carries out Principal Component Analysis on arrays using
    NIPALS algorithm.
    
    
    EXAMPLE USE:
    ----
    import pca
    
    model = pca.nipalsPCA(array, numPC=5, mode="cent")
    model = pca.nipalsPCA(array)
    model = pca.nipalsPCA(array, numPC=3)
    model = pca.nipalsPCA(array, mode="stand")
    model = pca.nipalsPCA(array, cvType=["loo"])
    model = pca.nipalsPCA(array, cvType=["lpo", 4])
    model = pca.nipalsPCA(array, cvType=["lolo", [1,2,3,2,3,1]])
    
    
    TYPES:
    ------
    array: <array>
    numPC: <integer>
    mode: <boolean>
                False: first column centre input data then run PCA
                True: first scale columns of input data to equal variance
                         then run PCA
    cvType: <list>
                loo: <string> leave one out (full cross validation)
                cvType = ["loo"]

                lpo: leave p out
                cvType = ["lpo", size]
                    size: <scalar> number of objects in each segment
                
                lolo: leave one label out
                cvType = ["lolo", labels]
                    labels: <list>  Assign a label to each object. One label is 
                           kept out at a time.
    """
    
    def __init__(self, inputArray, **kargs):
        """
        On initialisation check how inputArray is to be pre-processed (stand is
        True or False). Then check whether number of PC's chosen by user is OK.
        Then run NIPALS algorithm.
        """
#===============================================================================
#         Check what is provided by user for PCA
#===============================================================================
        
        # Check whether number of PC's that are to be computed is provided.
        # If NOT, then number of PC's is set to either number of objects or
        # variables of inputArray, whichever is smaller (maxPC). If number of
        # PC's IS provided, then number is checked against maxPC and set to
        # maxPC if provided number is larger.
        if 'numPC' not in kargs.keys():
            self.numPC = min(np.shape(inputArray))
        else:
            if kargs['numPC'] > min(np.shape(inputArray)):
                self.numPC = min(np.shape(inputArray))
            else:
                self.numPC = kargs['numPC']
        
        
        # Check whether information on pre-processing is required. If NOT,
        # then inputArray is centred by default.
        if 'stand' not in kargs.keys():
            self.stand = False
        else:
            self.stand = kargs['stand']
        
        # Define inputArray within class. self.inputArray is later needed in
        # .getCorrLoadings()
        self.inputArray = inputArray
        
        
        # Check whether cvType is provided. If NOT, then drop cross validation.
        if 'cvType' not in kargs.keys():
            self.cvType = None
        else:
            self.cvType = kargs['cvType']
        
        
        # Pre-process data according to user request.
        # -------------------------------------------
        
        # Process inputArray according to request.
        # Mean centre inputArray
        if self.stand == False:
            self.dataMean = np.average(inputArray, axis=0)
            self.data = inputArray.copy() - self.dataMean
            #self.data = st.centre(inputArray)
        
        # Standardise variables in inputArray
        elif self.stand == True:
            self.dataMean = np.average(inputArray, axis=0)
            self.dataStd = np.std(inputArray, axis=0, ddof=1)
            self.data = (inputArray.copy() - self.dataMean) / self.dataStd
            #self.data = st.STD(inputArray, 0)
            
        
        # Initiate Collections of computed results.
        # -----------------------------------------
        
        # Collect scores and loadings in lists that will be later converted
        # to arrays.
        scoresList = []
        loadingsList = []
        
        
        # Collect residual matrices/arrays after each computed PC
        self.resids = {}
        
        # Collect predicted matrices/array Xhat after each computed PC
        self.calXhatDict_singPC = {}
        
        # Collect explained variance in each PC
        self.calExplainedVariancesDict = {}
        self.calExplainedVariancesList = []
        totalVar = np.sum(np.square(self.data))

        
#===============================================================================
#        Here the NIPALS PCA algorithm starts
#===============================================================================
        threshold = 1.0e-8
        X_new = self.data.copy()
        
        # Compute number of principal components as specified by user
        for j in range(self.numPC):
            
            t = X_new[:,0].reshape(-1,1)
            
            # Iterate until score vector converges according to threshold
            while 1:
                num = np.dot(np.transpose(X_new), t)
                denom = npla.norm(num)
                
                p = num / denom
                t_new = np.dot(X_new, p)
                
                diff = t - t_new
                t = t_new.copy()
                SS = np.sum(np.square(diff))
                
                # Check whether sum of squares is smaller than threshold. Break
                # out of loop if true and start computation of next PC.
                if SS < threshold:
                    scoresList.append(t)
                    loadingsList.append(p)
                    break
            
            # Peel off information explained by actual PC and continue with
            # decomposition on the residuals (X_new = E).
            X_old = X_new.copy()
            Xhat_j = np.dot(t, np.transpose(p))
            X_new = X_old - Xhat_j
            
            # Store residuals E and Xhat in their dictionaries
            self.resids[j+1] = X_new
            self.calXhatDict_singPC[j+1] = Xhat_j
            
            if self.stand == True:
                self.calXhatDict_singPC[j+1] = (Xhat_j * self.dataStd) + \
                        self.dataMean
            
            else:
                self.calXhatDict_singPC[j+1] = Xhat_j + self.dataMean
            
            # Compute calibrated explained variance in each PC and store value 
            # in corresponding dictionary.
            fracVar = np.sum(np.square(Xhat_j))
            self.calExplainedVariancesDict[j+1] = fracVar / totalVar * 100
            self.calExplainedVariancesList.append(fracVar / totalVar * 100)
            
        # Collect scores and loadings for the actual PC.
        self.arr_scores = np.hstack(scoresList)
        self.arr_loadings = np.hstack(loadingsList)
        
#==============================================================================
#         From here computation of CALIBRATED explained variance starts
#==============================================================================
        
        # Collect calibrated predicted X in dictionaries.
        self.calPredXdict = {}
        
        # First compute Xhat after each component
        for comp in range(self.numPC):
            part_calT = self.arr_scores[:,0:comp+1]
            part_calP = self.arr_loadings[:,0:comp+1]
            calPredX_proc = np.dot(part_calT, np.transpose(part_calP))
            
            # Depending on preprocessing re-process in same manner
            # in order to get values that compare to original values.
            if self.stand == True:
                calXhat = (calPredX_proc * self.dataStd) + \
                        self.dataMean
            else:
                calXhat = calPredX_proc + self.dataMean
            
            self.calPredXdict[comp+1] = calXhat
        
        # First acces calibrated Xhat
        self.calPredXarrList = self.calPredXdict.values()
       
        # First get centered X which is needed for further computations
        X_cent = self.inputArray - np.average(self.inputArray, axis=0)
        
        # Compute first MSESC for each individual variable
        firstIndVarMSEE = np.sum(np.square(X_cent), axis=0).reshape(1,-1)
        zeroExplVar = np.zeros(np.shape(firstIndVarMSEE))
        self.indVarXcumCalExplVarList = [zeroExplVar]
        self.indVarMSEEList = [firstIndVarMSEE]
        
        # Compute MSEE for each variable
        for Xhat in self.calPredXarrList:
            diffX = X_cent - st.centre(Xhat)
            indVarMSEE = np.sum(np.square(diffX), axis=0)
            self.indVarMSEEList.append(indVarMSEE)
            self.indVarXcumCalExplVarList.append((firstIndVarMSEE - \
                    indVarMSEE) / firstIndVarMSEE * 100)
        
        self.indVarXcalExplVarArr = np.vstack(self.indVarXcumCalExplVarList)
        self.indVarMSEEarr = np.vstack(self.indVarMSEEList)
        
        # Compute MSEE for all variables together
        self.XcumCalExplVarList = [0]
        self.XcumCalExplVarDict = {}
        self.XcumCalExplVarDict[0] = 0
        self.MSEE_total = np.average(self.indVarMSEEarr, axis=1)
        firstMSEE = self.MSEE_total[0]
        for value in range(1, len(self.MSEE_total)):
            calPerc = (firstMSEE - self.MSEE_total[value]) / firstMSEE * 100
            self.XcumCalExplVarList.append(calPerc)
            self.XcumCalExplVarDict[value] = calPerc
        
        
        # Compute RMSEE for individual variables and for all together
        self.indVarRMSEEarr = np.sqrt(self.indVarMSEEarr)
        self.RMSEE_total = np.sqrt(self.MSEE_total)
        
#==============================================================================
#         From here cross validation procedure starts
#==============================================================================
        if self.cvType == None:
            pass
        else:
            numObj = np.shape(self.data)[0]
            
            if self.cvType[0] == "loo":
                print "loo"
                cvComb = cv.LeaveOneOut(numObj)
            elif self.cvType[0] == "lpo":
                print "lpo"
                cvComb = cv.LeavePOut(numObj, self.cvType[1])
            elif self.cvType[0] == "lolo":
                print "lolo"
                cvComb = cv.LeaveOneLabelOut(self.cvType[1])
            else:
                print('Requested form of cross validation is not available')
            
            
            # Collect validated predicted X for test data in dictionaries.
            # Later, when cross validation is finished they are all collected
            # in an array.
            self.valPredXdict = {}
            for pc in range(1, self.numPC+1):
                self.valPredXdict[pc] = []
            
            # Collect scores and loadings from each cross validation step
            self.valTlist = []
            self.valPlist = []

            # Collect train and test set in a dictionary for each PC
            self.cvTrainAndTestDataList = []
            self.X_train_means_list = []
            
            # First devide into combinations of training and test sets
            for train_index, test_index in cvComb:
                x_train, x_test = cv.split(train_index, test_index, inputArray)
                
                subDict = {}
                subDict['train'] = x_train
                subDict['test'] = x_test
                self.cvTrainAndTestDataList.append(subDict)
                
                # -------------------------------------------------------------                    
                # Center or standardise X according to users choice
                if self.stand == True:
                    X_train_mean = np.average(x_train, axis=0).reshape(1,-1)
                    X_train_std = np.std(x_train, axis=0, ddof=1).reshape(1,-1)
                    X_train_proc = (x_train - X_train_mean) / X_train_std
                    
                    # Standardise X test using mean and STD from training set
                    X_test_proc = (x_test - X_train_mean) / X_train_std
                
                else:
                    X_train_mean = np.average(x_train, axis=0).reshape(1,-1)
                    X_train_proc = x_train - X_train_mean
                    
                    # Center X test using mean from training set
                    X_test_proc = x_test - X_train_mean
                # -------------------------------------------------------------
                self.X_train_means_list.append(X_train_mean)
                
        
                # Here the NIPALS PCA algorithm starts
                # ------------------------------------
                threshold = 1.0e-8
                X_new = X_train_proc.copy()
                
                # Collect scores and loadings in lists that will be later converted
                # to arrays.
                scoresList = []
                loadingsList = []
                
                # Compute number of principal components as specified by user
                for j in range(self.numPC):
                    
                    t = X_new[:,0].reshape(-1,1)
                    
                    # Iterate until score vector converges according to threshold
                    while 1:
                        num = np.dot(np.transpose(X_new), t)
                        denom = npla.norm(num)
                        
                        p = num / denom
                        t_new = np.dot(X_new, p)
                        
                        diff = t - t_new
                        t = t_new.copy()
                        SS = np.sum(np.square(diff))
                        
                        # Check whether sum of squares is smaller than threshold. Break
                        # out of loop if true and start computation of next PC.
                        if SS < threshold:
                            scoresList.append(t)
                            loadingsList.append(p)
                            break
                    
                    # Peel off information explained by actual PC and continue with
                    # decomposition on the residuals (X_new = E).
                    X_old = X_new.copy()
                    Xhat_j = np.dot(t, np.transpose(p))
                    X_new = X_old - Xhat_j
                
                # Collect scores and loadings for the actual PC.
                valT = np.hstack(scoresList)
                valP = np.hstack(loadingsList)
                
                self.valTlist.append(valT)
                self.valPlist.append(valP)
                
                # Compute the scores for the left out object
                projT = np.dot(X_test_proc, valP)
                dims = np.shape(projT)[1]
                
                # Construct validated predicted X first for one component,
                # then two, three, etc
                for ind in range(0, dims):
                    
                    part_projT = projT[:,0:ind+1].reshape(1,-1)
                    part_valP = valP[:,0:ind+1]
                    valPredX_proc = np.dot(part_projT, np.transpose(part_valP))
                    
                    # Depending on preprocessing re-process in same manner
                    # in order to get values that compare to original values.
                    if self.stand == True:
                        valPredX = (valPredX_proc * X_train_std) + \
                                X_train_mean
                    else:
                        valPredX = valPredX_proc + X_train_mean
                    
                    self.valPredXdict[ind+1].append(valPredX)
                
            
            # Convert list of one-row arrays into one array such that it
            # corresponds to the orignial variable
            for ind in range(1, dims+1):
                self.valPredXdict[ind] = np.vstack(self.valPredXdict[ind])

            # Put all predicitons into an array that corresponds to the
            # original variable
            self.valPredXarrList = []
            valPreds = self.valPredXdict.values()
            for preds in valPreds:
                pc_arr = np.vstack(preds)
                self.valPredXarrList.append(pc_arr)
            

#==============================================================================
# From here VALIDATED explained variance is computed
#==============================================================================
            
            # First get centered X which is needed for further computations
            X_cent = self.inputArray - np.average(self.inputArray, axis=0)
            
            # Compute first MSESC for each individual variable
            firstIndVarMSECV = np.sum(np.square(X_cent), axis=0).reshape(1,-1)
            zeroExplVar = np.zeros(np.shape(firstIndVarMSECV))
            self.indVarXcumValExplVarList = [zeroExplVar]
            self.indVarMSECVList = [firstIndVarMSECV]
            
            # Compute MSECV for each variable
            for Xhat in self.valPredXarrList:
                diffX = X_cent - st.centre(Xhat)
                indVarMSECV = np.sum(np.square(diffX), axis=0).reshape(1,-1)
                self.indVarMSECVList.append(indVarMSECV)
                self.indVarXcumValExplVarList.append((firstIndVarMSECV - \
                        indVarMSECV) / firstIndVarMSECV * 100)
            
            self.indVarXvalExplVarArr = np.vstack(self.indVarXcumValExplVarList)
            self.indVarMSECVarr = np.vstack(self.indVarMSECVList)
            
            # Compute MSECV for all variables together
            self.XcumValExplVarList = [0]
            self.XcumValExplVarDict = {}
            self.XcumValExplVarDict[0] = 0
            self.MSECV_total = np.average(self.indVarMSECVarr, axis=1)
            firstMSECV = self.MSECV_total[0]
            for value in range(1, len(self.MSECV_total)):
                valPerc = (firstMSECV - self.MSECV_total[value]) / firstMSECV * 100
                self.XcumValExplVarList.append(valPerc)
                self.XcumValExplVarDict[value] = valPerc
            
            self.valExplVarArr = np.vstack(self.XcumValExplVarList)
            
            # Compute RMSEE for individual variables and for all together
            self.indVarRMSECVarr = np.sqrt(self.indVarMSECVarr)
            self.RMSECV_total = np.sqrt(self.MSECV_total)
            
    
    def means(self):
        """
        Returns the score matrix T. First column holds scores for PC1,
        second column holds scores for PC2, etc.
        """
        return self.dataMean.reshape(1,-1)
        
    
    def scores(self):
        """
        Returns the score matrix T. First column holds scores for PC1,
        second column holds scores for PC2, etc.
        """
        return self.arr_scores
        
    
    def loadings(self):
        """
        Returns the loading matrix P. First column holds loadings for PC1,
        second column holds scores for PC2, etc.
        """
        return self.arr_loadings
    
    
    def corrLoadings(self):
        """
        Returns correlation loadings. First column holds correlation loadings
        for PC1, second column holds scores for PC2, etc.
        """

        # Creates empty matrix for correlation loadings
        arr_corrLoadings = np.zeros((np.shape(self.arr_scores)[1], \
            np.shape(self.arr_loadings)[0]), float)
        
        # Compute correlation loadings:
        # For each PC in score matrix
        for PC in range(np.shape(self.arr_scores)[1]):
            PCscores = self.arr_scores[:, PC]
            
            # For each variable/attribute in original matrix (not meancentered)
            for var in range(np.shape(self.inputArray)[1]):
                origVar = self.inputArray[:, var]
                corrs = np.corrcoef(PCscores, origVar)
                arr_corrLoadings[PC, var] = corrs[0,1]
        
        self.arr_corrLoadings = np.transpose(arr_corrLoadings)
        
        return self.arr_corrLoadings
    
    
    
    def modelSettings(self):
        """
        Returns a dictionary holding the settings under which NIPALS PCA was
        run. Dictionary key represents order of PC.
        """
        # Collect settings under which PCA was run.
        self.settings = {}
        self.settings['numPC'] = self.numPC
        self.settings['stand'] = self.stand
        self.settings['inputArray'] = self.inputArray
        self.settings['analysedArray'] = self.data
        
        return self.settings
    
    
    def residuals(self):
        """
        Returns a dictionary holding the residual matrices E after each
        computed PC. Dictionary key represents order of PC.
        """
        return self.resids
    
    
    def calExplVar(self):
        """
        Returns a list holding the calibrated explained variance for
        each PC. 
        """
        return self.calExplainedVariancesList
    
    
    def cumCalExplVar_indVar(self):
        """
        Returns an array holding the cumulative calibrated explained variance
        for each variable in X after each PC.
        """
        return self.indVarXcalExplVarArr
    
    
    def cumCalExplVar(self):
        """
        Returns a list holding the cumulative calibrated explained variance for
        each PC. Dictionary key represents order of PC.
        """
        return self.XcumCalExplVarList
    
    
    def calPredX(self):
        """
        Returns a dictionary holding the predicted matrices Xhat from
        calibration after each computed PC. Dictionary key represents order
        of PC.
        """
        return self.calPredXdict
    
    
    def MSEE_indVar(self):
        """
        Returns a dictionary holding MSEE from cross validation after each
        computed PC for each variable. Dictionary key represents order of PC.
        """
        return self.indVarMSEEarr
    
    
    def MSEE(self):
        """
        Returns a dictionary holding MSEE from cross validation after each
        computed PC. Dictionary key represents order of PC
        """
        return self.MSEE_total
    
    
    def RMSEE_indVar(self):
        """
        Returns a dictionary holding RMSEE from cross validation after each
        computed PC for each variable. Dictionary key represents order of PC.
        """
        return self.indVarRMSEEarr
    
    
    def RMSEE(self):
        """
        Returns a dictionary holding RMSEE from cross validation after each
        computed PC. Dictionary key represents order of PC
        """
        return self.RMSEE_total
    

    def valExplVar(self):
        """
        Returns a list holding the validated explained variance for
        each PC.
        """
        l = self.XcumValExplVarList
        
        return [b-a for a,b in zip(l,l[1:])]
    
    
    def cumValExplVar_indVar(self):
        """
        Returns an array holding the cumulative validated explained variance
        for each variable in X after each PC.
        """
        return self.indVarXvalExplVarArr

    
    def cumValExplVar(self):
        """
        Returns a list holding the cumulative validated explained variance for
        each PC.
        """
        return self.XcumValExplVarList
    
    
    def valPredX(self):
        """
        Returns a dictionary holding the validated matrices Xhat from
        calibration after each computed PC. Dictionary key represents order
        of PC.
        """
        return self.valPredXdict
    
    
    def MSECV_indVar(self):
        """
        Returns a dictionary holding MSECV from cross validation after each
        computed PC for each variable. Dictionary key represents order of PC.
        """
        return self.indVarMSECVarr
        
    
    def MSECV(self):
        """
        Returns a dictionary holding MSECV from cross validation after each
        computed PC. Dictionary key represents order of PC
        """
        return self.MSECV_total
    
    
    def RMSECV_indVar(self):
        """
        Returns a dictionary holding RMSEE from cross validation after each
        computed PC for each variable. Dictionary key represents order of PC.
        """
        return self.indVarRMSECVarr
    
    
    def RMSECV(self):
        """
        Returns a dictionary holding RMSEE from cross validation after each
        computed PC. Dictionary key represents order of PC
        """
        return self.RMSECV_total
    
    
    def cvTrainAndTestData(self):
        """
        Returns a list consisting of dictionaries holding training and test sets.
        """
        return self.cvTrainAndTestDataList
    
    
    def corrLoadingsEllipses(self):
        """
        Returns the ellipses that represent 50% and 100% expl. variance in
        correlation loadings plot.
        """
        
        # Create range for ellipses
        t = np.arange(0.0, 2*np.pi, 0.01)
        
        # Compuing the outer circle (100 % expl. variance)
        xcords100perc = np.cos(t)
        ycords100perc = np.sin(t)
        
        # Computing inner circle
        xcords50perc = 0.707 * np.cos(t)
        ycords50perc = 0.707 * np.sin(t)
        
        # Collect ellipse coordinates in dictionary
        ellipses = {}
        ellipses['x50perc'] = xcords50perc
        ellipses['y50perc'] = ycords50perc
        
        ellipses['x100perc'] = xcords100perc
        ellipses['y100perc'] = ycords100perc
        
        return ellipses



if __name__ == '__main__':
    # Things to fix for testing
    from tests.conftest import make_ds_mock
    ds = make_ds_mock()
    with np.errstate(invalid='ignore'):
        res = nipalsPCA(ds.matrix, numPC=4, mode='stand', cvType=["loo"])
