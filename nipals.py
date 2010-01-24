# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 21:28:47 2009

@author: OTO
"""

# Import necessary modules
import numpy as np
import numpy.linalg as npla
import statTools as st


class PCA:
    """
    GENERAL INFO:
    -------------
    This class carries out Principal Component Analysis on arrays based on
    NIPALS algorithm.
    
    USE:
    ----
    analysis = nipals.PCA(array, #PCs, 0) / PCA on raw data
    analysis = nipals.PCA(array, #PCs, 1) / mean centering data column-wise, 
        then PCA
    analysis = nipals.PCA(array, #PCs, 2) / standardising data column-wise, 
        then PCA
        
    TYPES:
    ------
    array: <array>
    numPC: <integer> # Can't be higher than number of rows or columns (whichever
        is higher of the two)
    mode: <integer> # Can take values 0, 1 or 2
    """
    
    def __init__(self, inputArray, numPC = 2, mode = 1):
        """
        On initialisation check how inputArray is to be pre-processed (which
        mode is used). Then check whether number of PC's chosen by user is OK.
        Then run NIPALS algorithm.
        """
        
        if mode == 0:
            self.data = inputArray.copy()
        
        elif mode == 1:
            self.data = st.centre(inputArray)
        
        elif mode == 2:
            self.data = st.STD(inputArray, 0)
            
        # Here the NIPALS PCA algorithm starts
        threshold = 1.0e-8
        X_new = self.data.copy()
        
        # Check whether number of PC's chosen by user is larger than highest
        # dimension of array. If true, then set numer of PC's to highest 
        # dimension of array.
        dims = np.shape(self.data)
        if numPC > max(dims):
            numPC = max(dims)
            
        scores = []
        loadings = []
        
        # Compute principal components for as specified by user 
        for j in range(numPC):
            
            t = X_new[:,0].reshape(-1,1)
            
            # Iterate until score vector converges
            while 1:
                nom = np.dot(np.transpose(X_new), t)
                denom = npla.norm(nom)
                
                p = nom / denom
                
                t_new = np.dot(X_new, p)
                
                diff = t - t_new
                t = t_new.copy()
                SS = np.sum(np.square(diff))

                if SS < threshold: 
                    scores.append(t)
                    loadings.append(p)
                    break
                
            X_old = X_new.copy()
            X_new = X_old - np.dot(t, np.transpose(p))        
        
        self.scores = np.hstack(scores)
        self.loadings = np.hstack(loadings)
        
    
    def getScores(self):
        """
        Returns the score matrix T. First column holds scores for PC1, 
        second column holds scores for PC2, etc.
        """
        print 'GET THE SCORES'
        return self.scores
        
    
    def getLoadings(self):
        """
        Returns the loading matrix P. First column holds loadings for PC1, 
        second column holds scores for PC2, etc.
        """
        return self.loadings
