# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 11:02:42 2011

@author: Oliver Tomic (OTO), <oliver.tomic@nofima.no>

@info:
Implemented PLSR (PLS1 and PLS2) in Python according to description in:
"Module 7: Partial Least Squares Regression I"
"Module 8: Partial Least Squares Regression II" 
by Bent Jørgensen and Yuri Goegebeur

http://statmaster.sdu.dk/courses/ST02/


@update 01: 14.07.2011 (OTO)
============================
added the following class attributes for PLS2:
    - .Xscores
    - .Xloadings
    - .Yscores
    - .Yloadings
    - .XcorrLoadings
    - .YcorrLoadings
    - .corrLoadingsEllipses
    - .Xresiduals
    - .Yresiduals
    - .Xmeans
    - .Ymeans
    - .Yfitted

@update 02: 26.10.2011 (OTO)
============================
Just finished a major upgrade with many new attributes for both PLS1 and PLS2.
This upgrade has happened over several weeks.

PLS1 has now the following attributes:
    - .results
    - .modelSettings
    - .Xscores
    - .Xloadings
    - .Yscores
    - .Yloadings
    - .XloadingsWeights
    - .XcorrLoadings
    - .YcorrLoadings
    - .Yresiduals
    - .Xresiduals
    - .Xmeans
    - .Ymeans
    - .XpredCal
    - .YpredCal
    - .YcalExplVar_tot_list
    - .YcumCalExplVar_tot_list
    - .XcalExplVar_tot_list
    - .XcumCalExplVar_tot_list
    - .PRESSE_tot_list
    - .PRESSE_tot_dict
    - .MSEE_tot_list
    - .MSEE_tot_dict
    - .RMSEE_tot_list
    - .RMSEE_tot_dict
    - .corrLoadingsEllipses
    - .cvTrainAndTestData
    - .YpredVal
    - .YcumValExplVar_tot_list
    - .YvalExplVar_tot_list
    - .PRESSCV_tot_list
    - .PRESSCV_tot_dict
    - .MSECV_tot_list
    - .MSECV_tot_dict
    - .RMSECV_tot_list
    - .RMSECV_tot_dict
    
PLS2 has now the following attributes:
    - .results
    - .modelSettings
    - .Xscores
    - .Xloadings
    - .Yscores
    - .Yloadings
    - .XloadingsWeights
    - .XcorrLoadings
    - .YcorrLoadings
    - .Yresiduals
    - .Xresiduals
    - .Xmeans
    - .Ymeans
    - .XpredCal
    - .YpredCal
    - .YcalExplVar_tot_list
    - .YcumCalExplVar_tot_list
    - .XcalExplVar_tot_list
    - .XcumCalExplVar_tot_list
    - .PRESSE_tot_list
    - .PRESSE_tot_dict
    - .MSEE_tot_list
    - .MSEE_tot_dict
    - .RMSEE_tot_list
    - .RMSEE_tot_dict
    - .corrLoadingsEllipses
    - .cvTrainAndTestData
    - .YpredVal
    - .YcumValExplVar_tot_list
    - .YvalExplVar_tot_list
    - .PRESSCV_tot_list
    - .PRESSCV_tot_dict
    - .MSECV_tot_list
    - .MSECV_tot_dict
    - .RMSECV_tot_list
    - .RMSECV_tot_dict
    - .YcumCalExplVar_indVar_arr
    - .YcumCalExplVar_indVar_dict
    - .YcumValExplVar_indVar_arr
    - .YcumValExplVar_indVar_dict
    - .PRESSE_indVar_arr
    - .PRESSE_indVar_dict
    - .MSEE_indVar_arr
    - .MSEE_indVar_dict
    - .RMSEE_indVar_arr
    - .RMSEE_indVar_dict
    - .PRESSCV_indVar_arr
    - .PRESSCV_indVar_dict
    - .MSECV_indVar_arr
    - .MSECV_indVar_dict
    - .RMSECV_indVar_arr
    - .RMSECV_indVar_dict


