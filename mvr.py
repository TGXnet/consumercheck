# -*- coding: utf-8 -*-
"""
Created on Sat Apr 03 15:38:48 2010
Modified on 2011-06-08 by TG

@author: OTO


@purpose: 
Run either PLS or PCR, using Bjørn-Helge Mevik's pls package which
is programmed in the R language. This is a limited Python wrapper of that 
package. The wrapper will be continuously extendend.


@version 01: 03.04.2010
This version returns:
    - scores T
    - Yloadings Q
    - Xloadings P
    - fitted Y, that is Yhat:

"""

# Import necessary modules to make analysis work.
import numpy as np
import statTools as st
import rpy2.robjects as ro
import rpy2.robjects.numpy2ri # necessary for array conversion from Python to R

# Import necessary R library and get function that will be used
ro.r('library(pls)')

# Temporary way to import updated libraries in R. Bjørn-Helge has made
# some modifications to R code and new packages have not been compiled by
# CRAN yet. uselspls.R imports the modified libraries.
# ro.r('source("C:/Work/LS-PLS/R-BHME/newRpacks/uselspls.R")')
# ro.r('source("~/R/uselspls.R")')


# Define partial least square (PLSR) method
def plsr(X, Y, centre, fncomp, fmethod, fvalidation):
    """
    INPUT:
    ------

    X: type <array> holding values for X

    Y: type <array> holding values of Y

    centre: type <string>; 
        choices:
            - "yes"
            -" no"
    
    fncomp: type <integer> representing number of components to be computed
    
    fmethod: type <string>; 
        choices: 
            - "oscorespls"
            - "simpls"
            - "svdpc"
            - "widekernelpls"
    
    fvalidation: type <string>; 
        choices:
            - "LOO"
            - "none"
            
    """
    # Check whether number of components to be computed provided by user is
    # possible to compute. If not, set to maximum possible number of components.
    # --------------------------------------------------------------------------
    maxCompList = []    
    
    # Determine variable dimension in X    
    numVarX = np.shape(X)[1]
    maxCompList.append(numVarX)    
    
    # Determine variable dimension in Y
    numVarY = np.shape(Y)[1]
    maxCompList.append(numVarY)
    
    # Determine object dimension in X and/or Y. Must be the same to be able
    # to run PLSR
    numObjXY = np.shape(X)[0]
    maxCompList.append(numObjXY - 2)
    
    # Now set to maximum possible number of components if user has provided
    # a too large number
    if fncomp > min(maxCompList):
        fncomp = min(maxCompList)
    
    # Centre input arrays if requested.
    # ---------------------------------
    if centre == 'yes':
        centX = st.centre(X.copy())
        centY = st.centre(Y.copy())
        r_X = ro.conversion.py2ri(centX)
        r_Y = ro.conversion.py2ri(centY)
    
    elif centre == 'no':
        r_X = ro.conversion.py2ri(X.copy())
        r_Y = ro.conversion.py2ri(Y.copy())
    
    # Access and link up to mvr method in R.
    mvr = ro.r['mvr']
    
    # Definition of the regression equation for mvr commando. 
    # Use .getenvironment to link R arrays to R formula.
    fmla = ro.Formula('Y ~ X')
    env = fmla.getenvironment()
    env['X'] = r_X
    env['Y'] = r_Y
    
    # Run PLSR with parameters
    fit = mvr(fmla, ncomp=fncomp, method=fmethod, validation=fvalidation)
    
    # Define global environment variable in Python. With globalEnv all matrices 
    # in R are accessible. This is needed for access of results stored in R 
    # global environment extracted from 'fit' model.
    # However, first 'fit' needs to be transfered from Python to R, such that
    # it can be used in R code strings.
    globalenv = ro.globalenv
    globalenv['fit'] = fit
    
    # Fetch results from model and convert R-objects to numpy arrays
    # Scores T.
    ro.r('T <- scores(fit)')
    T = np.array(globalenv['T'])
    
    # X-loadings P.
    ro.r('P <- loadings(fit)')
    P = np.array(globalenv['P'])
    
    # Y-loadings Q.
    ro.r('Q <- Yloadings(fit)')
    Q = np.array(globalenv['Q'])
    
    # Y-scores
    ro.r('Yscores <- fit$Yscores')
    Yscores = np.array(globalenv['Yscores'])
    
    # Just a little example of how to check which R-attributes an object has.
    ro.r('R_attrList <- names(fit)')
    r_attrList = np.array(globalenv['R_attrList'])
    
    # loading weights
    ro.r('loadingWeights <- fit$loading.weights')
    loadingWeights = np.array(globalenv['loadingWeights'])
    
    # Compute calibrated explained variance in X (each PC and cumulated)
    # -------------------------------------------------------------------    
    
    # Each PC
    ro.r('calExplVarX <- explvar(fit)')
    calExplVarX = np.array(globalenv['calExplVarX'])
    
    # Cumulated calibrated explained variance in X.
    cumCalExplVarX = list(np.cumsum(calExplVarX))
    cumCalExplVarX.insert(0,0)
    
    # Routine for extraction of predicted Y's, coefficients and residuals
    # after each computed PC.
    # -------------------------------------------------------------------
    ro.r('Yhat <- fitted.mvr(fit)')
    Yhat = np.array(globalenv['Yhat'])
    YhatsDict = {}
    
    ro.r('coeffs <- fit$coefficients')
    coeffs = np.array(globalenv['coeffs'])
    coeffsDict = {}
    
    ro.r('resids <- fit$residuals')
    resids = np.array(globalenv['resids'])
    residsDict = {}
    
    for comp in range(0, fncomp):
        namePC = 'PC' + str(comp + 1)
        YhatsDict[namePC] = Yhat[:,:,comp]
        coeffsDict[namePC] = coeffs[:,:,comp]
        residsDict[namePC] = resids[:,:,comp]
    
    # Compute calibrated explained variance in Y. (each PC and cumulated)
    # -------------------------------------------------------------------
    
    # Each PC
    calExplVarY = []
    for comp in range(0, fncomp):
        nom = np.trace(np.dot(np.transpose(centY - Yhat[:,:,comp]), \
            (centY - Yhat[:,:,comp])))
        denom = np.trace(np.dot(np.transpose(centY),centY))
        oneYexplVar = (1 - (nom / denom)) - np.sum(calExplVarY)
        calExplVarY.append(oneYexplVar)
    calExplVarY = np.array(calExplVarY) * 100
    
    # Cumulated calibrated explained variance in X
    cumCalExplVarY = list(np.cumsum(calExplVarY))
    cumCalExplVarY.insert(0,0)    
    
    # Routine to extract RMSEP from R results
    # ---------------------------------------
    ro.r('RMSEPval <- RMSEP(fit)[1]')
    RMSEPobj = globalenv['RMSEPval']
    CV_RMSEP = np.array(RMSEPobj[0])[0,:,:]
    adjCV_RMSEP = np.array(RMSEPobj[0])[1,:,:]
    
    model_CV_RMSEP = np.average(CV_RMSEP, axis=0)
    model_adjCV_RMSEP = np.average(adjCV_RMSEP, axis=0)
    
    # Routine to extract MSEP from R results
    # --------------------------------------
    ro.r('MSEPval <- MSEP(fit)[1]')
    MSEPobj = globalenv['MSEPval']
    CV_MSEP = np.array(MSEPobj[0])[0,:,:]
    adjCV_MSEP = np.array(MSEPobj[0])[1,:,:]
    
    model_CV_MSEP = np.average(CV_MSEP, axis=0)
    model_adjCV_MSEP = np.average(adjCV_MSEP, axis=0)
    
    # Compute validated explained variance in Y (each PC and cumulated)
    # -----------------------------------------------------------------
    
    # For each PC
    valExplVarY = []
    MSEPvalues = list(model_CV_MSEP[:])    
    firstMSEP = MSEPvalues[0]
    MSEPvalues.pop(0)
    
    for ind, item in enumerate(MSEPvalues):
        perc = (firstMSEP - item) / firstMSEP * 100
        valExplVarY.append(perc)
    
    #valExplVarY.insert(0,0)
        
    # Cumulated
    cumValExplVarY = list(np.cumsum(valExplVarY))
    cumValExplVarY.insert(0,0)
    
    # Compute correlation loadings of X.
    # ----------------------------------
    corrLoadX = np.zeros((np.shape(T)[1], np.shape(X)[1]), float)
    
    # Compute correlation loadings for each PC in score matrix
    for PC in range(np.shape(T)[1]):
        PCscores = T[:, PC]
        
        # For each variable/attribute in original matrix (not meancentered)
        for var in range(np.shape(X)[1]):
            origVar = X[:, var]
            corrs = np.corrcoef(PCscores, origVar)
            corrLoadX[PC, var] = corrs[0,1]
    
    # Compute correlation loadings of Y.
    # ----------------------------------
    corrLoadY = np.zeros((np.shape(T)[1], np.shape(Y)[1]), float)
    
    # Compute correlation loadings for each PC in score matrix
    for PC in range(np.shape(T)[1]):
        PCscores = T[:, PC]
        
        # For each variable/attribute in original matrix (not meancentered)
        for var in range(np.shape(Y)[1]):
            origVar = Y[:, var]
            corrs = np.corrcoef(PCscores, origVar)
            corrLoadY[PC, var] = corrs[0,1]

    # Return results in a Python dictionary.
    res = {}

    res['Scores T'] = T
    res['Yloadings Q'] = Q
    res['Xloadings P'] = P
    res['Yscores'] = Yscores
    
    res['corrLoadX'] = corrLoadX
    res['corrLoadY'] = corrLoadY
    
    res['pred Y'] = YhatsDict
    
    res['calExplVarX'] = calExplVarX
    res['calExplVarY'] = calExplVarY
    res['cumCalExplVarX'] = cumCalExplVarX
    res['cumCalExplVarY'] = cumCalExplVarY
    
    res['valExplVarY'] = valExplVarY
    res['cumValExplVarY'] = cumValExplVarY
    
    res['coeffs'] = coeffsDict
    res['loadingWeights'] = loadingWeights
    res['residuals'] = residsDict
    
    res['indVariable RMSEP'] = CV_RMSEP
    res['indVariable adj RMSEP'] = adjCV_RMSEP
    res['model RMSEP'] = model_CV_RMSEP
    res['model adj RMSEP'] = model_adjCV_RMSEP
    
    res['indVariable MSEP'] = CV_MSEP
    res['indVariable adj MSEP'] = adjCV_MSEP
    res['model MSEP'] = model_CV_MSEP
    res['model adj MSEP'] = model_adjCV_MSEP
    
    res['R_attr'] = r_attrList
    
    return res
