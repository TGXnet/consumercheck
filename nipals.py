"""
Created on Mon Nov 16 21:28:47 2009


@author: OTO


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
"""

# Import necessary modules
import numpy as np
import numpy.linalg as npla
import statTools as st


class PCA:
    """
    GENERAL INFO:
    -------------
    This class carries out Principal Component Analysis on arrays using
    NIPALS algorithm.
    
    EXAMPLE USE:
    ----
    analysis = nipals.PCA(array, numPC=5, mode=2)
    analysis = nipals.PCA(array)
    analysis = nipals.PCA(array, numPC=3)
    analysis = nipals.PCA(array, mode=1)
        
    TYPES:
    ------
    array: <array>
    numPC: <integer>
    mode: <integer> # Can take values 0 (raw data), 1 (column centred) or 
          2 (standardised data)
    """
    
    def __init__(self, inputArray, **kargs):
        """
        On initialisation check how inputArray is to be pre-processed (which
        mode is used). Then check whether number of PC's chosen by user is OK.
        Then run NIPALS algorithm.
        """
        
        # Check what is provided by user for PCA.
        # ---------------------------------------
        
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
        
        # Check whether mode is provided. If NOT, then inputArray is centred
        # by default.
        if 'mode' not in kargs.keys():
            self.mode = 1
        else:
            self.mode = kargs['mode']
        
        # Define inputArray within class. self.inputArray is later needed in
        # .getCorrLoadings()
        self.inputArray = inputArray
        
        
        # Pre-process data according to user request.
        # -------------------------------------------
        
        # Process inputArray according to selected mode.
        # No pre-processing of inputAray
        if self.mode == 0:
            self.data = inputArray.copy()
        
        # Mean centre inputArray
        elif self.mode == 1:
            self.data = st.centre(inputArray)
        
        # Standardise variables in inputArray
        elif self.mode == 2:
            self.data = st.STD(inputArray, 0)
            
        
        # Initiate Collections of computed results.
        # -----------------------------------------
        
        # Collect scores and loadings in lists that will be later converted
        # to arrays.
        scoresList = []
        loadingsList = []
        
        # Collect settings under which PCA was run.
        self.settings = {}
        self.settings['numPC'] = self.numPC
        self.settings['mode'] = self.mode
        self.settings['inputArray'] = inputArray
        self.settings['analysedArray'] = self.data
        
        # Collect residual matrices/arrays after each computed PC
        self.resids = {}
        
        # Collect predicted matrices/array Xhat after each computed PC
        self.predX = {}
        
        # Collect explained variance in each PC
        self.explainedVariances = {}
        totalVar = np.sum(np.square(self.data))
        
        
        # Here the NIPALS PCA algorithm starts
        # ------------------------------------
        threshold = 1.0e-8
        X_new = self.data.copy()
        
        # Compute number of principal components as specified by user 
        for j in range(self.numPC): 
            
            t = X_new[:,0].reshape(-1,1)
            
            # Iterate until score vector converges according to threshold
            while 1:
                nom = np.dot(np.transpose(X_new), t)
                denom = npla.norm(nom)
                
                p = nom / denom
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
            self.predX[j+1] = Xhat_j
            
            # Compute explained variance in each PC and store value in
            # corresponding dictionary.
            fracVar = np.sum(np.square(Xhat_j))
            self.explainedVariances[j+1] = fracVar / totalVar * 100
            
        # Collect scores and loadings for the actual PC.
        self.scores = np.hstack(scoresList)
        self.loadings = np.hstack(loadingsList)
        
        
    
    def getScores(self):
        """
        Returns the score matrix T. First column holds scores for PC1, 
        second column holds scores for PC2, etc.
        """
        return self.scores
        
    
    def getLoadings(self):
        """
        Returns the loading matrix P. First column holds loadings for PC1, 
        second column holds scores for PC2, etc.
        """
        return self.loadings
    
    
    def getCalExplVar(self):
        """
        Returns a dictionary holding the calibrated explained variance for 
        each PC. Key represents order of PC. 
        """
        return self.explainedVariances

    
    def getResidualsMatrices(self):
        """
        Returns a dictionary holding the residual matrices E after each 
        computed PC. Key represents order of PC.
        """
        return self.resids
    
    
    def getPredictedMatrices(self):
        """
        Returns a dictionary holding the predicted matrices Xhat after each 
        computed PC. Key represents order of PC.
        """
        return self.predX
    
    
    def getSettings(self):
        """
        Returns a dictionary holding the settings under which NIPALS PCA was
        run. Key represents order of PC.
        """
        return self.settings
    
    
    def getCorrLoadings(self):
        """
        Returns the loading matrix P. First column holds loadings for PC1, 
        second column holds scores for PC2, etc.
        """

        # Creates empty matrix for correlation loadings
        corrLoadings = np.zeros((np.shape(self.scores)[1], \
            np.shape(self.loadings)[0]), float)
        
        # Compute correlation loadings:
        # For each PC in score matrix
        for PC in range(np.shape(self.scores)[1]):
            PCscores = self.scores[:, PC]
            
            # For each variable/attribute in original matrix (not meancentered)
            for var in range(np.shape(self.inputArray)[1]):
                origVar = self.inputArray[:, var]
                corrs = np.corrcoef(PCscores, origVar)
                corrLoadings[PC, var] = corrs[0,1]
        
        self.corrLoadings = np.transpose(corrLoadings)
        
        return self.corrLoadings
    
    
    def getCorrLoadingsEllipses(self):
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