@update 03: 29.10.2011 (OTO)
============================
Changed maximum number of components allowed in PLS2. In "update 02" dimensions 
of both X and Y were used were used to determine maximum number of components. 
Now only X is used to determine maximum number of components. This needed to be
fixed because a Y with only 2 variables would allow only 2 components. 
"""

# Import necessary modules
import numpy as np
import statTools as st
import numpy.linalg as npla
import cross_val as cv



class nipalsPLS1:
    """
    GENERAL INFO
    ------------
    This class carries out Partial Least Squares Regression (PLS1) between a 
    data matrix X and a vector y.
    """
    
    def __init__(self, arrX, vecy, **kargs):
        """
        On initialisation check how X and y are to be pre-processed (which
        mode is used). Then check whether number of PC's chosen by user is OK.
        Then run NIPALS PLS1 algorithm.
        """
#===============================================================================
#         Check what is provided by user for PLS1
#===============================================================================
        
        # Check whether number of PC's that are to be computed is provided.
        # If NOT, then number of PC's is set to either number of objects or
        # variables of X, whichever is smaller (maxPC). If number of  
        # PC's IS provided, then number is checked against maxPC and set to
        # maxPC if provided number is larger.
        if 'numPC' not in kargs.keys():
            self.numPC = min(np.shape(arrX))
        else:
            if kargs['numPC'] > min(np.shape(arrX)):
                self.numPC = min(np.shape(arrX))
            else:
                self.numPC = kargs['numPC']
        
        # Define X and y within class such that the data can be accessed from
        # all attributes in class.
        self.arrX_input = arrX
        self.vecy_input = vecy
        
       
       # Pre-process data according to user request.
        # -------------------------------------------
        # Check whether standardisation of X and Y are requested by user. If 
        # NOT, then X and y are centred by default. 
        if 'Xstand' not in kargs.keys():
            self.Xstand = False
        else:
            self.Xstand = kargs['Xstand']
        
        if 'Ystand' not in kargs.keys():
            self.ystand = False
        else:
            self.ystand = kargs['Ystand']
        
                
        # Standardise X if requested by user, otherwise center X.
        if self.Xstand == True:
            Xmeans = np.average(self.arrX_input, axis=0)            
            Xstd = np.std(self.arrX_input, axis=0, ddof=1)
            self.arrX = (self.arrX_input - Xmeans) / Xstd
        else:
            Xmeans = np.average(self.arrX_input, axis=0)            
            self.arrX = self.arrX_input - Xmeans
        
        # Standardise Y if requested by user, otherwise center Y.
        if self.ystand == True:            
            vecyMean = np.average(self.vecy_input)
            yStd = np.std(self.vecy_input, ddof=1)
            self.vecy = (self.vecy_input - vecyMean) / yStd
        else:           
            vecyMean = np.average(self.vecy_input)
            self.vecy = self.vecy_input - vecyMean
        

        # Check whether cvType is provided. If NOT, then use "loo" by default.
        if 'cvType' not in kargs.keys():
            self.cvType = ["loo"]
        else:
            self.cvType = kargs['cvType']
        
                
        # Before PLS1 NIPALS algorithm starts initiate dictionaries and lists
        # in which results are stored.
        self.x_scoresList = []
        self.x_loadingsList = []
        self.y_scoresList = []
        self.y_loadingsList = []
        self.x_loadingsWeightsList = []
        self.coeffList = []
        self.Y_residualsList = [self.vecy]
        self.X_residualsList = [self.arrX]
        
        
#===============================================================================
#        Here PLS1 NIPALS algorithm starts 
#===============================================================================
        X_new = self.arrX.copy()
        y_new = self.vecy.copy()
        
        # Compute j number of components
        for j in range(self.numPC):
            
            # Module 7: STEP 1            
            w_num = np.dot(np.transpose(X_new), y_new)
            w_denom = npla.norm(w_num)
            w = w_num / w_denom
            
            # Module 7: STEP 2
            t = np.dot(X_new, w)
            
            # Module 7: STEP 3
            # NOTE: c_hat (in Module 7 paper) = q (here in code) ==> Yloadings
            q_num = np.dot(np.transpose(t), y_new)
            q_denom = np.dot(np.transpose(t), t)
            q = q_num / q_denom
            
            # Module 7: STEP 4
            p_num = np.dot(np.transpose(X_new), t)
            p_denom = np.dot(np.transpose(t), t)
            p = p_num / p_denom
            
            # Module 7: STEP 5
            X_old = X_new.copy()
            X_new = X_old - np.dot(t, np.transpose(p))
            
            y_old = y_new.copy()
            y_new = y_old - t*q
            
            # Collect vectors t, p, u, q, w and            
            self.x_scoresList.append(t.reshape(-1))
            self.x_loadingsList.append(p.reshape(-1))
            self.y_loadingsList.append(q.reshape(-1))
            self.x_loadingsWeightsList.append(w.reshape(-1))
            
            # Collect residuals
            self.Y_residualsList.append(y_new)
            self.X_residualsList.append(X_new)
        
        
        # Construct T, P, U, Q and W from lists of vectors
        self.arrT = np.array(np.transpose(self.x_scoresList))
        self.arrP = np.array(np.transpose(self.x_loadingsList))
        self.arrQ = np.array(np.transpose(self.y_loadingsList))
        self.arrW = np.array(np.transpose(self.x_loadingsWeightsList))
        
        
        # ---------------------------------------------------------------------
        # === COMPUTATIONS FOR X ===
        # Create a list holding arrays of Xhat predicted calibration after each 
        # component. Xhat is computed with Xhat = T*P'
        self.calXpredList = []
        
        # Compute Xhat for 1 and more components (cumulatively).        
        for ind in range(1,self.numPC+1):
            
            part_arrT = self.arrT[:,0:ind] 
            part_arrP = self.arrP[:,0:ind]
            predXcal = np.dot(part_arrT, np.transpose(part_arrP))
            
            if self.Xstand == True:
                Xhat = (predXcal * Xstd) + Xmeans
            else:
                Xhat = predXcal + Xmeans
            self.calXpredList.append(Xhat)
        
        
        # Construct a dictionary that holds predicted X (Xhat) from calibration
        # for each number of components.
        self.calXpredDict = {} 
        
        for ind, item in enumerate(self.calXpredList):
            self.calXpredDict[ind+1] = item
        
        # Construct a list that holds cumulative calibrated explained variance
        # in X.
        # First compute MSEE for zero components
        X_cent = st.centre(self.arrX_input)
        firstMSEE = np.sum(np.square(X_cent))
        self.XcumCalExplVarList = [0]
        
        # Compute MSEE for each Yhat for 1, 2, 3, etc number of components and
        # compute explained variance
        for Xhat in self.calXpredList:
            diffX = X_cent - st.centre(Xhat)
            MSEE = np.sum(np.square(diffX))
            self.XcumCalExplVarList.append((firstMSEE - MSEE) / firstMSEE * 100)
        
        
        # Construct a list that holds calibrated explained variance in X
        self.XcalExplVarList = []
        for ind, item in enumerate(self.XcumCalExplVarList):
            if ind == len(self.XcumCalExplVarList)-1: break
            explVarComp = self.XcumCalExplVarList[ind+1] - self.XcumCalExplVarList[ind]
            self.XcalExplVarList.append(explVarComp)
        # ---------------------------------------------------------------------
            
        
        # ---------------------------------------------------------------------
        # === COMPUTATIONS FOR Y =====
        # Create a list holding arrays of yhat predicted calibration after each 
        # component. yhat is computed with Yhat = T*Q'  
        self.calYpredList = []
        
        for ind in range(1, self.numPC+1):
            
            x_scores = self.arrT[:,0:ind]
            y_loadings = self.arrQ[:,0:ind]
            
            # Depending on whether Y was standardised or not compute Yhat
            # accordingly.            
            if self.ystand == True:
                yhat_stand = np.dot(x_scores, np.transpose(y_loadings))
                yhat = (yhat_stand * yStd.reshape(1,-1)) + vecyMean.reshape(1,-1)
            else:
                yhat = np.dot(x_scores, np.transpose(y_loadings)) \
                        + vecyMean
            self.calYpredList.append(yhat)
            
        
        # Construct a list that holds cumulative calibrated explained variance
        # in Y.
        # First compute MSEE for zero components
        y_cent = st.centre(self.vecy_input)
        firstMSEE = np.sum(np.square(y_cent))
        self.YcumCalExplVarList = [0]
        
        # Compute MSEE for each Yhat for 1, 2, 3, etc number of components and
        # compute explained variance
        for yhat in self.calYpredList:
            diffY = y_cent - st.centre(yhat)
            MSEE = np.sum(np.square(diffY))
            self.YcumCalExplVarList.append((firstMSEE - MSEE) / firstMSEE * 100)
        
        
        # Construct a list that holds calibrated explained variance in Y
        self.YcalExplVarList = []
        for ind, item in enumerate(self.YcumCalExplVarList):
            if ind == len(self.YcumCalExplVarList)-1: break
            explVarComp = self.YcumCalExplVarList[ind+1] - self.YcumCalExplVarList[ind]
            self.YcalExplVarList.append(explVarComp)
        
        
        # Construct a dictionary that holds predicted Y (Yhat) from calibration
        # for each number of components.
        self.calYpredDict = {}
        for ind, item in enumerate(self.calYpredList):
            self.calYpredDict[ind+1] = item             
        # ---------------------------------------------------------------------
        
        # ---------------------------------------------------------------------
        # Collect all PRESSE in a dictionary. Keys represent number of 
        # component.            
        self.PRESSEdict_indVar = {}
        
        # Compute PRESS for calibration / estimation
        PRESSE_0 = np.sum(np.square(self.vecy))
        self.PRESSEdict_indVar[0] = PRESSE_0
        
        # Compute PRESS for each Yhat for 1, 2, 3, etc number of components
        # and compute explained variance
        for ind, yhat in enumerate(self.calYpredList):
            diffY = self.vecy_input - yhat
            PRESSE = np.sum(np.square(diffY), axis=0)
            self.PRESSEdict_indVar[ind+1] = PRESSE
                    
        # Now store all PRESSE values into an array. Then compute MSEE and
        # RMSEE.
        self.PRESSEarr = np.array(self.PRESSEdict_indVar.values())
        self.MSEEarr = self.PRESSEarr / np.shape(self.vecy_input)[0]
        self.RMSEEarr = np.sqrt(self.MSEEarr)
        # ---------------------------------------------------------------------
        
        # -----------------------------------------------------------------
        # Compute explained variance for each variable in Y using the
        # MSEE for each variable. Also collect PRESSE, MSEE, RMSEE in 
        # their respective dictionaries for each variable. Keys represent 
        # now variables and NOT components as above with 
        # self.PRESSEdict_indVar
        self.cumCalExplVarYarr_indVar = np.zeros(np.shape(self.MSEEarr))
        MSEE_0 = self.MSEEarr[0]
        
        for ind, item in enumerate(self.MSEEarr):
            MSEE = item
            explVar = (MSEE_0 - MSEE) / MSEE_0 * 100
            self.cumCalExplVarYarr_indVar[ind] = explVar
                    
        self.PRESSEdict = {}
        self.MSEEdict = {}
        self.RMSEEdict = {}
        self.cumCalExplVarY_indVar = {}
        
        for ind in range(np.shape(self.PRESSEarr)[0]):
            self.PRESSEdict[ind] = self.PRESSEarr[ind]
            self.MSEEdict[ind] = self.MSEEarr[ind]
            self.RMSEEdict[ind] = self.RMSEEarr[ind]
            self.cumCalExplVarY_indVar[ind] = self.cumCalExplVarYarr_indVar[ind]
        # -----------------------------------------------------------------


#===============================================================================
#         Here starts the cross validation process of PLS1
#===============================================================================
        
        # Check whether cross validation is required by user. If required,
        # check what kind and build training and test sets thereafter.        
        if self.cvType == None:
            pass
        else:
            numObj = np.shape(self.vecy)[0]
            
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
                pass


            # Collect predicted y (i.e. yhat) for each CV segment in a  
            # dictionary according to numer of PC
            self.valYpredDict = {}
            for ind in range(1, self.numPC+1):
                self.valYpredDict[ind] = []            
            

            # Collect train and test set in dictionaries for each PC and put
            # them in this list.            
            self.cvTrainAndTestDataList = []            
            

            # Collect: validation X scores T, validation X loadings P,
            # validation Y scores U, validation Y loadings Q,
            # validation X loading weights W and scores regression coefficients C
            # in lists for each PC
            self.val_arrTlist = []
            self.val_arrPlist = []
            self.val_arrUlist = []
            self.val_arrQlist = []
            self.val_arrWlist = []            
            
            
            # First devide into combinations of training and test sets
            for train_index, test_index in cvComb:
                x_train, x_test = cv.split(train_index, test_index, self.arrX_input)
                y_train, y_test = cv.split(train_index, test_index, self.vecy_input)
                
                subDict = {}
                subDict['x train'] = x_train
                subDict['x test'] = x_test
                subDict['y train'] = y_train
                subDict['y test'] = y_test
                self.cvTrainAndTestDataList.append(subDict)
                
                
                # Collect X scores and Y loadings vectors from each iterations step
                val_x_scoresList = []
                val_x_loadingsList = []
                #val_y_scoresList = []
                val_y_loadingsList = []
                val_x_loadingsWeightsList = []
                
                
                # Standardise X if requested by user, otherwise center X.
                if self.Xstand == True:
                    x_train_means = np.average(x_train, axis=0)            
                    x_train_std = np.std(x_train, axis=0, ddof=1)
                    X_new = (x_train - x_train_means) / x_train_std
                else:
                    x_train_means = np.average(x_train, axis=0)            
                    X_new = x_train - x_train_means
                
                 # Standardise y if requested by user, otherwise center y.
                if self.ystand == True:            
                    y_train_mean = np.average(y_train)
                    y_train_std = np.std(y_train, ddof=1)
                    y_new = (y_train - y_train_mean) / y_train_std
                else:           
                    y_train_mean = np.average(y_train)
                    y_new = y_train - y_train_mean
                
                
                # Compute j number of components
                for j in range(self.numPC):
                    
                    # Module 7: STEP 1            
                    w_num = np.dot(np.transpose(X_new), y_new)
                    w_denom = npla.norm(w_num)
                    w = w_num / w_denom
                    
                    # Module 7: STEP 2
                    t = np.dot(X_new, w)
                    
                    # Module 7: STEP 3
                    q_num = np.dot(np.transpose(t), y_new)
                    q_denom = np.dot(np.transpose(t), t)
                    q = q_num / q_denom
                    
                    # Module 7: STEP 4
                    p_num = np.dot(np.transpose(X_new), t)
                    p_denom = np.dot(np.transpose(t), t)
                    p = p_num / p_denom
                    
                    # Module 7: STEP 5
                    X_old = X_new.copy()
                    X_new = X_old - np.dot(t, np.transpose(p))
                    
                    y_old = y_new.copy()
                    y_new = y_old - t*q
                    
                     # Collect vectors t, p, u, q, w and            
                    val_x_scoresList.append(t.reshape(-1))
                    val_x_loadingsList.append(p.reshape(-1))
                    val_y_loadingsList.append(q.reshape(-1))
                    val_x_loadingsWeightsList.append(w.reshape(-1))
                    
                                
                # Construct T, P, U, Q and W from lists of vectors
                val_arrT = np.array(np.transpose(val_x_scoresList))
                val_arrP = np.array(np.transpose(val_x_loadingsList))
                val_arrQ = np.array(np.transpose(val_y_loadingsList))
                val_arrW = np.array(np.transpose(val_x_loadingsWeightsList))
                
                self.val_arrTlist.append(val_arrT)
                self.val_arrPlist.append(val_arrP)
                self.val_arrQlist.append(val_arrQ)
                self.val_arrWlist.append(val_arrW)
                
                
                                
                # 'Module 7: Partial least squares regression I' - section 7.2 
                # Prediction for PLS2.
                if self.Xstand == True:
                    x_new = (x_test - x_train_means) / x_train_std
                else:
                    x_new = x_test - x_train_means 
                
                t_list = []
                for ind in range(self.numPC):
                    
                    # Module 8: Prediction STEP 1                    
                    t = np.dot(x_new, val_arrW[:,ind]).reshape(-1,1)
                    
                    # Module 8: Prediction STEP 2
                    p = val_arrP[:,ind].reshape(-1,1)                    
                    x_old = x_new
                    x_new = x_old - np.dot(t,np.transpose(p))
                    
                    # Generate a vector t that gets longer by one element with
                    # each PC
                    t_list.append(list(t)[0])                   
                    t_vec = np.transpose(np.array(t_list))

                    # Give vector y_train_mean the correct dimension in 
                    # numpy, so matrix multiplication will be possible
                    # i.e from dimension (x,) to (1,x)                    
                    ytm = y_train_mean.reshape(1,-1)
                    
                    # Get relevant part of Q for specific number of PC's                   
                    part_val_arrQ = val_arrQ[0,0:ind+1]
                    
                    # Module 8: Prediction STEP 3                                        
                    if self.ystand == True:
                        tCQ = np.dot(t_vec,part_val_arrQ) * y_train_std.reshape(1,-1)
                    else:
                        tCQ = np.dot(t_vec,part_val_arrQ)
                    
                    yhat = ytm + tCQ
                    self.valYpredDict[ind+1].append(yhat.reshape(-1))
                    
                        
            # Convert vectors from CV segments stored in lists into matrices 
            # for each PC            
            for key in self.valYpredDict:
                self.valYpredDict[key] = np.array(self.valYpredDict[key])
            
            
            
            # -----------------------------------------------------------------
            # Compute PRESS (PRediction Error Sum of Squares) for cross 
            # validation 
            self.valYpredList = self.valYpredDict.values()
            
            # Collect all PRESS in a dictionary. Keys represent number of 
            # component.            
            #self.PRESSdict = {}
            self.PRESSCVdict = {}
            
            # First compute PRESS for zero components            
            varY = np.var(self.vecy_input, ddof=1)
            self.PRESS_0 = (varY * np.square(np.shape(self.vecy_input)[0])) \
                    / np.shape(x_train)[0]
            self.PRESSCVdict[0] = self.PRESS_0
            
            # Compute PRESS for each Yhat for 1, 2, 3, etc number of components
            # and compute explained variance
            for ind, yhat in enumerate(self.valYpredList):
                diffy = self.vecy_input - yhat
                PRESS = np.sum(np.square(diffy), axis=0)
                self.PRESSCVdict[ind+1] = float(PRESS)
                        
            # Now store all PRESS values into an array. Then compute MSECV and
            # RMSECV.
            self.PRESSCVarr = np.array(self.PRESSCVdict.values())
            self.MSECVarr = self.PRESSCVarr / np.shape(self.vecy_input)[0]
            self.RMSECVarr = np.sqrt(self.MSECVarr)
            # -----------------------------------------------------------------
            
            # -----------------------------------------------------------------
            # Collect MSECV in a dictionary. Also,
            # compute total validated explained variance in Y.             
            self.MSECVdict = {}
            MSECV0 = self.MSECVarr[0]

            # Compute total validated explained variance in Y
            self.YcumValExplVarList = []
            for ind, MSECV in enumerate(self.MSECVarr):
                perc = (MSECV0 - MSECV) / MSECV0 * 100
                self.MSECVdict[ind] = MSECV
                self.YcumValExplVarList.append(perc)
            
            # Construct list with total validated explained variance in Y
            self.YvalExplVarList = []
            for ind, item in enumerate(self.YcumValExplVarList):
                if ind == len(self.YcumValExplVarList)-1: break
                explVarComp = self.YcumValExplVarList[ind+1] - self.YcumValExplVarList[ind]
                self.YvalExplVarList.append(explVarComp)
            # -----------------------------------------------------------------
            
            # -----------------------------------------------------------------
            # Compute total RMSECV and store values in a dictionary and list.            
            self.RMSECVdict = {}
            for ind, RMSECV in enumerate(self.RMSECVarr):
                self.RMSECVarr[ind] = RMSECV
            # -----------------------------------------------------------------
                
                
    
    
    
    def results(self):
        resDict = {}
        resDict['X'] = self.arrX
        resDict['y'] = self.vecy
        resDict['T'] = self.x_scoresList
        resDict['P'] = self.x_loadingsList
        resDict['Q'] = self.y_loadingsList
        resDict['W'] = self.x_loadingsWeightsList
        
        return resDict
    
        
    def modelSettings(self):
        """
        Collect settings under which PLS1 was run.
        """
        settingsDict = {}
        settingsDict['numPC'] = self.numPC
        settingsDict['X'] = self.arrX_input
        settingsDict['y'] = self.vecy_input
        settingsDict['analysed X'] = self.arrX
        settingsDict['analysed y'] = self.vecy 
        settingsDict['Xstand'] = self.Xstand
        settingsDict['ystand'] = self.ystand
        settingsDict['cv type'] = self.cvType
        
        return settingsDict
    
    
    def Xscores(self):
        """
        Returns an array holding X scores. First column for component 1, etc.
        """
        return self.arrT
    
    
    def Xloadings(self):
        """
        Returns an array holding X loadings. First column for component 1, etc.
        """
        return self.arrP
    
    
    def Yscores(self):
        """
        Returns an array holding Y scores. First column for component 1, etc.
        """
        return self.arrU
    
    
    def Yloadings(self):
        """
        Returns an array holding Y loadings. First column for component 1, etc.
        """
        return self.arrQ
    
    
    def XloadingsWeights(self):
        """
        Returns an array holding X loadings weights.
        """
        return self.arrW
    
    
    def XcorrLoadings(self):
        """
        Returns correlation loadings. First column holds correlation loadings
        for PC1, second column holds scores for PC2, etc.
        """

        # Creates empty matrix for correlation loadings
        arr_XcorrLoadings = np.zeros((np.shape(self.arrT)[1], \
            np.shape(self.arrP)[0]), float)
        
        # Compute correlation loadings:
        # For each PC in score matrix
        for PC in range(np.shape(self.arrT)[1]):
            PCscores = self.arrT[:, PC]
            
            # For each variable/attribute in original matrix (not meancentered)
            for var in range(np.shape(self.arrX)[1]):
                origVar = self.arrX[:, var]
                corrs = np.corrcoef(PCscores, origVar)
                arr_XcorrLoadings[PC, var] = corrs[0,1]
        
        self.arr_XcorrLoadings = np.transpose(arr_XcorrLoadings)
        
        return self.arr_XcorrLoadings
    
    
    def YcorrLoadings(self):
        """
        Returns correlation loadings. First column holds correlation loadings
        for PC1, second column holds scores for PC2, etc.
        """

        # Creates empty matrix for correlation loadings
        arr_ycorrLoadings = np.zeros((np.shape(self.arrT)[1], \
            np.shape(self.arrQ)[0]), float)
        
        # Compute correlation loadings:
        # For each PC in score matrix
        for PC in range(np.shape(self.arrT)[1]):
            PCscores = self.arrT[:, PC]
            
            # For each variable/attribute in original matrix (not meancentered)
            for var in range(np.shape(self.vecy)[1]):
                origVar = self.vecy[:, var]
                corrs = np.corrcoef(PCscores, origVar)
                arr_ycorrLoadings[PC, var] = corrs[0,1]
        
        self.arr_ycorrLoadings = np.transpose(arr_ycorrLoadings)
        
        return self.arr_ycorrLoadings
    
    
    def Yresiduals(self):
        """
        Returns list holding residuals F of Y after each component.
        """
        return self.Y_residualsList
    
    
    def Xresiduals(self):
        """
        Returns list holding  residuals E of X after each component.
        """
        return self.X_residualsList
    
    
    def Xmeans(self):
        """
        Returns a vector holding the column means of X. 
        """
        return np.average(self.arrX_input, axis=0)
    
    
    def Ymeans(self):
        """
        Returns a vector holding the column means of Y. 
        """
        return np.average(self.vecy_input)
    
    
    def XpredCal(self):
        """
        Returns dictionary holding arrays of predicted Xhat after each component 
        from calibration. Dictionary key represents order of PC. Yhat is 
        computed with Xhat = T*P'
        """
        return self.calXpredDict
    
    
    def YpredCal(self):
        """
        Returns dictionary holding arrays of predicted Yhat after each component 
        from calibration. Dictionary key represents order of PC. Yhat is 
        computed with Yhat = T*Chat*Q'
        """
        return self.calYpredDict
    
    
    def YcalExplVar_tot_list(self):
        """
        Returns list holding calibrated explained variance for each PC in Y.
        """
        return self.YcalExplVarList
    
    
    def YcumCalExplVar_tot_list(self):
        """
        Returns list holding cumulative calibrated explained variance in Y.
        """
        return self.YcumCalExplVarList
    
    
    def XcalExplVar_tot_list(self):
        """
        Returns list holding calibrated explained variance for each PC in X.
        """
        return self.XcalExplVarList
    
    
    def XcumCalExplVar_tot_list(self):
        """
        Returns list holding cumulative calibrated explained variance in X.
        """
        return self.XcumCalExplVarList
    
    
    def PRESSE_tot_list(self):
        """
        Returns an array holding PRESS of all variables in Y acquired through 
        calibration after each computed PC. First row is PRESS for zero
        components, second row component 1, third row for component 2, etc.
        """   
        return self.PRESSEarr
    
    
    def PRESSE_tot_dict(self):
        """
        Returns a dictionary holding PRESS off all variables in Y acquire
        through cross validation after each computed PC. Dictionary key 
        represents order of variable in Y.
        """
        return self.PRESSEdict
    
    
    def MSEE_tot_list(self):
        """
        Returns an array holding MSECV of all variables in Y acquired through 
        cross validation after each computed PC. First row is PRESS for zero
        components, second row component 1, third row for component 2, etc.
        """   
        return self.MSEEarr
    
    
    def MSEE_tot_dict(self):
        """
        Returns a dictionary holding MSEP from cross validation after each
        computed PC. Dictionary key represents order of variable in Y.
        """   
        return self.MSEEdict
    
    
    def RMSEE_tot_list(self):
        """
        Returns an array holding MSECV of all variables in Y acquired through 
        cross validation after each computed PC. First row is PRESS for zero
        components, second row component 1, third row for component 2, etc.
        """   
        return self.RMSEEarr
    
    
    def RMSEE_tot_dict(self):
        """
        Returns a dictionary holding total MSEP from cross validation after each
        computed PC. Dictionary key represents order of variable in Y.
        """   
        return self.RMSEEdict


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
    
    
    def cvTrainAndTestData(self):
        """
        Returns a list consisting of dictionaries holding training and test 
        sets.
        """
        return self.cvTrainAndTestDataList


    def YpredVal(self):
        """
        Returns dictionary holding arrays of predicted Yhat after each component 
        from validation. Dictionary key represents order of PC.
        """
        return self.valYpredDict
    
    
    def YcumValExplVar_tot_list(self):
        """
        Returns list holding cumulative calibrated explained variance in Y.
        """
        return self.YcumValExplVarList
    
    
    def YvalExplVar_tot_list(self):
        """
        Returns list holding calibrated explained variance for each PC in Y.
        """
        return  self.YvalExplVarList
    
    
    def PRESSCV_tot_list(self):
        """
        Returns an array holding PRESS of all variables in Y acquired through 
        calibration after each computed PC. First row is PRESS for zero
        components, second row component 1, third row for component 2, etc.
        """   
        return self.PRESSCVarr
    
    
    def PRESSCV_tot_dict(self):
        """
        Returns a dictionary holding PRESS off all variables in Y acquire
        through cross validation after each computed PC. Dictionary key 
        represents order of variable in Y.
        """
        return self.PRESSCVdict
    
    
    def MSECV_tot_list(self):
        """
        Returns an array holding MSECV of all variables in Y acquired through 
        cross validation after each computed PC. First row is PRESS for zero
        components, second row component 1, third row for component 2, etc.
        """   
        return self.MSECVarr
    
    
    def MSECV_tot_dict(self):
        """
        Returns a dictionary holding MSEP from cross validation after each
        computed PC. Dictionary key represents order of variable in Y.
        """   
        return self.MSECVdict
    
    
    def RMSECV_tot_list(self):
        """
        Returns an array holding MSECV of all variables in Y acquired through 
        cross validation after each computed PC. First row is PRESS for zero
        components, second row component 1, third row for component 2, etc.
        """   
        return self.RMSECVarr
    
    
    def RMSECV_tot_dict(self):
        """
        Returns a dictionary holding total MSEP from cross validation after each
        computed PC. Dictionary key represents order of variable in Y.
        """   
        return self.RMSECVdict
    



class nipalsPLS2:
    """
    GENERAL INFO
    ------------
    This class carries out Partial Least Squares Regression (PLS2) between the 
    two data matrices X and Y.
    """
    
    def __init__(self, arrX, arrY, **kargs):
        """
        On initialisation check whether number of PC's chosen by user is given
        and smaller than maximum number of PC's possible.Then check how X and Y
        are to be pre-processed (whether 'xstand' and 'ystand' are used). Then
        run NIPALS PLS2 algorithm.
        """
#===============================================================================
#         Check what is provided by user for PLS2
#===============================================================================
        
        # Check whether number of PC's that are to be computed is provided.
        # If NOT, then number of PC's is set to either number of objects or
        # variables of X whichever is smallest (numPC). If number of  
        # PC's IS provided, then number is checked against maxPC and set to
        # numPC if provided number is larger.
        if 'numPC' not in kargs.keys(): 
            self.numPC = min(np.shape(arrX))
        else:
            maxNumPC = min(np.shape(arrX))           
            if kargs['numPC'] > maxNumPC:
                self.numPC = maxNumPC
            else:
                self.numPC = kargs['numPC']
        
        
        # Define X and Y within class such that the data can be accessed from
        # all attributes in class.
        self.arrX_input = arrX
        self.arrY_input = arrY
        
                
        # Pre-process data according to user request.
        # -------------------------------------------
        # Check whether standardisation of X and Y are requested by user. If 
        # NOT, then X and y are centred by default. 
        if 'Xstand' not in kargs.keys():
            self.Xstand = False
        else:
            self.Xstand = kargs['Xstand']
        
        if 'Ystand' not in kargs.keys():
            self.Ystand = False
        else:
            self.Ystand = kargs['Ystand']
        
        
        # Standardise X if requested by user, otherwise center X.
        if self.Xstand == True:
            Xmeans = np.average(self.arrX_input, axis=0)            
            Xstd = np.std(self.arrX_input, axis=0, ddof=1)
            self.arrX = (self.arrX_input - Xmeans) / Xstd
        else:
            Xmeans = np.average(self.arrX_input, axis=0)            
            self.arrX = self.arrX_input - Xmeans
            
        
        # Standardise Y if requested by user, otherwise center Y.
        if self.Ystand == True:            
            Ymeans = np.average(self.arrY_input, axis=0)
            Ystd = np.std(self.arrY_input, axis=0, ddof=1)
            self.arrY = (self.arrY_input - Ymeans) / Ystd
        else:           
            Ymeans = np.average(self.arrY_input, axis=0)
            self.arrY = self.arrY_input - Ymeans
        
        
        # Check whether cvType is provided. If NOT, then use "loo" by default.
        if 'cvType' not in kargs.keys():
            self.cvType = ["loo"]
        else:
            self.cvType = kargs['cvType']
        
        
        # Before PLS2 NIPALS algorithm starts initiate dictionaries and lists
        # in which results are stored.
        self.x_scoresList = []
        self.y_scoresList = []
        self.x_loadingsList = []
        self.y_loadingsList = []
        self.x_loadingsWeightsList = []
        self.coeffList = []
        self.Y_residualsList = [self.arrY]
        self.X_residualsList = [self.arrX]
        

#===============================================================================
#        Here PLS2 NIPALS algorithm starts 
#===============================================================================
        threshold = 1.0e-12
        
        X_new = self.arrX
        Y_new = self.arrY
        
        # Compute number of principal components as specified by user 
        for j in range(self.numPC): 
            
            # Module 8: STEP 1            
            u_new = Y_new[:,0].copy().reshape(-1,1)
            
            # Iterate until Y score vector converges according to threshold
            runs = 0
            while 1:
                runs = runs + 1
                
                # Module 8: STEP 2
                w_num = np.dot(np.transpose(X_new), u_new)
                w_denom = npla.norm(w_num)
                w = w_num / w_denom
                
                # Module 8: STEP 3                
                t = np.dot(X_new, w)

                # Module 8: STEP 4
                q_num = np.dot(np.transpose(Y_new), t)
                q_denom = npla.norm(q_num)
                q = q_num / q_denom
                
                # Module 8: STEP 5
                u_old = u_new.copy()
                u_new = np.dot(Y_new, q)
                
                # Module 8: STEP 6                
                # Stop iteration when difference smaller than threshold or 100
                # iterations are reached.                
                diff = u_old - u_new
                SS = np.sum(np.square(diff))
                if SS <= threshold or runs==100:
                    break
                
            # Module 8: STEP 7
            c_num = np.dot(np.transpose(t), u_new)
            c_denom = np.dot(np.transpose(t), t)
            c = c_num / c_denom
            
            # Module 8: STEP 8
            p_num = np.dot(np.transpose(X_new), t)
            p_denom = np.dot(np.transpose(t), t)
            p = p_num / p_denom
            
            # Module 8: STEP 9            
            X_old = X_new.copy()
            X_new = X_old - np.dot(t, np.transpose(p))
            
            Y_old = Y_new.copy()
            Y_new = Y_old - c * np.dot(t, np.transpose(q))
            
            # Collect vectors t, p, u, q, w and scalar c            
            self.x_scoresList.append(t.reshape(-1))
            self.x_loadingsList.append(p.reshape(-1))
            self.y_scoresList.append(u_new.reshape(-1))
            self.y_loadingsList.append(q.reshape(-1))
            self.x_loadingsWeightsList.append(w.reshape(-1))
            self.coeffList.append(c.reshape(-1))
            
            # Collect residuals
            self.Y_residualsList.append(Y_new)
            self.X_residualsList.append(X_new)
            
        
        # Construct T, P, U, Q and W from lists of vectors
        self.arrT = np.array(np.transpose(self.x_scoresList))
        self.arrP = np.array(np.transpose(self.x_loadingsList))
        self.arrU = np.array(np.transpose(self.y_scoresList))
        self.arrQ = np.array(np.transpose(self.y_loadingsList))
        self.arrW = np.array(np.transpose(self.x_loadingsWeightsList))
        self.arrC = np.eye(self.numPC) * np.array(np.transpose(self.coeffList))
        


        # ---------------------------------------------------------------------
        # === COMPUTATIONS FOR Y =====
        # Create a list holding arrays of Yhat predicted calibration after each 
        # component. Yhat is computed with Yhat = T*Chat*Q'  
        self.calYpredList = []
        
        for ind in range(1, self.numPC+1):
            
            x_scores = self.arrT[:,0:ind]
            y_loadings = self.arrQ[:,0:ind]
            c_regrCoeff = self.arrC[0:ind,0:ind]
            
            # Depending on whether Y was standardised or not compute Yhat
            # accordingly.            
            if self.Ystand == True:
                Yhat_stand = np.dot(np.dot(x_scores, c_regrCoeff), np.transpose(y_loadings))
                Yhat = (Yhat_stand * Ystd.reshape(1,-1)) + Ymeans.reshape(1,-1)
            else:
                Yhat = np.dot(np.dot(x_scores, c_regrCoeff), np.transpose(y_loadings)) \
                        + Ymeans
            self.calYpredList.append(Yhat)
            
        
        # Construct a list that holds cumulative calibrated explained variance
        # in Y.
        # First compute MSEE for zero components
        Y_cent = st.centre(self.arrY_input)
        firstMSEE = np.sum(np.square(Y_cent))
        self.YcumCalExplVarList = [0]
        
        # Compute MSEE for each Yhat for 1, 2, 3, etc number of components and
        # compute explained variance
        for Yhat in self.calYpredList:
            diffY = Y_cent - st.centre(Yhat)
            MSEE = np.sum(np.square(diffY))
            self.YcumCalExplVarList.append((firstMSEE - MSEE) / firstMSEE * 100)
        
        
        # Construct a list that holds calibrated explained variance in Y
        self.YcalExplVarList = []
        for ind, item in enumerate(self.YcumCalExplVarList):
            if ind == len(self.YcumCalExplVarList)-1: break
            explVarComp = self.YcumCalExplVarList[ind+1] - self.YcumCalExplVarList[ind]
            self.YcalExplVarList.append(explVarComp)
        
        
        # Construct a dictionary that holds predicted Y (Yhat) from calibration
        # for each number of components.
        self.calYpredDict = {}
        for ind, item in enumerate(self.calYpredList):
            self.calYpredDict[ind+1] = item             
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # === COMPUTATIONS FOR X ===
        # Create a list holding arrays of Xhat predicted calibration after each 
        # component. Xhat is computed with Xhat = T*P'
        self.calXpredList = []
        
        # Compute Xhat for 1 and more components (cumulatively).        
        for ind in range(1,self.numPC+1):
            
            part_arrT = self.arrT[:,0:ind] 
            part_arrP = self.arrP[:,0:ind]
            predXcal = np.dot(part_arrT, np.transpose(part_arrP))
            
            if self.Xstand == True:
                Xhat = (predXcal * Xstd) + Xmeans
            else:
                Xhat = predXcal + Xmeans
            self.calXpredList.append(Xhat)
        
        
        # Construct a dictionary that holds predicted X (Xhat) from calibration
        # for each number of components.
        self.calXpredDict = {} 
        
        for ind, item in enumerate(self.calXpredList):
            self.calXpredDict[ind+1] = item
        
        # Construct a list that holds cumulative calibrated explained variance
        # in X.
        # First compute MSEE for zero components
        X_cent = st.centre(self.arrX_input)
        firstMSEE = np.sum(np.square(X_cent))
        self.XcumCalExplVarList = [0]
        
        # Compute MSEE for each Yhat for 1, 2, 3, etc number of components and
        # compute explained variance
        for Xhat in self.calXpredList:
            diffX = X_cent - st.centre(Xhat)
            MSEE = np.sum(np.square(diffX))
            self.XcumCalExplVarList.append((firstMSEE - MSEE) / firstMSEE * 100)
        
        
        # Construct a list that holds calibrated explained variance in X
        self.XcalExplVarList = []
        for ind, item in enumerate(self.XcumCalExplVarList):
            if ind == len(self.XcumCalExplVarList)-1: break
            explVarComp = self.XcumCalExplVarList[ind+1] - self.XcumCalExplVarList[ind]
            self.XcalExplVarList.append(explVarComp)
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Collect all PRESSE in a dictionary. Keys represent number of 
        # component.            
        self.PRESSEdict_indVar = {}
        
        # Compute PRESS for calibration / estimation
        PRESSE_0 = np.sum(np.square(self.arrY), axis=0)
        self.PRESSEdict_indVar[0] = PRESSE_0
        
        # Compute PRESS for each Yhat for 1, 2, 3, etc number of components
        # and compute explained variance
        for ind, Yhat in enumerate(self.calYpredList):
            diffY = self.arrY_input - Yhat
            PRESSE = np.sum(np.square(diffY), axis=0)
            self.PRESSEdict_indVar[ind+1] = PRESSE
                    
        # Now store all PRESSE values into an array. Then compute MSEE and
        # RMSEE.
        self.PRESSEarr_indVar = np.array(self.PRESSEdict_indVar.values())
        self.MSEEarr_indVar = self.PRESSEarr_indVar / np.shape(self.arrY_input)[0]
        self.RMSEEarr_indVar = np.sqrt(self.MSEEarr_indVar)
        # ---------------------------------------------------------------------
        
        # -----------------------------------------------------------------
        # Compute explained variance for each variable in Y using the
        # MSEP for each variable. Also collect PRESSE, MSEE, RMSEE in 
        # their respective dictionaries for each variable. Keys represent 
        # now variables and NOT components as above with 
        # self.PRESSEdict_indVar
        self.cumCalExplVarYarr_indVar = np.zeros(np.shape(self.MSEEarr_indVar))
        MSEE_0 = self.MSEEarr_indVar[0,:]
        
        for ind, item in enumerate(self.MSEEarr_indVar):
            MSEE = item
            explVar = (MSEE_0 - MSEE) / MSEE_0 * 100
            self.cumCalExplVarYarr_indVar[ind] = explVar
                    
        self.PRESSE_indVar = {}
        self.MSEE_indVar = {}
        self.RMSEE_indVar = {}
        self.cumCalExplVarY_indVar = {}
        
        for ind in range(np.shape(self.PRESSEarr_indVar)[1]):
            self.PRESSE_indVar[ind] = self.PRESSEarr_indVar[:,ind]
            self.MSEE_indVar[ind] = self.MSEEarr_indVar[:,ind]
            self.RMSEE_indVar[ind] = self.RMSEEarr_indVar[:,ind]
            self.cumCalExplVarY_indVar[ind] = self.cumCalExplVarYarr_indVar[:,ind]
        # -----------------------------------------------------------------
        
        # -----------------------------------------------------------------
        # Collect total MSECV across all variables in a dictionary. Also,
        # compute total validated explained variance in Y.             
        self.MSEE_total_dict = {}
        self.MSEE_total_list = np.sum(self.MSEEarr_indVar, axis=1) 

        for ind, MSEE in enumerate(self.MSEE_total_list):
            self.MSEE_total_dict[ind] = MSEE
        # -----------------------------------------------------------------
        
        # -----------------------------------------------------------------
        # Compute total RMSEP and store values in a dictionary and list.            
        self.RMSEE_total_dict = {}
        self.RMSEE_total_list = np.sqrt(self.MSEE_total_list)
        
        for ind, RMSEE in enumerate(self.RMSEE_total_list):
            self.RMSEE_total_dict[ind] = RMSEE
        # -----------------------------------------------------------------

#===============================================================================
#         Here starts the cross validation process
#===============================================================================
        
        # Check whether cross validation is required by user. If required,
        # check what kind and build training and test sets thereafter.        
        if self.cvType == None:
            pass
        else:
            numObj = np.shape(self.arrY)[0]
            
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
                pass
            
                        
            # Collect predicted y (i.e. yhat) for each CV segment in a  
            # dictionary according to numer of PC
            self.valYpredDict = {}
            for ind in range(1, self.numPC+1):
                self.valYpredDict[ind] = []            
            

            # Collect train and test set in dictionaries for each PC and put
            # them in this list.            
            self.cvTrainAndTestDataList = []            
            

            # Collect: validation X scores T, validation X loadings P,
            # validation Y scores U, validation Y loadings Q,
            # validation X loading weights W and scores regression coefficients C
            # in lists for each PC
            self.val_arrTlist = []
            self.val_arrPlist = []
            self.val_arrUlist = []
            self.val_arrQlist = []
            self.val_arrWlist = []
            self.val_arrClist = []            
            
            
            # First devide into combinations of training and test sets
            for train_index, test_index in cvComb:
                x_train, x_test = cv.split(train_index, test_index, self.arrX_input)
                y_train, y_test = cv.split(train_index, test_index, self.arrY_input)
                
                subDict = {}
                subDict['x train'] = x_train
                subDict['x test'] = x_test
                subDict['y train'] = y_train
                subDict['y test'] = y_test
                self.cvTrainAndTestDataList.append(subDict)
                
                
                # Collect X scores and Y loadings vectors from each iterations step
                val_x_scoresList = []
                val_x_loadingsList = []
                val_y_scoresList = []
                val_y_loadingsList = []
                val_x_loadingsWeightsList = []
                val_coeffList = []                
                
                
                # Here the PLS2 algorithm starts (cross validation)
                # ------------------------------------------------
                threshold = 1.0e-12
                
                # For cross validation pre-process data according to user
                # request                
                if self.Xstand == True:
                    x_train_means = np.average(x_train, axis=0)
                    x_train_std = np.std(x_train, axis=0, ddof=1)
                    X_new = (x_train - x_train_means) / x_train_std
                else:
                    x_train_means = np.average(x_train, axis=0)
                    X_new = x_train - x_train_means
                
                
                if self.Ystand == True:
                    y_train_means = np.average(y_train, axis=0)
                    y_train_std = np.std(y_train, axis=0, ddof=1)
                    Y_new = (y_train - y_train_means) / y_train_std
                else:
                    y_train_means = np.average(y_train, axis=0)
                    Y_new = y_train - y_train_means
                
                
                # Compute number of principal components as specified by user 
                for j in range(self.numPC): 
                    
                    # Module 8: STEP 1            
                    u_new = Y_new[:,0].copy().reshape(-1,1)
                    
                    # Iterate until Y score vector converges according to threshold
                    runs = 0
                    while 1:
                        runs = runs + 1
                
                        # Module 8: STEP 2
                        w_num = np.dot(np.transpose(X_new), u_new)
                        w_denom = npla.norm(w_num)
                        w = w_num / w_denom
                        
                        # Module 8: STEP 3                
                        t = np.dot(X_new, w)
        
                        # Module 8: STEP 4
                        q_num = np.dot(np.transpose(Y_new), t)
                        q_denom = npla.norm(q_num)
                        q = q_num / q_denom
                        
                        # Module 8: STEP 5
                        u_old = u_new.copy()
                        u_new = np.dot(Y_new, q)
                        
                        # Module 8: STEP 6                
                        # Stop iteration when difference smaller than threshold or 100
                        # iterations are reached.                
                        diff = u_old - u_new
                        SS = np.sum(np.square(diff))
                        if SS <= threshold or runs==100:
                            break
                        
                    # Module 8: STEP 7
                    c_num = np.dot(np.transpose(t), u_new)
                    c_denom = np.dot(np.transpose(t), t)
                    c = c_num / c_denom
                    
                    # Module 8: STEP 8
                    p_num = np.dot(np.transpose(X_new), t)
                    p_denom = np.dot(np.transpose(t), t)
                    p = p_num / p_denom
                    
                    # Module 8: STEP 9            
                    X_old = X_new.copy()
                    X_new = X_old - np.dot(t, np.transpose(p))
                    
                    Y_old = Y_new.copy()
                    Y_new = Y_old - c * np.dot(t, np.transpose(q))
                    
                    # Collect vectors t, p, u, q, w and scalar c            
                    val_x_scoresList.append(t.reshape(-1))
                    val_x_loadingsList.append(p.reshape(-1))
                    val_y_scoresList.append(u_new.reshape(-1))
                    val_y_loadingsList.append(q.reshape(-1))
                    val_x_loadingsWeightsList.append(w.reshape(-1))
                    val_coeffList.append(c.reshape(-1))
                    
                # Construct T, P, U, Q and W from lists of vectors
                val_arrT = np.array(np.transpose(val_x_scoresList))
                val_arrP = np.array(np.transpose(val_x_loadingsList))
                val_arrU = np.array(np.transpose(val_y_scoresList))
                val_arrQ = np.array(np.transpose(val_y_loadingsList))
                val_arrW = np.array(np.transpose(val_x_loadingsWeightsList))
                val_arrC = np.eye(self.numPC) * np.array(np.transpose(val_coeffList))
                
                self.val_arrTlist.append(val_arrT)
                self.val_arrPlist.append(val_arrP)
                self.val_arrUlist.append(val_arrU)
                self.val_arrQlist.append(val_arrQ)
                self.val_arrWlist.append(val_arrW)
                self.val_arrClist.append(val_arrC)
                
                                                
                # Compute SEP and yhat for PC1 and further
                # yhat is computed as in: 
                # 'Module 8: Partial least squares regression II' - section 8.2 
                # Prediction for PLS2.
                if self.Xstand == True:
                    x_new = (x_test - x_train_means) / x_train_std
                else:
                    x_new = x_test - x_train_means 
                
                t_list = []
                for ind in range(self.numPC):
                    
                    # Module 8: Prediction STEP 1                    
                    t = np.dot(x_new, val_arrW[:,ind]).reshape(-1,1)
                    
                    # Module 8: Prediction STEP 2
                    p = val_arrP[:,ind].reshape(-1,1)                    
                    x_old = x_new
                    x_new = x_old - np.dot(t,np.transpose(p))
                    
                    # Generate a vector t that gets longer by one element with
                    # each PC
                    t_list.append(list(t)[0])                   
                    t_vec = np.transpose(np.array(t_list))

                    # Give vector y_train_means the correct dimension in 
                    # numpy, so matrix multiplication will be possible
                    # i.e from dimension (x,) to (1,x)                    
                    ytm = y_train_means.reshape(1,-1)
                    
                    # Get relevant part of C anc Q for specific number of PC's                   
                    part_val_arrQ = val_arrQ[:,0:ind+1]
                    part_val_arrC = val_arrC[0:ind+1,0:ind+1]
                    
                    # Module 8: Prediction STEP 3                                        
                    if self.Ystand == True:
                        tCQ = np.dot(np.dot(t_vec,part_val_arrC), \
                                np.transpose(part_val_arrQ)) * y_train_std.reshape(1,-1)
                    else:
                        tCQ = np.dot(np.dot(t_vec,part_val_arrC), \
                                np.transpose(part_val_arrQ))
                    
                    yhat = ytm + tCQ
                    self.valYpredDict[ind+1].append(yhat.reshape(-1))
                    
                        
            # Convert vectors from CV segments stored in lists into matrices 
            # for each PC            
            for key in self.valYpredDict:
                self.valYpredDict[key] = np.array(self.valYpredDict[key])
            
            # -----------------------------------------------------------------
            # Compute PRESSCV (PRediction Error Sum of Squares) for cross 
            # validation 
            self.valYpredList = self.valYpredDict.values()
            
            # Collect all PRESS in a dictionary. Keys represent number of 
            # component.            
            self.PRESSdict_indVar = {}
            
            # First compute PRESSE for zero components            
            varY = np.var(self.arrY_input, axis=0, ddof=1)
            self.PRESSCV_0 = (varY * np.square(np.shape(self.arrY_input)[0])) \
                    / (np.shape(x_train)[0])
            self.PRESSdict_indVar[0] = self.PRESSCV_0
            
            # Compute PRESSCV for each Yhat for 1, 2, 3, etc number of components
            # and compute explained variance
            for ind, Yhat in enumerate(self.valYpredList):
                diffY = self.arrY_input - Yhat
                #diffY = st.centre(self.arrY_input, axis=0) - st.centre(Yhat)
                PRESSCV = np.sum(np.square(diffY), axis=0)
                self.PRESSdict_indVar[ind+1] = PRESSCV
                        
            # Now store all PRESSCV values into an array. Then compute MSECV and
            # RMSECV.
            self.PRESSCVarr_indVar = np.array(self.PRESSdict_indVar.values())
            self.MSECVarr_indVar = self.PRESSCVarr_indVar / np.shape(self.arrY_input)[0]
            self.RMSECVarr_indVar = np.sqrt(self.MSECVarr_indVar)
            # -----------------------------------------------------------------
            
            # -----------------------------------------------------------------
            # Compute explained variance for each variable in Y using the
            # MSEP for each variable. Also collect PRESS, MSECV, RMSECV in 
            # their respective dictionaries for each variable.  Keys represent 
            # now variables and NOT components as above with 
            # self.PRESSdict_indVar
            self.cumValExplVarYarr_indVar = np.zeros(np.shape(self.MSECVarr_indVar))
            MSECV_0 = self.MSECVarr_indVar[0,:]
            
            for ind, item in enumerate(self.MSECVarr_indVar):
                MSECV = item
                explVar = (MSECV_0 - MSECV) / MSECV_0 * 100
                self.cumValExplVarYarr_indVar[ind] = explVar
                        
            self.PRESSCV_indVar = {}
            self.MSECV_indVar = {}
            self.RMSECV_indVar = {}
            self.cumValExplVarY_indVar = {}
            
            for ind in range(np.shape(self.PRESSCVarr_indVar)[1]):
                self.PRESSCV_indVar[ind] = self.PRESSCVarr_indVar[:,ind]
                self.MSECV_indVar[ind] = self.MSECVarr_indVar[:,ind]
                self.RMSECV_indVar[ind] = self.RMSECVarr_indVar[:,ind]
                self.cumValExplVarY_indVar[ind] = self.cumValExplVarYarr_indVar[:,ind]
            # -----------------------------------------------------------------
            
            # -----------------------------------------------------------------
            # Collect total PRESSCV across all variables in a dictionary. Also,
            # compute total validated explained variance in Y.
            self.PRESSCV_total_dict = {}
            self.PRESSCV_total_list = np.sum(self.PRESSCVarr_indVar, axis=1)
            
            for ind, PRESSCV in enumerate(self.PRESSCV_total_list):
                self.PRESSCV_total_dict[ind] =PRESSCV
            # -----------------------------------------------------------------
            
            
            # -----------------------------------------------------------------
            # Collect total MSECV across all variables in a dictionary. Also,
            # compute total validated explained variance in Y.             
            self.MSECV_total_dict = {}
            self.MSECV_total_list = np.sum(self.MSECVarr_indVar, axis=1) 
            MSECV0 = self.MSECV_total_list[0]

            # Compute total validated explained variance in Y
            self.YcumValExplVarList = []
            for ind, MSECV in enumerate(self.MSECV_total_list):
                perc = (MSECV0 - MSECV) / MSECV0 * 100
                self.MSECV_total_dict[ind] = MSECV
                self.YcumValExplVarList.append(perc)
            
            # Construct list with total validated explained variance in Y
            self.YvalExplVarList = []
            for ind, item in enumerate(self.YcumValExplVarList):
                if ind == len(self.YcumValExplVarList)-1: break
                explVarComp = self.YcumValExplVarList[ind+1] - self.YcumValExplVarList[ind]
                self.YvalExplVarList.append(explVarComp)
            # -----------------------------------------------------------------
            
            # -----------------------------------------------------------------
            # Compute total RMSECV and store values in a dictionary and list.            
            self.RMSECV_total_dict = {}
            self.RMSECV_total_list = np.sqrt(self.MSECV_total_list)
            
            for ind, RMSECV in enumerate(self.RMSECV_total_list):
                self.RMSECV_total_dict[ind] = RMSECV
            # -----------------------------------------------------------------       
            
                            
        
            

    def results(self):
        resDict = {}
        resDict['T'] = self.arrT
        resDict['P'] = self.arrP
        resDict['U'] = self.arrU
        resDict['Q'] = self.arrQ
        resDict['W'] = self.arrW
        resDict['C'] = self.arrC
        
        resDict['val T'] = self.val_arrTlist
        resDict['val P'] = self.val_arrPlist
        resDict['val U'] = self.val_arrUlist
        resDict['val Q'] = self.val_arrQlist
        resDict['val W'] = self.val_arrWlist
        resDict['val C'] = self.val_arrClist
        
        resDict['val MSEP list'] = self.MSECV_total_dict.values()
        resDict['PRESSCV_0'] = self.PRESSCV_0
        
        resDict['PRESSE'] = self.PRESSEarr_indVar
        resDict['MSEE'] = self.MSEEarr_indVar
        resDict['RMSEE'] = self.RMSEEarr_indVar
        resDict['ind cum cal expl var Y'] = self.cumCalExplVarYarr_indVar
        
        
        return resDict
    
    
    def modelSettings(self):
        """
        Collect settings under which PLS2 was run.
        """
        settingsDict = {}
        settingsDict['numPC'] = self.numPC
        settingsDict['X'] = self.arrX_input
        settingsDict['Y'] = self.arrY_input
        settingsDict['Xstand'] = self.Xstand
        settingsDict['Ystand'] = self.Ystand
        settingsDict['analysed X'] = self.arrX
        settingsDict['analysed Y'] = self.arrY 
        settingsDict['cv type'] = self.cvType
        
        return settingsDict
    
    
    def Xscores(self):
        """
        Returns an array holding X scores. First column for component 1, etc.
        """
        return self.arrT
    
    
    def Xloadings(self):
        """
        Returns an array holding X loadings. First column for component 1, etc.
        """
        return self.arrP
    
    
    def Yscores(self):
        """
        Returns an array holding Y scores. First column for component 1, etc.
        """
        return self.arrU
    
    
    def Yloadings(self):
        """
        Returns an array holding Y loadings. First column for component 1, etc.
        """
        return self.arrQ
    
    
    def XloadingsWeights(self):
        """
        Returns an array holding X loadings weights.
        """
        return self.arrW
    
    
    def scoresRegressionCoeffs(self):
        """
        Returns a one dimensional array holding regression coefficients between
        X and Y scores.
        """ 
        return self.arrC
    
    
    def XcorrLoadings(self):
        """
        Returns correlation loadings. First column holds correlation loadings
        for PC1, second column holds scores for PC2, etc.
        """

        # Creates empty matrix for correlation loadings
        arr_XcorrLoadings = np.zeros((np.shape(self.arrT)[1], \
            np.shape(self.arrP)[0]), float)
        
        # Compute correlation loadings:
        # For each PC in score matrix
        for PC in range(np.shape(self.arrT)[1]):
            PCscores = self.arrT[:, PC]
            
            # For each variable/attribute in original matrix (not meancentered)
            for var in range(np.shape(self.arrX)[1]):
                origVar = self.arrX[:, var]
                corrs = np.corrcoef(PCscores, origVar)
                arr_XcorrLoadings[PC, var] = corrs[0,1]
        
        self.arr_XcorrLoadings = np.transpose(arr_XcorrLoadings)
        
        return self.arr_XcorrLoadings
    
    
    def YcorrLoadings(self):
        """
        Returns correlation loadings. First column holds correlation loadings
        for PC1, second column holds scores for PC2, etc.
        """

        # Creates empty matrix for correlation loadings
        arr_YcorrLoadings = np.zeros((np.shape(self.arrT)[1], \
            np.shape(self.arrQ)[0]), float)
        
        # Compute correlation loadings:
        # For each PC in score matrix
        for PC in range(np.shape(self.arrT)[1]):
            PCscores = self.arrT[:, PC]
            
            # For each variable/attribute in original matrix (not meancentered)
            for var in range(np.shape(self.arrY)[1]):
                origVar = self.arrY[:, var]
                corrs = np.corrcoef(PCscores, origVar)
                arr_YcorrLoadings[PC, var] = corrs[0,1]
        
        self.arr_YcorrLoadings = np.transpose(arr_YcorrLoadings)
        
        return self.arr_YcorrLoadings
    
    
    def Yresiduals(self):
        """
        Returns list holding residuals F of Y after each component.
        """
        return self.Y_residualsList
    
    
    def Xresiduals(self):
        """
        Returns list holding  residuals E of X after each component.
        """
        return self.X_residualsList
    
    
    def Xmeans(self):
        """
        Returns a vector holding the column means of X. 
        """
        return np.average(self.arrX_input, axis=0)
    
    
    def Ymeans(self):
        """
        Returns a vector holding the column means of Y. 
        """
        return np.average(self.arrY_input, axis=0)
        
    
    def YpredCal(self):
        """
        Returns dictionary holding arrays of predicted Yhat after each component 
        from calibration. Dictionary key represents order of PC. Yhat is 
        computed with Yhat = T*Chat*Q'
        """
        return self.calYpredDict
    
    
    def YpredVal(self):
        """
        Returns dictionary holding arrays of predicted Yhat after each component 
        from validation. Dictionary key represents order of PC.
        """
        return self.valYpredDict
    
    
    def XpredCal(self):
        """
        Returns dictionary holding arrays of predicted Xhat after each component 
        from calibration. Dictionary key represents order of PC. Yhat is 
        computed withXYhat = T*P'
        """
        return self.calXpredDict
    
    
    def YcumCalExplVar_tot_list(self):
        """
        Returns list holding cumulative calibrated explained variance in Y.
        """
        return self.YcumCalExplVarList
    
    
    def YcalExplVar_tot_list(self):
        """
        Returns list holding calibrated explained variance for each PC in Y.
        """
        return self.YcalExplVarList
    
    
    def YcumCalExplVar_indVar_arr(self):
        """
        Returns array holding cumulative validated explained variance in Y for
        each variable. Cols represent variables in Y. Rows represent number of
        components.
        """
        return self.cumCalExplVarYarr_indVar
    
    
    def YcumCalExplVar_indVar_dict(self):
        """
        Returns dictionary holding cumulative validated explained variance in Y 
        for each variable. Keys represent number of variable in Y.
        """
        return self.cumCalExplVarY_indVar


    def YcumValExplVar_tot_list(self):
        """
        Returns list holding cumulative calibrated explained variance in Y.
        """
        return self.YcumValExplVarList
    
    
    def YvalExplVar_tot_list(self):
        """
        Returns list holding calibrated explained variance for each PC in Y.
        """
        return  self.YvalExplVarList
    
    
    def YcumValExplVar_indVar_arr(self):
        """
        Returns array holding cumulative validated explained variance in Y for
        each variable. Rows represent variables in Y. Rows represent number of
        components.
        """
        return self.cumValExplVarYarr_indVar
    
    
    def YcumValExplVar_indVar_dict(self):
        """
        Returns dictionary holding cumulative validated explained variance in Y 
        for each variable. Keys represent number of variable in Y.
        """
        return self.cumValExplVarY_indVar
        
    
    def XcumCalExplVar_tot_list(self):
        """
        Returns list holding cumulative calibrated explained variance in X.
        """
        return self.XcumCalExplVarList
    
    
    def XcalExplVar_tot_list(self):
        """
        Returns list holding calibrated explained variance for each PC in X.
        """
        return self.XcalExplVarList
            
                
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
    
    
    def cvTrainAndTestData(self):
        """
        Returns a list consisting of dictionaries holding training and test 
        sets.
        """
        return self.cvTrainAndTestDataList
    
    
    def PRESSE_indVar_arr(self):
        """
        Returns an array holding PRESS of all variables in Y acquired through 
        calibration after each computed PC. First row is PRESS for zero
        components, second row component 1, third row for component 2, etc.
        """   
        return self.PRESSEarr_indVar
    
    
    def PRESSE_indVar_dict(self):
        """
        Returns a dictionary holding PRESS off all variables in Y acquire
        through cross validation after each computed PC. Dictionary key 
        represents order of variable in Y.
        """
        return self.PRESSE_indVar
    
    
    def MSEE_indVar_arr(self):
        """
        Returns an array holding MSECV of all variables in Y acquired through 
        cross validation after each computed PC. First row is PRESS for zero
        components, second row component 1, third row for component 2, etc.
        """   
        return self.MSEEarr_indVar
    
    
    def MSEE_indVar_dict(self):
        """
        Returns a dictionary holding MSEP from cross validation after each
        computed PC. Dictionary key represents order of variable in Y.
        """   
        return self.MSEE_indVar
    
    
    def RMSEE_indVar_arr(self):
        """
        Returns an array holding MSECV of all variables in Y acquired through 
        cross validation after each computed PC. First row is PRESS for zero
        components, second row component 1, third row for component 2, etc.
        """   
        return self.RMSEEarr_indVar
    
    
    def RMSEE_indVar_dict(self):
        """
        Returns a dictionary holding total MSEP from cross validation after each
        computed PC. Dictionary key represents order of variable in Y.
        """   
        return self.RMSEE_indVar
    
    
    def MSEE_tot_list(self):
        """
        Returns a dictionary holding total MSEP from cross validation after each
        computed PC. Dictionary key represents order of PC.
        """   
        return self.MSEE_total_list
    
    
    def MSEE_tot_dict(self):
        """
        Returns a dictionary holding total MSEP from cross validation after each
        computed PC. Dictionary key represents order of PC.
        """   
        return self.MSEE_total_dict
        
    
    def RMSEE_tot_list(self):
        """
        Returns a dictionary holding total RMSEP from cross validation after each
        computed PC. Dictionary key represents order of PC.
        """   
        return self.RMSEE_total_list
    
    
    def RMSEE_tot_dict(self):
        """
        Returns a dictionary holding total RMSEP from cross validation after each
        computed PC. Dictionary key represents order of PC.
        """   
        return self.RMSEE_total_dict
    
    
    def PRESSCV_indVar_arr(self):
        """
        Returns an array holding PRESS of all variables in Y acquired through 
        cross validation after each computed PC. First row is PRESS for zero
        components, second row component 1, third row for component 2, etc.
        """   
        return self.PRESSCVarr_indVar
    
    
    def PRESSCV_indVar_dict(self):
        """
        Returns a dictionary holding PRESS off all variables in Y acquire
        through cross validation after each computed PC. Dictionary key 
        represents order of variable in Y.
        """
        return self.PRESS_indVar
    
    
    def MSECV_indVar_arr(self):
        """
        Returns an array holding MSECV of all variables in Y acquired through 
        cross validation after each computed PC. First row is PRESS for zero
        components, second row component 1, third row for component 2, etc.
        """   
        return self.MSECVarr_indVar
    
    
    def MSECV_indVar_dict(self):
        """
        Returns a dictionary holding MSEP from cross validation after each
        computed PC. Dictionary key represents order of variable in Y.
        """   
        return self.MSECV_indVar
    
    
    def RMSECV_indVar_arr(self):
        """
        Returns an array holding MSECV of all variables in Y acquired through 
        cross validation after each computed PC. First row is PRESS for zero
        components, second row component 1, third row for component 2, etc.
        """   
        return self.RMSECVarr_indVar
    
    
    def RMSECV_indVar_dict(self):
        """
        Returns a dictionary holding total MSEP from cross validation after each
        computed PC. Dictionary key represents order of variable in Y.
        """   
        return self.RMSECV_indVar
    
    
    def PRESSCV_tot_list(self):
        """
        Returns a dictionary holding total MSEP from cross validation after each
        computed PC. Dictionary key represents order of PC.
        """   
        return self.PRESSCV_total_list
    
    
    def PRESSCV_tot_dict(self):
        """
        Returns a dictionary holding total MSEP from cross validation after each
        computed PC. Dictionary key represents order of PC.
        """   
        return self.PRESSCV_total_dict

    
    def MSECV_tot_list(self):
        """
        Returns a dictionary holding total MSEP from cross validation after each
        computed PC. Dictionary key represents order of PC.
        """   
        return self.MSECV_total_list
    
    
    def MSECV_tot_dict(self):
        """
        Returns a dictionary holding total MSEP from cross validation after each
        computed PC. Dictionary key represents order of PC.
        """   
        return self.MSECV_total_dict
        
    
    def RMSECV_tot_list(self):
        """
        Returns a dictionary holding total RMSEP from cross validation after each
        computed PC. Dictionary key represents order of PC.
        """   
        return self.RMSECV_total_list
    
    
    def RMSECV_tot_dict(self):
        """
        Returns a dictionary holding total RMSEP from cross validation after each
        computed PC. Dictionary key represents order of PC.
        """   
        return self.RMSECV_total_dict
        