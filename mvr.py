# -*- coding: utf-8 -*-

"""
Created on Sat Apr 03 15:38:48 2010

@author: OTO


@purpose:
Run either PLS or PCR, using Bjorn-Helge Mevik's pls package which
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
# necessary for array conversion from Python to R
import rpy2.robjects.numpy2ri


# Import necessary R library and get function that will be used
# http://cran.r-project.org/web/packages/pls/index.html
# http://mevik.net/work/software/pls.html
ro.r('library(pls)')

# Temporary way to import updated libraries in R. Bjorn-Helge has made
# some modifications to R code and new packages have not been compiled by
# CRAN yet. uselspls.R imports the modified libraries.
#ro.r('source("C:/Work/LS-PLS/R-BHME/newRpacks/uselspls.R")')



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


    # Centre input arrays if requested.
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
    fmla = ro.RFormula('Y ~ X')
    env = fmla.getenvironment()
    env['X'] = r_X
    env['Y'] = r_Y


    # Run PLSR with parameters
    fit = mvr(fmla, ncomp=4, method=fmethod, validation=fvalidation)


    # Define global environment variable in Python. With globalEnv all matrices
    # in R are accessible. This is needed for access of results stored in R
    # global environment extracted from 'fit' model.
    # However, first 'fit' needs to be transfered from Python to R, such that
    # it can be used in R code strings.
    globalEnv = ro.globalEnv
    globalEnv['fit'] = fit

    # Fetch results from model and convert R-objects to numpy arrays
    # Scores T.
    ro.r('T <- scores(fit)')
    T = np.array(globalEnv['T'])

    # X-loadings P.
    ro.r('P <- loadings(fit)')
    P = np.array(globalEnv['P'])

    # Y-loadings Q.
    ro.r('Q <- Yloadings(fit)')
    Q = np.array(globalEnv['Q'])

    # Explained variance in X.
    ro.r('XexplVar <- explvar(fit)')
    XexplVar = np.array(globalEnv['XexplVar'])

    # Routine for extract predicted Y's.
    ro.r('Yhat <- fitted.mvr(fit)')
    Yhat = np.array(globalEnv['Yhat'])
    YhatsDict = {}
    for comp in range(0, fncomp):
       namePC = 'PC' + str(comp + 1)
       YhatsDict[namePC] = Yhat[:,:,comp]

    # Routine to extract explained variance in Y.
    YexplVar = []
    for comp in range(0, fncomp):
        nom = np.trace(np.dot(np.transpose(centY - Yhat[:,:,comp]), \
            (centY - Yhat[:,:,comp])))
        denom = np.trace(np.dot(np.transpose(centY),centY))
        oneYexplVar = (1 - (nom / denom)) - np.sum(YexplVar)
        YexplVar.append(oneYexplVar)
    YexplVar = np.array(YexplVar) * 100


    # Return results in a Python dictionary.
    res = {}

    res['Scores T'] = T
    res['Yloadings Q'] = Q
    res['Xloadings P'] = P

    res['XexplVar'] = XexplVar
    res['YexplVar'] = YexplVar
    res['pred Y'] = YhatsDict

    return res
