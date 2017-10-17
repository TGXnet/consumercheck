# -*- coding: utf-8 -*-
"""PLSR module

Partial Least Squares Regression
"""

# Import necessary modules
import numpy as np
import numpy.linalg as npla
import hoggorm.statTools as st
import hoggorm.cross_val as cv



class nipalsPLS1:
    """
    This class carries out partial least squares regression (PLSR) for two 
    arrays using NIPALS algorithm. The y array is univariate, which is why
    PLS1 is applied.
    
    
    PARAMETERS
    ----------
    arrX : numpy array 
        This is X in the PLS1 model. Number and order of objects (rows) must 
        match those of vecy.
    vecy : numpy array of shape (n x 1).  
        This is y in the PLS1 model. Number and order of objects (rows)
        must match those of arrX.
    numComp : int
        An integer that defines how many components are to be computed. If not
        provided, the maximum possible number of components is used.
    Xstand : boolean 
        False : columns of arrX are mean centred (default)
        True : columns of arrX are mean centred and devided by their own 
            standard deviation
    Ystand : boolean 
        False : columns of arrY are mean centred (default)
        True : columns of arrY are mean centred and devided by their own 
            standard deviation
    cvType : list
        The list defines cross validation settings when computing the model. 
        Choose cross validation type from the following:
        
        loo : leave one out / a.k.a. full cross validation (default)
        cvType = ["loo"]
        
        KFold : leave out one fold or segment
        cvType = ["KFold", numFolds]
            numFolds: int 
            number of folds or segments
    
            
    RETURNS
    -------
    Returns PLS1 model. Use the attributes of class nipalsPLS1 to access    
    computational results of PLS1 model.
                           
                           
    EXAMPLES
    --------
    >>> import hoggorm as ho 
    
    >>> np.shape(my_X_data)
    (14, 292)
    
    >>> np.shape(my_y_data)
    (14, 1)
    
    >>> model = ho.nipalsPLS1(arrX=my_X_data, vecy=my_y_data, numComp=5)
    >>> model = ho.nipalsPLS1(arrX=my_X_data, vecy=my_y_data)
    >>> model = ho.nipalsPLS1(arrX=my_X_data, vecy=my_y_data, numComp=3, Ystand=True)
    >>> model = ho.nipalsPLS1(arrX=my_X_data, vecy=my_y_data, Xstand=False, Ystand=True)
    >>> model = ho.nipalsPLS1(arrX=my_X_data, vecy=my_y_data, cvType=["loo"])
    >>> model = ho.nipalsPLS1(arrX=my_X_data, vecy=my_y_data, cvType=["lpo", 4])
    
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
        if 'numComp' not in kargs.keys():
            self.numPC = min(np.shape(arrX))
        else:
            if kargs['numComp'] > min(np.shape(arrX)):
                self.numPC = min(np.shape(arrX))
            else:
                self.numPC = kargs['numComp']
        
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
        

        # Check whether cvType is provided. If NOT, then no cross validation
        # is carried out.
        if 'cvType' not in kargs.keys():
            self.cvType = None
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
        
        
        
        # ========== COMPUTATIONS FOR X ==========
        # ---------------------------------------------------------------------
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
        # ---------------------------------------------------------------------
         
         
        # ---------------------------------------------------------------------        
        # Construct a dictionary that holds predicted X (Xhat) from calibration
        # for each number of components.
        self.calXpredDict = {} 
        
        for ind, item in enumerate(self.calXpredList):
            self.calXpredDict[ind+1] = item
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Collect all PRESSE for individual variables in a dictionary. 
        # Keys represent number of component.            
        self.PRESSEdict_indVar_X = {}
        
        # Compute PRESS for calibration / estimation
        PRESSE_0_indVar_X = np.sum(np.square(st.centre(self.arrX_input)), \
                axis=0)
        self.PRESSEdict_indVar_X[0] = PRESSE_0_indVar_X
        
        # Compute PRESS for each Xhat for 1, 2, 3, etc number of components
        # and compute explained variance
        for ind, Xhat in enumerate(self.calXpredList):
            diffX = st.centre(self.arrX_input) - st.centre(Xhat)
            PRESSE_indVar_X = np.sum(np.square(diffX), axis=0)
            self.PRESSEdict_indVar_X[ind+1] = PRESSE_indVar_X
                    
        # Now store all PRESSE values into an array. Then compute MSEE and
        # RMSEE.
        self.PRESSEarr_indVar_X = np.array(list(self.PRESSEdict_indVar_X.values()))
        self.MSEEarr_indVar_X = self.PRESSEarr_indVar_X / \
                np.shape(self.arrX_input)[0]
        self.RMSEEarr_indVar_X = np.sqrt(self.MSEEarr_indVar_X)
        # ---------------------------------------------------------------------
         
         
        # ---------------------------------------------------------------------
        # Compute explained variance for each variable in X using the
        # MSEE for each variable. Also collect PRESSE, MSEE, RMSEE in 
        # their respective dictionaries for each variable. Keys represent 
        # now variables and NOT components as above with 
        # self.PRESSEdict_indVar_X
        self.cumCalExplVarXarr_indVar = np.zeros(np.shape(self.MSEEarr_indVar_X))
        MSEE_0_indVar_X = self.MSEEarr_indVar_X[0,:]
        
        for ind, MSEE_indVar_X in enumerate(self.MSEEarr_indVar_X):
            explVar = (MSEE_0_indVar_X - MSEE_indVar_X) / MSEE_0_indVar_X * 100
            self.cumCalExplVarXarr_indVar[ind] = explVar
                    
        self.PRESSE_indVar_X = {}
        self.MSEE_indVar_X = {}
        self.RMSEE_indVar_X = {}
        self.cumCalExplVarX_indVar = {}
        
        for ind in range(np.shape(self.PRESSEarr_indVar_X)[1]):
            self.PRESSE_indVar_X[ind] = self.PRESSEarr_indVar_X[:,ind]
            self.MSEE_indVar_X[ind] = self.MSEEarr_indVar_X[:,ind]
            self.RMSEE_indVar_X[ind] = self.RMSEEarr_indVar_X[:,ind]
            self.cumCalExplVarX_indVar[ind] = self.cumCalExplVarXarr_indVar[:,ind]
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Collect total PRESSE across all variables in a dictionary. Also,
        # compute total calibrated explained variance in X.
        self.PRESSE_total_dict_X = {}
        self.PRESSE_total_list_X = np.sum(self.PRESSEarr_indVar_X, axis=1)
        
        for ind, PRESSE_X in enumerate(self.PRESSE_total_list_X):
            self.PRESSE_total_dict_X[ind] = PRESSE_X
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Collect total MSEE across all variables in a dictionary. Also,
        # compute total validated explained variance in X.             
        self.MSEE_total_dict_X = {}
        self.MSEE_total_list_X = np.sum(self.MSEEarr_indVar_X, axis=1) / \
                np.shape(self.arrX_input)[1]        
        MSEE_0_X = self.MSEE_total_list_X[0]

        # Compute total calibrated explained variance in X
        self.XcumCalExplVarList = []
        if self.Xstand == False:
            for ind, MSEE_X in enumerate(self.MSEE_total_list_X):
                perc = (MSEE_0_X - MSEE_X) / MSEE_0_X * 100
                self.MSEE_total_dict_X[ind] = MSEE_X
                self.XcumCalExplVarList.append(perc)
        else:
            self.XcumCalExplVarArr = np.average(self.cumCalExplVarXarr_indVar, axis=1)
            self.XcumCalExplVarList = list(self.XcumCalExplVarArr)
        
        # Construct list with total validated explained variance in X
        self.XcalExplVarList = []
        for ind, item in enumerate(self.XcumCalExplVarList):
            if ind == len(self.XcumCalExplVarList)-1: break
            explVarComp = self.XcumCalExplVarList[ind+1] - \
                    self.XcumCalExplVarList[ind]
            self.XcalExplVarList.append(explVarComp)

        # Construct a dictionary that holds predicted X (Xhat) from calibration
        # for each number of components.
        self.calXpredDict = {}
        for ind, item in enumerate(self.calXpredList):
            self.calXpredDict[ind+1] = item 
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Compute total RMSEE and store values in a dictionary and list.            
        self.RMSEE_total_dict_X = {}
        self.RMSEE_total_list_X = np.sqrt(self.MSEE_total_list_X)
        
        for ind, RMSEE_X in enumerate(self.RMSEE_total_list_X):
            self.RMSEE_total_dict_X[ind] = RMSEE_X
        # ---------------------------------------------------------------------
        
        

        # ========== COMPUTATIONS FOR y ============
        # --------------------------------------------------------------------
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
                yhat = (yhat_stand * yStd.reshape(1,-1)) + \
                        vecyMean.reshape(1,-1)
            else:
                yhat = np.dot(x_scores, np.transpose(y_loadings)) \
                        + vecyMean
            self.calYpredList.append(yhat)
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------        
        # Construct a dictionary that holds predicted Y (Yhat) from calibration
        # for each number of components.
        self.calYpredDict = {}
        for ind, item in enumerate(self.calYpredList):
            self.calYpredDict[ind+1] = item
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Collect PRESSE for each PC in a dictionary. 
        # Keys represent number of component.            
        self.PRESSE_total_dict = {}
        self.MSEE_total_dict = {}
        
        # Compute PRESS and MSEE for calibration / estimation with zero
        # components
        PRESSE_0 = np.sum(np.square(st.centre(self.vecy_input)))
        self.PRESSE_total_dict[0] = PRESSE_0
        MSEE_0 = PRESSE_0 / np.shape(self.vecy_input)[0]
        self.MSEE_total_dict[0] = MSEE_0
        
        # Compute PRESS and MSEE for each Yhat for 1, 2, 3, etc number of 
        # components and compute explained variance
        for ind, yhat in enumerate(self.calYpredList):
            diffy = st.centre(self.vecy_input) - st.centre(yhat)
            PRESSE = np.sum(np.square(diffy))
            self.PRESSE_total_dict[ind+1] = PRESSE
            self.MSEE_total_dict[ind+1] = PRESSE / np.shape(self.vecy_input)[0]

        
        # Compute total calibrated explained variance in Y 
        self.MSEE_total_list = self.MSEE_total_dict.values()
        
        self.YcumCalExplVarList = []
        for ind, MSEE in enumerate(self.MSEE_total_list):
            perc = (MSEE_0 - MSEE) / MSEE_0 * 100
            self.YcumCalExplVarList.append(perc)
        
        # Construct list with total validated explained variance in Y
        self.YcalExplVarList = []
        for ind, item in enumerate(self.YcumCalExplVarList):
            if ind == len(self.YcumCalExplVarList)-1: break
            explVarComp = self.YcumCalExplVarList[ind+1] - \
                    self.YcumCalExplVarList[ind]
            self.YcalExplVarList.append(explVarComp)
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Compute total RMSEP and store values in a dictionary and list.            
        self.RMSEE_total_dict = {}
        self.RMSEE_total_list = np.sqrt(list(self.MSEE_total_list))

        
        for ind, RMSEE in enumerate(self.RMSEE_total_list):
            self.RMSEE_total_dict[ind] = RMSEE
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        self.PRESSEarr = np.array(list(self.PRESSE_total_dict.values()))
        self.MSEEarr = np.array(list(self.MSEE_total_dict.values()))
        self.RMSEEarr = np.array(list(self.RMSEE_total_dict.values()))
        # ---------------------------------------------------------------------


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
                print("loo")
                cvComb = cv.LeaveOneOut(numObj)
            elif self.cvType[0] == "KFold":
                print("KFold")
                cvComb = cv.KFold(numObj, k=self.cvType[1])
            elif self.cvType[0] == "lolo":
                print("lolo")
                cvComb = cv.LeaveOneLabelOut(self.cvType[1])
            else:
                print('Requested form of cross validation is not available')
                pass

            
            # Collect predicted y (i.e. yhat) for each CV segment in a  
            # dictionary according to numer of PC
            self.valYpredDict = {}
            for ind in range(1, self.numPC+1):
                self.valYpredDict[ind] = []
            
            # Construct a dictionary that holds predicted X (Xhat) from 
            # validation for each number of components. 
            self.valXpredDict = {}             
            for ind in range(1, self.numPC+1):
                self.valXpredDict[ind] = []
            

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
                    y_train_means = np.average(y_train)
                    y_train_std = np.std(y_train, ddof=1)
                    y_new = (y_train - y_train_means) / y_train_std
                else:           
                    y_train_means = np.average(y_train)
                    y_new = y_train - y_train_means
                
                
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
                    # ---------------------------
                    t = np.dot(x_new, val_arrW[:,ind]).reshape(-1,1)
                    
                    # Module 8: Prediction STEP 2
                    # ---------------------------
                    p = val_arrP[:,ind].reshape(-1,1)                    
                    x_old = x_new
                    x_new = x_old - np.dot(t,np.transpose(p))
                    
                    # Generate a vector t that gets longer by one element with
                    # each PC
                    t_list.append(t)                   
                    t_vec = np.hstack(t_list)

                    # Give vector y_train_mean the correct dimension in 
                    # numpy, so matrix multiplication will be possible
                    # i.e from dimension (x,) to (1,x)                    
                    ytm = y_train_means.reshape(1,-1)
                    xtm = x_train_means.reshape(1,-1)
                    
                    # Get relevant part of Q for specific number of PC's
                    part_val_arrP = val_arrP[:,0:ind+1]
                    part_val_arrQ = val_arrQ[0,0:ind+1]
                    
                    # Module 8: Prediction STEP 3
                    # ---------------------------
                    # First compute yhat                                      
                    if self.ystand == True:
                        tCQ = np.dot(t_vec,part_val_arrQ) * \
                                y_train_std.reshape(1,-1)
                    else:
                        tCQ = np.dot(t_vec,part_val_arrQ)
                    
                    yhat = np.transpose(ytm + tCQ)
                    self.valYpredDict[ind+1].append(yhat)
                    
                    # Then compute Xhat
                    if self.Xstand == True:
                        tP = np.dot(t_vec,np.transpose(part_val_arrP)) * \
                                x_train_std.reshape(1,-1)
                    else:
                        tP = np.dot(t_vec, np.transpose(part_val_arrP))
                    
                    xhat = xtm + tP
                    self.valXpredDict[ind+1].append(xhat)
                    
                    
                    
                        
            # ========== COMPUTATIONS FOR y ============
            # -----------------------------------------------------------------            
            # Convert vectors from CV segments stored in lists into matrices 
            # for each PC            
            for key in self.valYpredDict:
                self.valYpredDict[key] = np.vstack(self.valYpredDict[key])
            self.valYpredList = list(self.valYpredDict.values())
            # -----------------------------------------------------------------
            
                
            # -----------------------------------------------------------------
            # Collect all PRESSCV for individual variables in a dictionary. 
            # Keys represent number of component.            
            self.PRESSCV_total_dict = {}
            self.MSECV_total_dict = {}
            
            # Compute PRESS for validation
            varY = np.var(self.vecy_input, ddof=1)
            PRESSCV_0 = (varY * np.square(np.shape(self.vecy_input)[0])) \
                    / np.shape(self.vecy_input)[0]
            self.PRESSCV_total_dict[0] = PRESSCV_0
            MSECV_0 = PRESSCV_0 / np.shape(self.vecy_input)[0]
            self.MSECV_total_dict[0] = MSECV_0
            # -----------------------------------------------------------------
            
            # -----------------------------------------------------------------
            # Compute PRESSCV and MSECV for each Yhat for 1, 2, 3, etc number  
            # of components and compute explained variance
            for ind, yhat in enumerate(self.valYpredList):
                diffy = st.centre(self.vecy_input) - st.centre(yhat)
                PRESSCV = np.sum(np.square(diffy))
                self.PRESSCV_total_dict[ind+1] = PRESSCV
                self.MSECV_total_dict[ind+1] = PRESSCV / \
                        np.shape(self.vecy_input)[0]
            
            # Compute total validated explained variance in Y        
            self.MSECV_total_list = self.MSECV_total_dict.values()
            
            self.YcumValExplVarList = []
            for ind, MSECV in enumerate(self.MSECV_total_list):
                perc = (MSECV_0 - MSECV) / MSECV_0 * 100
                self.YcumValExplVarList.append(perc)
            
            # Construct list with total validated explained variance in Y
            self.YvalExplVarList = []
            for ind, item in enumerate(self.YcumValExplVarList):
                if ind == len(self.YcumValExplVarList)-1: break
                explVarComp = self.YcumValExplVarList[ind+1] - \
                        self.YcumValExplVarList[ind]
                self.YvalExplVarList.append(explVarComp)
            # -----------------------------------------------------------------
            
            
            # -----------------------------------------------------------------
            # Compute total RMSECV and store values in a dictionary and list.            
            self.RMSECV_total_dict = {}
            self.RMSECV_total_list = np.sqrt(list(self.MSECV_total_list))
            
            for ind, RMSECV in enumerate(self.RMSECV_total_list):
                self.RMSECV_total_dict[ind] = RMSECV
            # -----------------------------------------------------------------
            
            # -----------------------------------------------------------------
            self.PRESSCVarr = np.array(list(self.PRESSCV_total_dict.values()))
            self.MSECVarr = np.array(list(self.MSECV_total_dict.values()))
            self.RMSECVarr = np.array(list(self.RMSECV_total_dict.values()))
            # -----------------------------------------------------------------
            
            
            

            # ========== COMPUTATIONS FOR X ============
            # -----------------------------------------------------------------
            # Convert vectors from CV segments stored in lists into matrices 
            # for each PC            
            for key in self.valXpredDict:
                self.valXpredDict[key] = np.vstack(self.valXpredDict[key])
            self.valXpredList = self.valXpredDict.values()
            # -----------------------------------------------------------------
            
            
            # -----------------------------------------------------------------
            # Collect all PRESSCV for individual variables in X in a dictionary. 
            # Keys represent number of component.            
            self.PRESSCVdict_indVar_X = {}
            
            # First compute PRESSCV for zero components            
            varX = np.var(self.arrX_input, axis=0, ddof=1)
            PRESSCV_0_indVar_X = (varX * np.square(np.shape(self.arrX_input)[0])) \
                    / (np.shape(self.arrX_input)[0])
            self.PRESSCVdict_indVar_X[0] = PRESSCV_0_indVar_X
            
            # Compute PRESS for each Xhat for 1, 2, 3, etc number of components
            # and compute explained variance
            for ind, Xhat in enumerate(self.valXpredList):
                diffX = st.centre(self.arrX_input) - st.centre(Xhat)
                PRESSCV_indVar_X = np.sum(np.square(diffX), axis=0)
                self.PRESSCVdict_indVar_X[ind+1] = PRESSCV_indVar_X
                        
            # Now store all PRESSE values into an array. Then compute MSEE and
            # RMSEE.
            self.PRESSCVarr_indVar_X = np.array(list(self.PRESSCVdict_indVar_X.values()))
            self.MSECVarr_indVar_X = self.PRESSCVarr_indVar_X / \
                    np.shape(self.arrX_input)[0]
            self.RMSECVarr_indVar_X = np.sqrt(self.MSECVarr_indVar_X)
            # -----------------------------------------------------------------
            
            
            # -----------------------------------------------------------------
            # Compute explained variance for each variable in X using the
            # MSEP for each variable. Also collect PRESS, MSECV, RMSECV in 
            # their respective dictionaries for each variable. Keys represent 
            # now variables and NOT components as above with 
            # self.PRESSdict_indVar
            self.cumValExplVarXarr_indVar = np.zeros(np.shape(self.MSECVarr_indVar_X))
            MSECV_0_indVar_X = self.MSECVarr_indVar_X[0,:]
            
            for ind, MSECV_indVar_X in enumerate(self.MSECVarr_indVar_X):
                explVar = (MSECV_0_indVar_X - MSECV_indVar_X) / MSECV_0_indVar_X * 100
                self.cumValExplVarXarr_indVar[ind] = explVar
                        
            self.PRESSCV_indVar_X = {}
            self.MSECV_indVar_X = {}
            self.RMSECV_indVar_X = {}
            self.cumValExplVarX_indVar = {}
            
            for ind in range(np.shape(self.PRESSCVarr_indVar_X)[1]):
                self.PRESSCV_indVar_X[ind] = self.PRESSCVarr_indVar_X[:,ind]
                self.MSECV_indVar_X[ind] = self.MSECVarr_indVar_X[:,ind]
                self.RMSECV_indVar_X[ind] = self.RMSECVarr_indVar_X[:,ind]
                self.cumValExplVarX_indVar[ind] = self.cumValExplVarXarr_indVar[:,ind]
            # -----------------------------------------------------------------
            
            
            # -----------------------------------------------------------------
            # Collect total PRESSCV across all variables in a dictionary.
            self.PRESSCV_total_dict_X = {}
            self.PRESSCV_total_list_X = np.sum(self.PRESSCVarr_indVar_X, axis=1)
            
            for ind, PRESSCV_X in enumerate(self.PRESSCV_total_list_X):
                self.PRESSCV_total_dict_X[ind] = PRESSCV_X
            # -----------------------------------------------------------------
            
            
            # -----------------------------------------------------------------
            # Collect total MSECV across all variables in a dictionary. Also,
            # compute total validated explained variance in X.             
            self.MSECV_total_dict_X = {}
            self.MSECV_total_list_X = np.sum(self.MSECVarr_indVar_X, axis=1) / \
                    np.shape(self.arrX_input)[1]
            MSECV_0_X = self.MSECV_total_list_X[0]

            # Compute total validated explained variance in X
            self.XcumValExplVarList = []
            if self.Xstand == False:
                for ind, MSECV_X in enumerate(self.MSECV_total_list_X):
                    perc = (MSECV_0_X - MSECV_X) / MSECV_0_X * 100
                    self.MSECV_total_dict_X[ind] = MSECV_X
                    self.XcumValExplVarList.append(perc)
            else:
                self.XcumValExplVarArr = np.average(self.cumValExplVarXarr_indVar, axis=1)
                self.XcumValExplVarList = list(self.XcumValExplVarArr)
            
            # Construct list with total validated explained variance in X in 
            # each component
            self.XvalExplVarList = []
            for ind, item in enumerate(self.XcumValExplVarList):
                if ind == len(self.XcumValExplVarList)-1: break
                explVarComp = self.XcumValExplVarList[ind+1] - \
                        self.XcumValExplVarList[ind]
                self.XvalExplVarList.append(explVarComp)
            # -----------------------------------------------------------------
            
            
            # -----------------------------------------------------------------
            # Compute total RMSECV and store values in a dictionary and list.            
            self.RMSECV_total_dict_X = {}
            self.RMSECV_total_list_X = np.sqrt(self.MSECV_total_list_X)
            
            for ind, RMSECV_X in enumerate(self.RMSECV_total_list_X):
                self.RMSECV_total_dict_X[ind] = RMSECV_X
            # -----------------------------------------------------------------
    
    
        
    def modelSettings(self):
        """
        Returns a dictionary holding settings under which PLS1 was run.
        """
        settingsDict = {}
        settingsDict['numComp'] = self.numPC
        settingsDict['X'] = self.arrX_input
        settingsDict['y'] = self.vecy_input
        settingsDict['analysed X'] = self.arrX
        settingsDict['analysed y'] = self.vecy 
        settingsDict['Xstand'] = self.Xstand
        settingsDict['ystand'] = self.ystand
        settingsDict['cv type'] = self.cvType
        
        return settingsDict
    
    
    def X_means(self):
        """
        Returns array holding the column means of X. 
        """
        return np.average(self.arrX_input, axis=0).reshape(1,-1)
    
    
    def X_scores(self):
        """
        Returns array holding scores of array X. First column holds scores 
        for component 1, second column holds scores for component 2, etc.
        """
        return self.arrT
    
    
    def X_loadings(self):
        """
        Returns array holding loadings of array X. Rows represent variables
        and columns represent components. First column holds loadings for 
        component 1, second column holds scores for component 2, etc.
        """
        return self.arrP
    
    
    def X_loadingsWeights(self):
        """
        Returns an array holding X loadings weights.
        """
        return self.arrW
    
    
    def X_corrLoadings(self):
        """
        Returns array holding correlation loadings of array X. First column 
        holds correlation loadings for component 1, second column holds 
        correlation loadings for component 2, etc.
        """

        # Creates empty matrix for correlation loadings
        arr_XcorrLoadings = np.zeros((np.shape(self.arrT)[1], \
            np.shape(self.arrP)[0]), float)
        
        # Compute correlation loadings:
        # For each component in score matrix
        for PC in range(np.shape(self.arrT)[1]):
            PCscores = self.arrT[:, PC]
            
            # For each variable/attribute in original matrix (not meancentered)
            for var in range(np.shape(self.arrX)[1]):
                origVar = self.arrX[:, var]
                corrs = np.corrcoef(PCscores, origVar)
                arr_XcorrLoadings[PC, var] = corrs[0,1]
        
        self.arr_XcorrLoadings = np.transpose(arr_XcorrLoadings)
        
        return self.arr_XcorrLoadings
    
    
    def X_residuals(self):
        """
        Returns a dictionary holding the residual arrays for array X after 
        each computed component. Dictionary key represents order of component.
        """
        # Create empty dictionary that will hold residuals
        X_residualsDict = {}
        
        # Fill dictionary with residuals arrays from residuals list
        for ind, item in enumerate(self.X_residualsList):
            X_residualsDict[ind] = item
        
        return X_residualsDict
    
    
    def X_calExplVar(self):
        """
        Returns a list holding the calibrated explained variance for 
        each component. First number in list is for component 1, second number 
        for component 2, etc.
        """
        return self.XcalExplVarList
    
    
    def X_cumCalExplVar_indVar(self):
        """
        Returns an array holding the cumulative calibrated explained variance
        for each variable in X after each component. First row represents zero
        components, second row represents one component, third row represents 
        two components, etc. Columns represent variables.
        """
        return self.cumCalExplVarXarr_indVar
    
    
    def X_cumCalExplVar(self):
        """
        Returns a list holding the cumulative calibrated explained variance 
        for array X after each component. 
        """
        return self.XcumCalExplVarList
    
    
    def X_predCal(self):
        """
        Returns a dictionary holding the predicted arrays Xhat from 
        calibration after each computed component. Dictionary key represents 
        order of component.
        """
        return self.calXpredDict
    
    
    def X_PRESSE_indVar(self):
        """
        Returns array holding PRESSE for each individual variable in X
        acquired through calibration after each computed component. First row 
        is PRESSE for zero components, second row for component 1, third row 
        for component 2, etc.
        """
        return self.PRESSEarr_indVar_X
    
    
    def X_PRESSE(self):
        """
        Returns array holding PRESSE across all variables in X acquired  
        through calibration after each computed component. First row is PRESSE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.PRESSE_total_list_X
    
    
    def X_MSEE_indVar(self):
        """
        Returns an array holding MSEE for each variable in array X acquired 
        through calibration after each computed component. First row holds MSEE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """
        return self.MSEEarr_indVar_X
    
    
    def X_MSEE(self):
        """
        Returns an array holding MSEE across all variables in X acquired 
        through calibration after each computed component. First row is MSEE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.MSEE_total_list_X
    
    
    def X_RMSEE_indVar(self):
        """
        Returns an array holding RMSEE for each variable in array X acquired 
        through calibration after each component. First row holds RMSEE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """
        return self.RMSEEarr_indVar_X
    
    
    def X_RMSEE(self):
        """
        Returns an array holding RMSEE across all variables in X acquired 
        through calibration after each computed component. First row is RMSEE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.RMSEE_total_list_X
    
    
    def X_valExplVar(self):
        """
        Returns a list holding the validated explained variance for X after
        each component. First number in list is for component 1, second number 
        for component 2, third number for component 3, etc.
        """
        return  self.XvalExplVarList
    
    
    def X_cumValExplVar_indVar(self):
        """
        Returns an array holding the cumulative validated explained variance
        for each variable in X after each component. First row represents 
        zero components, second row represents component 1, third row for 
        compnent 2, etc. Columns represent variables.
        """
        return self.cumValExplVarXarr_indVar
    
    
    def X_cumValExplVar(self):
        """
        Returns a list holding the cumulative validated explained variance 
        for array X after each component. First number represents zero 
        components, second number represents component 1, etc. 
        """
        return self.XcumValExplVarList
    
    
    def X_predVal(self):
        """
        Returns dictionary holding arrays of predicted Xhat after each 
        component from validation. Dictionary key represents order of 
        component.
        """
        return self.valXpredDict
    
    
    def X_PRESSCV_indVar(self):
        """
        Returns array holding PRESSCV for each individual variable in X 
        acquired through cross validation after each computed component. First 
        row is PRESSCV for zero components, second row for component 1, third 
        row for component 2, etc.
        """
        return self.PRESSCVarr_indVar_X
    
    
    def X_PRESSCV(self):
        """
        Returns an array holding PRESSCV across all variables in X acquired  
        through cross validation after each computed component. First row is 
        PRESSCV for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.PRESSCV_total_list_X
    
    
    def X_MSECV_indVar(self):
        """
        Returns an arrary holding MSECV for each variable in X acquired through  
        cross validation. First row is MSECV for zero components, second row 
        for component 1, etc.
        """
        return self.MSECVarr_indVar_X
    
    
    def X_MSECV(self):
        """
        Returns an array holding MSECV across all variables in X acquired 
        through cross validation after each computed component. First row is 
        MSECV for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.MSECV_total_list_X
    
    
    def X_RMSECV_indVar(self):
        """
        Returns an arrary holding RMSECV for each variable in X acquired 
        through cross validation after each computed component. First row is 
        RMSECV for zero components, second row for component 1, third row for 
        component 2, etc.
        """
        return self.RMSECVarr_indVar_X
    
    
    def X_RMSECV(self):
        """
        Returns an array holding RMSECV across all variables in X acquired 
        through cross validation after each computed component. First row is 
        RMSECV for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.RMSECV_total_list_X

        
    def X_scores_predict(self, Xnew, numComp=1):
        """
        Returns array of X scores from new X data using the exsisting model. 
        Rows represent objects and columns represent components.
        """
        # Collect all predicted y (1 x 1) from one row of Xnew (1 x k) in a list
        XpredScoresList = []
        
        
        # Loop through each row in Xnew
        for X_rowInd in range(0, np.shape(Xnew)[0]):
        
            # 'Module 7: Partial least squares regression I' - section 7.2 
            # Prediction for PLS2.
            
            # First pre-process new X data accordingly
            if self.Xstand == True:
            
                x_new = (Xnew[X_rowInd, :] - np.average(self.arrX_input, axis=0)) / \
                        np.std(self.arrX_input, ddof=1)
            
            else:
                
                x_new = (Xnew[X_rowInd, :] - np.average(self.arrX_input, axis=0))
                    
                     
            t_list = []
            for ind in range(numComp):
                
                # Module 8: Prediction STEP 1
                # ---------------------------
                t = np.dot(x_new, self.arrW[:, ind]).reshape(-1, 1)
                
                # Module 8: Prediction STEP 2
                # ---------------------------
                p = self.arrP[:, ind].reshape(-1, 1)                    
                x_old = x_new
                x_new = x_old - np.dot(t, np.transpose(p))
                
                # Generate a vector t that gets longer by one element with
                # each PC
                t_list.append(list(t)[0])
            XpredScoresList.append(t_list)            

        return np.transpose(np.hstack(XpredScoresList))    
        
    
    def Y_means(self):
        """
        Returns an array holding the mean of vector y. 
        """
        return np.average(self.vecy_input)
    
    
    def Y_scores(self):
        """
        Returns scores of array Y (NOT IMPLEMENTED)
        """
        print("Not implemented")
        return None
    
    
    def Y_loadings(self):
        """
        Returns an array holding loadings of vector y. Columns represent 
        components. First column for component 1, second columns for 
        component 2, etc.
        """
        return self.arrQ
    
    
    def Y_corrLoadings(self):
        """
        Returns an array holding correlation loadings of vector y. Columns 
        represent components. First column for component 1, second columns for 
        component 2, etc.
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
    
    
    def Y_residuals(self):
        """
        Returns list of arrays holding residuals of vector y after each 
        component.
        """
        Y_residualsDict = {}
        for ind, item in enumerate(self.Y_residualsList):
            Y_residualsDict[ind] = item
        return Y_residualsDict
    
    
    def Y_calExplVar(self):
        """
        Returns list holding calibrated explained variance for each component 
        in vector y.
        """
        return self.YcalExplVarList
    
    
    def Y_cumCalExplVar(self):
        """
        Returns a list holding the calibrated explained variance for 
        each component. First number represent zero components, second number 
        one component, etc.
        """
        return self.YcumCalExplVarList
    
    
    def Y_predCal(self):
        """
        Returns dictionary holding arrays of predicted yhat after each component 
        from calibration. Dictionary key represents order of components.
        """
        return self.calYpredDict
    
    
    def Y_PRESSE(self):
        """
        Returns an array holding PRESSE for y acquired through calibration 
        after each computed component. First row is PRESSE for zero components, 
        second row component 1, third row for component 2, etc.
        """   
        return self.PRESSEarr
    
    
    def Y_MSEE(self):
        """
        Returns an array holding MSEE of vector y acquired through 
        calibration after each component. First row holds MSEE for zero
        components, second row component 1, third row for component 2, etc.
        """   
        return self.MSEEarr
    
    
    def Y_RMSEE(self):
        """
        Returns an array holding RMSEE of vector y acquired through calibration  
        after each computed component. First row is RMSEE for zero
        components, second row component 1, third row for component 2, etc.
        """   
        return self.RMSEEarr
    
    
    def Y_valExplVar(self):
        """
        Returns list holding validated explained variance for each component in 
        vector y.
        """
        return  self.YvalExplVarList
    
    
    def Y_cumValExplVar(self):
        """
        Returns list holding cumulative validated explained variance in 
        vector y.
        """
        return self.YcumValExplVarList
    
    
    def Y_predVal(self):
        """
        Returns dictionary holding arrays of predicted yhat after each 
        component from validation. Dictionary key represents order of component.
        """
        return self.valYpredDict
    
    
    def Y_PRESSCV(self):
        """
        Returns an array holding PRESSECV for Y acquired through cross 
        validation after each computed component. First row is PRESSECV for 
        zero components, second row component 1, third row for component 2, 
        etc.
        """   
        return self.PRESSCVarr
    
    
    def Y_MSECV(self):
        """
        Returns an array holding MSECV of vector y acquired  through cross 
        validation after each computed component. First row is MSECV for 
        zero components, second row component 1, third row for component 2, etc.
        """   
        return self.MSECVarr
    
    
    def Y_RMSECV(self):
        """
        Returns an array holding RMSECV for vector y acquired through cross 
        validation after each computed component. First row is RMSECV for zero 
        components, second row component 1, third row for component 2, etc.
        """   
        return self.RMSECVarr
    
    
    def Y_predict(self, Xnew, numComp=1):
        """
        Return predicted yhat from new measurements X. 
        """
        # Collect all predicted y (1 x 1) from one row of Xnew (1 x k) in a list
        ypredList = []
        
        
        # Loop through each row in Xnew
        for X_rowInd in range(0, np.shape(Xnew)[0]):

        
            # 'Module 7: Partial least squares regression I' - section 7.2 
            # Prediction for PLS2.
            
            # First pre-process new X data accordingly
            if self.Xstand == True:
            
                x_new = (Xnew[X_rowInd, :] - np.average(self.arrX_input, axis=0)) / \
                        np.std(self.arrX_input, ddof=1)
            
            else:
                
                x_new = (Xnew[X_rowInd, :] - np.average(self.arrX_input, axis=0))
                    
                  
            t_list = []
            for ind in range(numComp):
                
                # Module 8: Prediction STEP 1
                # ---------------------------
                t = np.dot(x_new, self.arrW[:, ind]).reshape(-1, 1)
                
                # Module 8: Prediction STEP 2
                # ---------------------------
                p = self.arrP[:, ind].reshape(-1, 1)                    
                x_old = x_new
                x_new = x_old - np.dot(t, np.transpose(p))
                
                # Generate a vector t that gets longer by one element with
                # each PC
                t_list.append(list(t)[0])                   
                t_vec = np.transpose(np.array(t_list))
    
                # Give vector y_train_mean the correct dimension in 
                # numpy, so matrix multiplication will be possible
                # i.e from dimension (x,) to (1,x)                    
                ytm = np.average(self.vecy_input).reshape(1, -1)
                
                # Get relevant part of Q for specific number of PC's
                part_arrQ = self.arrQ[0, 0:ind+1]
                
                # Module 8: Prediction STEP 3
                # ---------------------------
                # First compute yhat                                      
                if self.ystand == True:
                    tCQ = np.dot(t_vec, part_arrQ) * \
                            np.std(self.vecy_input, ddof=1).reshape(1, -1)
                else:
                    tCQ = np.dot(t_vec, part_arrQ)
                
                yhat = ytm + tCQ
            
            ypredList.append(yhat)
            
        return np.vstack(ypredList)

        
    def cvTrainAndTestData(self):
        """
        Returns a list consisting of dictionaries holding training and test 
        sets.
        """
        return self.cvTrainAndTestDataList
    

    def corrLoadingsEllipses(self):
        """
        Returns coordinates of ellipses that represent 50% and 100% expl. 
        variance in correlation loadings plot.
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

        
        
class nipalsPLS2:
    """
    This class carries out partial least squares regression (PLSR) for two 
    arrays using NIPALS algorithm. The Y array is multivariate, which is why
    PLS2 is applied.
        
    
    PARAMETERS
    ----------
    arrX : numpy array 
        This is X in the PLS2 model. Number and order of objects (rows) must 
        match those of vecy.
    arrY : numpy array
        This is Y in the PLS2 model. Number and order of objects (rows) must 
        match those of arrX.
    numComp : int
        An integer that defines how many components are to be computed. If not
        provided, the maximum possible number of components is used.
    Xstand : boolean 
        False : columns of arrX are mean centred prior to PCR (default)
        True : columns of arrX are mean centred and devided by their own 
            standard deviation.
    Ystand : boolean 
        False : columns of arrY are mean centred (default)
        True : columns of arrY are mean centred and devided by their own 
            standard deviation.
    cvType : list
        The list defines cross validation settings when computing the model.
        Choose cross validation type from the following:
        
        loo : leave one out / a.k.a. full cross validation (default)
        cvType = ["loo"]
        
        KFold : leave out one fold or segment
        cvType = ["KFold", numFolds]
            numFolds: int 
            number of folds or segments 

    
    RETURNS
    -------
    Returns PLS2 model. Use the attributes of class nipalsPLS2 to access    
    computational results of PLS2 model.
                           
                           
    EXAMPLES
    --------
    >>> import hoggorm as ho 
    
    >>> np.shape(my_X_data)
    (14, 292)
    
    >>> np.shape(my_Y_data)
    (14, 5)
       
    >>> model = ho.nipalsPLS2(arrX=my_X_data, arrY=my_Y_data, numComp=5)
    >>> model = ho.nipalsPLS2(arrX=my_X_data, arrY=my_Y_data)
    >>> model = ho.nipalsPLS2(arrX=my_X_data, arrY=my_Y_data, numComp=3, Ystand=True)
    >>> model = ho.nipalsPLS2(arrX=my_X_data, arrY=my_Y_data, Xstand=False, Ystand=True)
    >>> model = ho.nipalsPLS2(arrX=my_X_data, arrY=my_Y_data, cvType=["loo"])
    >>> model = ho.nipalsPLS2(arrX=my_X_data, arrY=my_Y_data, cvType=["lpo", 4])
    """
    
    def __init__(self, arrX, arrY, **kargs):
        """
        On initialisation check whether number of PC's chosen by user is given
        and smaller than maximum number of PC's possible.Then check how X and Y
        are to be pre-processed (whether 'Xstand' and 'Ystand' are used). Then
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
        if 'numComp' not in kargs.keys(): 
            self.numPC = min(np.shape(arrX))
        else:
            maxNumPC = min(np.shape(arrX))           
            if kargs['numComp'] > maxNumPC:
                self.numPC = maxNumPC
            else:
                self.numPC = kargs['numComp']
        
        
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
        
        
        # Check whether cvType is provided. If NOT, then no cross validation
        # is carried out.
        if 'cvType' not in kargs.keys():
            self.cvType = None
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
        
        
        
        # ========== COMPUTATIONS FOR Y ============
        # ---------------------------------------------------------------------
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
                Yhat_stand = np.dot(np.dot(x_scores, c_regrCoeff), \
                        np.transpose(y_loadings))
                Yhat = (Yhat_stand * Ystd.reshape(1,-1)) + Ymeans.reshape(1,-1)
            else:
                Yhat = np.dot(np.dot(x_scores, c_regrCoeff), \
                        np.transpose(y_loadings)) + Ymeans            
            self.calYpredList.append(Yhat)
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Collect all PRESSE for individual variables in a dictionary. 
        # Keys represent number of component.            
        self.PRESSEdict_indVar = {}
        
        # Compute PRESS for calibration / estimation
        PRESSE_0_indVar = np.sum(np.square(st.centre(self.arrY_input)), axis=0)
        self.PRESSEdict_indVar[0] = PRESSE_0_indVar
        
        # Compute PRESS for each Yhat for 1, 2, 3, etc number of components
        # and compute explained variance
        for ind, Yhat in enumerate(self.calYpredList):
            diffY = st.centre(self.arrY_input) - st.centre(Yhat)
            PRESSE_indVar = np.sum(np.square(diffY), axis=0)
            self.PRESSEdict_indVar[ind+1] = PRESSE_indVar
                    
        # Now store all PRESSE values into an array. Then compute MSEE and
        # RMSEE.
        self.PRESSEarr_indVar = np.array(list(self.PRESSEdict_indVar.values()))
        self.MSEEarr_indVar = self.PRESSEarr_indVar / \
                np.shape(self.arrY_input)[0]
        self.RMSEEarr_indVar = np.sqrt(self.MSEEarr_indVar)
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Compute explained variance for each variable in Y using the
        # MSEP for each variable. Also collect PRESSE, MSEE, RMSEE in 
        # their respective dictionaries for each variable. Keys represent 
        # now variables and NOT components as above with 
        # self.PRESSEdict_indVar
        self.cumCalExplVarYarr_indVar = np.zeros(np.shape(self.MSEEarr_indVar))
        MSEE_0_indVar = self.MSEEarr_indVar[0,:]
        
        for ind, MSEE_indVar in enumerate(self.MSEEarr_indVar):
            explVar = (MSEE_0_indVar - MSEE_indVar) / MSEE_0_indVar * 100
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
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Collect total PRESSE across all variables in a dictionary. Also,
        # compute total calibrated explained variance in Y.
        self.PRESSE_total_dict = {}
        self.PRESSE_total_list = np.sum(self.PRESSEarr_indVar, axis=1)
        
        for ind, PRESSE in enumerate(self.PRESSE_total_list):
            self.PRESSE_total_dict[ind] = PRESSE
        # ---------------------------------------------------------------------        
        
        
        # ---------------------------------------------------------------------
        # Collect total MSEE across all variables in a dictionary. Also,
        # compute total calibrated explained variance in Y.             
        self.MSEE_total_dict = {}
        self.MSEE_total_list = np.sum(self.MSEEarr_indVar, axis=1) / \
                np.shape(self.arrY_input)[1]
        MSEE_0 = self.MSEE_total_list[0]

        # Compute total calibrated explained variance in Y
        self.YcumCalExplVarList = []
        if self.Ystand == False:
            for ind, MSEE in enumerate(self.MSEE_total_list):
                perc = (MSEE_0 - MSEE) / MSEE_0 * 100
                self.MSEE_total_dict[ind] = MSEE
                self.YcumCalExplVarList.append(perc)
        else:
            self.YcumCalExplVarArr = np.average(self.cumCalExplVarYarr_indVar, axis=1)
            self.YcumCalExplVarList = list(self.YcumCalExplVarArr)
        
        # Construct list with total validated explained variance in Y
        self.YcalExplVarList = []
        for ind, item in enumerate(self.YcumCalExplVarList):
            if ind == len(self.YcumCalExplVarList)-1: break
            explVarComp = self.YcumCalExplVarList[ind+1] - \
                    self.YcumCalExplVarList[ind]
            self.YcalExplVarList.append(explVarComp)

        # Construct a dictionary that holds predicted Y (Yhat) from calibration
        # for each number of components.
        self.calYpredDict = {}
        for ind, item in enumerate(self.calYpredList):
            self.calYpredDict[ind+1] = item 
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Compute total RMSEP and store values in a dictionary and list.            
        self.RMSEE_total_dict = {}
        self.RMSEE_total_list = np.sqrt(self.MSEE_total_list)
        
        for ind, RMSEE in enumerate(self.RMSEE_total_list):
            self.RMSEE_total_dict[ind] = RMSEE
        # ---------------------------------------------------------------------
        
        
        
        
        # ========== COMPUTATIONS FOR X ==========
        # ---------------------------------------------------------------------
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
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Collect all PRESSE for individual variables in a dictionary. 
        # Keys represent number of component.            
        self.PRESSEdict_indVar_X = {}
        
        # Compute PRESS for calibration / estimation
        PRESSE_0_indVar_X = np.sum(np.square(st.centre(self.arrX_input)), axis=0)
        self.PRESSEdict_indVar_X[0] = PRESSE_0_indVar_X
        
        # Compute PRESS for each Xhat for 1, 2, 3, etc number of components
        # and compute explained variance
        for ind, Xhat in enumerate(self.calXpredList):
            diffX = st.centre(self.arrX_input) - st.centre(Xhat)
            PRESSE_indVar_X = np.sum(np.square(diffX), axis=0)
            self.PRESSEdict_indVar_X[ind+1] = PRESSE_indVar_X
                    
        # Now store all PRESSE values into an array. Then compute MSEE and
        # RMSEE.
        self.PRESSEarr_indVar_X = np.array(list(self.PRESSEdict_indVar_X.values()))
        self.MSEEarr_indVar_X = self.PRESSEarr_indVar_X / \
                np.shape(self.arrX_input)[0]
        self.RMSEEarr_indVar_X = np.sqrt(self.MSEEarr_indVar_X)
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Compute explained variance for each variable in X using the
        # MSEP for each variable. Also collect PRESSE, MSEE, RMSEE in 
        # their respective dictionaries for each variable. Keys represent 
        # now variables and NOT components as above with 
        # self.PRESSEdict_indVar_X
        self.cumCalExplVarXarr_indVar = np.zeros(np.shape(self.MSEEarr_indVar_X))
        MSEE_0_indVar_X = self.MSEEarr_indVar_X[0,:]
        
        for ind, MSEE_indVar_X in enumerate(self.MSEEarr_indVar_X):
            explVar = (MSEE_0_indVar_X - MSEE_indVar_X) / MSEE_0_indVar_X * 100
            self.cumCalExplVarXarr_indVar[ind] = explVar
                    
        self.PRESSE_indVar_X = {}
        self.MSEE_indVar_X = {}
        self.RMSEE_indVar_X = {}
        self.cumCalExplVarX_indVar = {}
        
        for ind in range(np.shape(self.PRESSEarr_indVar_X)[1]):
            self.PRESSE_indVar_X[ind] = self.PRESSEarr_indVar_X[:,ind]
            self.MSEE_indVar_X[ind] = self.MSEEarr_indVar_X[:,ind]
            self.RMSEE_indVar_X[ind] = self.RMSEEarr_indVar_X[:,ind]
            self.cumCalExplVarX_indVar[ind] = self.cumCalExplVarXarr_indVar[:,ind]
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Collect total PRESSE across all variables in a dictionary. Also,
        # compute total calibrated explained variance in Y.
        self.PRESSE_total_dict_X = {}
        self.PRESSE_total_list_X = np.sum(self.PRESSEarr_indVar_X, axis=1)
        
        for ind, PRESSE_X in enumerate(self.PRESSE_total_list_X):
            self.PRESSE_total_dict_X[ind] = PRESSE_X
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Collect total MSEE across all variables in a dictionary. Also,
        # compute total validated explained variance in X.             
        self.MSEE_total_dict_X = {}
        self.MSEE_total_list_X = np.sum(self.MSEEarr_indVar_X, axis=1) / \
                np.shape(self.arrX_input)[1]
        MSEE_0_X = self.MSEE_total_list_X[0]

        # Compute total calibrated explained variance in X
        self.XcumCalExplVarList = []
        if self.Xstand == False:
            for ind, MSEE_X in enumerate(self.MSEE_total_list_X):
                perc = (MSEE_0_X - MSEE_X) / MSEE_0_X * 100
                self.MSEE_total_dict_X[ind] = MSEE_X
                self.XcumCalExplVarList.append(perc)
        else:
            self.XcumCalExplVarArr = np.average(self.cumCalExplVarXarr_indVar, axis=1)
            self.XcumCalExplVarList = list(self.XcumCalExplVarArr)
        
        # Construct list with total validated explained variance in X
        self.XcalExplVarList = []
        for ind, item in enumerate(self.XcumCalExplVarList):
            if ind == len(self.XcumCalExplVarList)-1: break
            explVarComp = self.XcumCalExplVarList[ind+1] - \
                    self.XcumCalExplVarList[ind]
            self.XcalExplVarList.append(explVarComp)

        # Construct a dictionary that holds predicted X (Xhat) from calibration
        # for each number of components.
        self.calXpredDict = {}
        for ind, item in enumerate(self.calXpredList):
            self.calXpredDict[ind+1] = item 
        # ---------------------------------------------------------------------
        
        
        # ---------------------------------------------------------------------
        # Compute total RMSEE and store values in a dictionary and list.            
        self.RMSEE_total_dict_X = {}
        self.RMSEE_total_list_X = np.sqrt(self.MSEE_total_list_X)
        
        for ind, RMSEE_X in enumerate(self.RMSEE_total_list_X):
            self.RMSEE_total_dict_X[ind] = RMSEE_X
        # ---------------------------------------------------------------------

#==============================================================================
#         Here starts the cross validation process
#==============================================================================
        
        # Check whether cross validation is required by user. If required,
        # check what kind and build training and test sets thereafter.        
        if self.cvType == None:
            pass
            
        else:
            numObj = np.shape(self.arrY)[0]
            
            if self.cvType[0] == "loo":
                print("loo")
                cvComb = cv.LeaveOneOut(numObj)
            elif self.cvType[0] == "KFold":
                print("KFold")
                cvComb = cv.KFold(numObj, k=self.cvType[1])
            elif self.cvType[0] == "lolo":
                print("lolo")
                cvComb = cv.LeaveOneLabelOut(self.cvType[1])
            else:
                print('Requested form of cross validation is not available')
                pass
            
                        
            # Collect predicted y (i.e. yhat) for each CV segment in a  
            # dictionary according to nubmer of PC
            self.valYpredDict = {}
            for ind in range(1, self.numPC+1):
                self.valYpredDict[ind] = []
            
            # Collect predicted x (i.e. xhat) for each CV segment in a
            # dictionary according to number of PC
            self.valXpredDict = {}
            for ind in range(1, self.numPC+1):
                self.valXpredDict[ind] = []
            

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
                    # ---------------------------
                    t = np.dot(x_new, val_arrW[:,ind]).reshape(-1,1)
                    
                    # Module 8: Prediction STEP 2
                    # ---------------------------
                    p = val_arrP[:,ind].reshape(-1,1)                    
                    x_old = x_new
                    x_new = x_old - np.dot(t,np.transpose(p))
                    
                    # Generate a vector t that gets longer by one element with
                    # each PC
                    t_list.append(t)                   
                    t_arr = np.hstack(t_list)

                    # Give vector y_train_means the correct dimension in 
                    # numpy, so matrix multiplication will be possible
                    # i.e from dimension (x,) to (1,x)                    
                    ytm = y_train_means.reshape(1,-1)
                    xtm = x_train_means.reshape(1,-1)
                    
                    # Get relevant part of P, C anc Q for specific number of 
                    # PC's
                    part_val_arrP = val_arrP[:,0:ind+1]
                    part_val_arrQ = val_arrQ[:,0:ind+1]
                    part_val_arrC = val_arrC[0:ind+1,0:ind+1]
                    
                    # Module 8: Prediction STEP 3 
                    # ---------------------------                                       
                    # First compute yhat                    
                    if self.Ystand == True:
                        tCQ = np.dot(np.dot(t_arr,part_val_arrC), \
                                np.transpose(part_val_arrQ)) * \
                                y_train_std.reshape(1,-1)
                    else:
                        tCQ = np.dot(np.dot(t_arr,part_val_arrC), \
                                np.transpose(part_val_arrQ))
                    
                    yhat = ytm + tCQ
                    self.valYpredDict[ind+1].append(yhat)
                    
                    # Then compute xhat
                    if self.Xstand == True:
                        tP = np.dot(t_arr,np.transpose(part_val_arrP)) * \
                                x_train_std.reshape(1,-1)
                    else:
                        tP = np.dot(t_arr, np.transpose(part_val_arrP))
                    
                    xhat = xtm + tP
                    self.valXpredDict[ind+1].append(xhat)
                    
                        
            # Convert vectors from CV segments stored in lists into matrices 
            # for each PC            
            for key in self.valYpredDict:
                self.valYpredDict[key] = np.vstack(self.valYpredDict[key])
            
            for key in self.valXpredDict:
                self.valXpredDict[key] = np.vstack(self.valXpredDict[key])
            
            
            
            
            # ========== Computations for Y ==========
            # -----------------------------------------------------------------
            # Compute PRESSCV (PRediction Error Sum of Squares) for cross 
            # validation 
            self.valYpredList = list(self.valYpredDict.values())
            
            # Collect all PRESS in a dictionary. Keys represent number of 
            # component.            
            self.PRESSdict_indVar = {}
            
            # First compute PRESSCV for zero components
#            Y_cent = self.arrY_input - np.average(self.arrY_input, axis=0)
#            self.PRESSCV_0_indVar = np.sum(np.square(Y_cent), axis=0)            
            varY = np.var(self.arrY_input, axis=0, ddof=1)
            self.PRESSCV_0_indVar = (varY * np.square(np.shape(self.arrY_input)[0])) \
                    / (np.shape(self.arrY_input)[0])
            self.PRESSdict_indVar[0] = self.PRESSCV_0_indVar
            
            # Compute PRESSCV for each Yhat for 1, 2, 3, etc number of components
            # and compute explained variance
            for ind, Yhat in enumerate(self.valYpredList):
                diffY = st.centre(self.arrY_input) - st.centre(Yhat)
                PRESSCV_indVar = np.sum(np.square(diffY), axis=0)
                self.PRESSdict_indVar[ind+1] = PRESSCV_indVar
                        
            # Now store all PRESSCV values into an array. Then compute MSECV and
            # RMSECV.
            self.PRESSCVarr_indVar = np.array(list(self.PRESSdict_indVar.values()))
            self.MSECVarr_indVar = self.PRESSCVarr_indVar / \
                    np.shape(self.arrY_input)[0]
            self.RMSECVarr_indVar = np.sqrt(self.MSECVarr_indVar)
            # -----------------------------------------------------------------
            
            
            # -----------------------------------------------------------------
            # Compute explained variance for each variable in Y using the
            # MSEP for each variable. Also collect PRESS, MSECV, RMSECV in 
            # their respective dictionaries for each variable.  Keys represent 
            # now variables and NOT components as above with 
            # self.PRESSdict_indVar
            self.cumValExplVarYarr_indVar = np.zeros(np.shape(self.MSECVarr_indVar))
            MSECV_0_indVar = self.MSECVarr_indVar[0,:]
            
            for ind, MSECV_indVar in enumerate(self.MSECVarr_indVar):
                explVar = (MSECV_0_indVar - MSECV_indVar) / MSECV_0_indVar * 100
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
            # Collect total PRESSCV across all variables in a dictionary.
            self.PRESSCV_total_dict = {}
            self.PRESSCV_total_list = np.sum(self.PRESSCVarr_indVar, axis=1)
            
            for ind, PRESSCV in enumerate(self.PRESSCV_total_list):
                self.PRESSCV_total_dict[ind] = PRESSCV
            # -----------------------------------------------------------------
            
            
            # -----------------------------------------------------------------
            # Collect total MSECV across all variables in a dictionary. Also,
            # compute total validated explained variance in Y.             
            self.MSECV_total_dict = {}
            self.MSECV_total_list = np.sum(self.MSECVarr_indVar, axis=1) / \
                    np.shape(self.arrY_input)[1]
            MSECV_0 = self.MSECV_total_list[0]

            # Compute total validated explained variance in Y
            self.YcumValExplVarList = []
            if self.Ystand == False:
                for ind, MSECV in enumerate(self.MSECV_total_list):
                    perc = (MSECV_0 - MSECV) / MSECV_0 * 100
                    self.MSECV_total_dict[ind] = MSECV
                    self.YcumValExplVarList.append(perc)
            else:
                self.YcumValExplVarArr = np.average(self.cumValExplVarYarr_indVar, axis=1)
                self.YcumValExplVarList = list(self.YcumValExplVarArr)
            
            # Construct list with total validated explained variance in Y in
            # each component
            self.YvalExplVarList = []
            for ind, item in enumerate(self.YcumValExplVarList):
                if ind == len(self.YcumValExplVarList)-1: break
                explVarComp = self.YcumValExplVarList[ind+1] - \
                        self.YcumValExplVarList[ind]
                self.YvalExplVarList.append(explVarComp)
            # -----------------------------------------------------------------
            
            
            # -----------------------------------------------------------------
            # Compute total RMSECV and store values in a dictionary and list.            
            self.RMSECV_total_dict = {}
            self.RMSECV_total_list = np.sqrt(self.MSECV_total_list)
            
            for ind, RMSECV in enumerate(self.RMSECV_total_list):
                self.RMSECV_total_dict[ind] = RMSECV
            # -----------------------------------------------------------------
            
            



            # ========== Computations for X ==========
            # -----------------------------------------------------------------
            # Compute PRESSCV (PRediction Error Sum of Squares) for cross 
            # validation 
            self.valXpredList = self.valXpredDict.values()
            
            # Collect all PRESS in a dictionary. Keys represent number of 
            # component.            
            self.PRESSdict_indVar_X = {}
            
            # First compute PRESSCV for zero components            
            varX = np.var(self.arrX_input, axis=0, ddof=1)
            self.PRESSCV_0_indVar_X = (varX * np.square(np.shape(self.arrX_input)[0])) \
                    / (np.shape(self.arrX_input)[0])
            self.PRESSdict_indVar_X[0] = self.PRESSCV_0_indVar_X
            
            # Compute PRESSCV for each Yhat for 1, 2, 3, etc number of 
            # components and compute explained variance
            for ind, Xhat in enumerate(self.valXpredList):
                #diffX = self.arrX_input - Xhat
                diffX = st.centre(self.arrX_input) - st.centre(Xhat)
                PRESSCV_indVar_X = np.sum(np.square(diffX), axis=0)
                self.PRESSdict_indVar_X[ind+1] = PRESSCV_indVar_X
                        
            # Now store all PRESSCV values into an array. Then compute MSECV 
            # and RMSECV.
            self.PRESSCVarr_indVar_X = np.array(list(self.PRESSdict_indVar_X.values()))
            self.MSECVarr_indVar_X = self.PRESSCVarr_indVar_X / \
                    np.shape(self.arrX_input)[0]
            self.RMSECVarr_indVar_X = np.sqrt(self.MSECVarr_indVar_X)
            # -----------------------------------------------------------------
            
            
            # -----------------------------------------------------------------
            # Compute explained variance for each variable in X using the
            # MSEP for each variable. Also collect PRESS, MSECV, RMSECV in 
            # their respective dictionaries for each variable. Keys represent 
            # now variables and NOT components as above with 
            # self.PRESSdict_indVar
            self.cumValExplVarXarr_indVar = np.zeros(np.shape(self.MSECVarr_indVar_X))
            MSECV_0_indVar_X = self.MSECVarr_indVar_X[0,:]
            
            for ind, MSECV_indVar_X in enumerate(self.MSECVarr_indVar_X):
                explVar = (MSECV_0_indVar_X - MSECV_indVar_X) / MSECV_0_indVar_X * 100
                self.cumValExplVarXarr_indVar[ind] = explVar
                        
            self.PRESSCV_indVar_X = {}
            self.MSECV_indVar_X = {}
            self.RMSECV_indVar_X = {}
            self.cumValExplVarX_indVar = {}
            
            for ind in range(np.shape(self.PRESSCVarr_indVar_X)[1]):
                self.PRESSCV_indVar_X[ind] = self.PRESSCVarr_indVar_X[:,ind]
                self.MSECV_indVar_X[ind] = self.MSECVarr_indVar_X[:,ind]
                self.RMSECV_indVar_X[ind] = self.RMSECVarr_indVar_X[:,ind]
                self.cumValExplVarX_indVar[ind] = self.cumValExplVarXarr_indVar[:,ind]
            # -----------------------------------------------------------------
            
            
            # -----------------------------------------------------------------
            # Collect total PRESSCV across all variables in a dictionary.
            self.PRESSCV_total_dict_X = {}
            self.PRESSCV_total_list_X = np.sum(self.PRESSCVarr_indVar_X, axis=1)
            
            for ind, PRESSCV_X in enumerate(self.PRESSCV_total_list_X):
                self.PRESSCV_total_dict_X[ind] = PRESSCV_X
            # -----------------------------------------------------------------
            
            
            # -----------------------------------------------------------------
            # Collect total MSECV across all variables in a dictionary. Also,
            # compute total validated explained variance in X.             
            self.MSECV_total_dict_X = {}
            self.MSECV_total_list_X = np.sum(self.MSECVarr_indVar_X, axis=1) / \
                    np.shape(self.arrX_input)[1]
            MSECV_0_X = self.MSECV_total_list_X[0]

            # Compute total validated explained variance in X
            self.XcumValExplVarList = []
            if self.Xstand == False:
                for ind, MSECV_X in enumerate(self.MSECV_total_list_X):
                    perc = (MSECV_0_X - MSECV_X) / MSECV_0_X * 100
                    self.MSECV_total_dict_X[ind] = MSECV_X
                    self.XcumValExplVarList.append(perc)
            else:
                self.XcumValExplVarArr = np.average(self.cumValExplVarXarr_indVar, axis=1)
                self.XcumValExplVarList = list(self.XcumValExplVarArr)
            
            # Construct list with total validated explained variance in X in 
            # each component
            self.XvalExplVarList = []
            for ind, item in enumerate(self.XcumValExplVarList):
                if ind == len(self.XcumValExplVarList)-1: break
                explVarComp = self.XcumValExplVarList[ind+1] - \
                        self.XcumValExplVarList[ind]
                self.XvalExplVarList.append(explVarComp)
            # -----------------------------------------------------------------
            
            
            # -----------------------------------------------------------------
            # Compute total RMSECV and store values in a dictionary and list.            
            self.RMSECV_total_dict_X = {}
            self.RMSECV_total_list_X = np.sqrt(self.MSECV_total_list_X)
            
            for ind, RMSECV_X in enumerate(self.RMSECV_total_list_X):
                self.RMSECV_total_dict_X[ind] = RMSECV_X
            # -----------------------------------------------------------------
                            
    
    
    def modelSettings(self):
        """
        Returns a dictionary holding settings under which PLS2 was run.
        """
        self.settingsDict = {}
        self.settingsDict['numComp'] = self.numPC
        self.settingsDict['arrX'] = self.arrX_input
        self.settingsDict['arrY'] = self.arrY_input
        self.settingsDict['Xstand'] = self.Xstand
        self.settingsDict['Ystand'] = self.Ystand
        self.settingsDict['analysed X'] = self.arrX
        self.settingsDict['analysed Y'] = self.arrY
        self.settingsDict['cv type'] = self.cvType
        return self.settingsDict

    
    def X_means(self):
        """
        Returns a vector holding the column means of X. 
        """
        return np.average(self.arrX_input, axis=0).reshape(1,-1)    
    
    
    def X_scores(self):
        """
        Returns array holding scores of array X. First column holds scores 
        for component 1, second column holds scores for component 2, etc.
        """
        return self.arrT
    
    
    def X_loadings(self):
        """
        Returns array holding loadings of array X. Rows represent variables
        and columns represent components. First column holds loadings for 
        component 1, second column holds scores for component 2, etc.
        """
        return self.arrP
    
    
    def X_loadingsWeights(self):
        """
        Returns an array holding loadings weights of array X.
        """
        return self.arrW
    
    
    def X_corrLoadings(self):
        """
        Returns array holding correlation loadings of array X. First column 
        holds correlation loadings for component 1, second column holds 
        correlation loadings for component 2, etc.
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
    
    
    def X_residuals(self):
        """
        Returns a dictionary holding the residual arrays for array X after 
        each computed component. Dictionary key represents order of component.
        """
        # Create empty dictionary that will hold residuals
        X_residualsDict = {}
        
        # Fill dictionary with residuals arrays from residuals list
        for ind, item in enumerate(self.X_residualsList):
            X_residualsDict[ind] = item
        
        return X_residualsDict
    
    
    def X_calExplVar(self):
        """
        Returns a list holding the calibrated explained variance for 
        each component. First number in list is for component 1, second number 
        for component 2, etc.
        """
        return self.XcalExplVarList
    
    
    def X_cumCalExplVar_indVar(self):
        """
        Returns an array holding the cumulative calibrated explained variance
        for each variable in X after each component. First row represents zero
        components, second row represents one component, third row represents 
        two components, etc. Columns represent variables.
        """
        return self.cumCalExplVarXarr_indVar
    
    
    def X_cumCalExplVar(self):
        """
        Returns a list holding the cumulative calibrated explained variance 
        for array X after each component.
        """
        return self.XcumCalExplVarList
    
    
    def X_predCal(self):
        """
        Returns a dictionary holding the predicted arrays Xhat from 
        calibration after each computed component. Dictionary key represents 
        order of component.
        """
        return self.calXpredDict
    
    
    def X_PRESSE_indVar(self):
        """
        Returns array holding PRESSE for each individual variable in X
        acquired through calibration after each computed component. First row 
        is PRESSE for zero components, second row for component 1, third row 
        for component 2, etc.
        """
        return self.PRESSEarr_indVar_X
    
    
    def X_PRESSE(self):
        """
        Returns array holding PRESSE across all variables in X acquired  
        through calibration after each computed component. First row is PRESSE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.PRESSE_total_list_X
    
    
    def X_MSEE_indVar(self):
        """
        Returns an array holding MSEE for each variable in array X acquired 
        through calibration after each computed component. First row holds MSEE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """
        return self.MSEEarr_indVar_X
    
    
    def X_MSEE(self):
        """
        Returns an array holding MSEE across all variables in X acquired 
        through calibration after each computed component. First row is MSEE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.MSEE_total_list_X
    
    
    def X_RMSEE_indVar(self):
        """
        Returns an array holding RMSEE for each variable in array X acquired 
        through calibration after each component. First row holds RMSEE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """
        return self.RMSEEarr_indVar_X
    
    
    def X_RMSEE(self):
        """
        Returns an array holding RMSEE across all variables in X acquired 
        through calibration after each computed component. First row is RMSEE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.RMSEE_total_list_X
    
    
    def X_valExplVar(self):
        """
        Returns a list holding the validated explained variance for X after
        each component. First number in list is for component 1, second number 
        for component 2, third number for component 3, etc.
        """
        return self.XvalExplVarList
    
    
    def X_cumValExplVar_indVar(self):
        """
        Returns an array holding the cumulative validated explained variance
        for each variable in X after each component. First row represents 
        zero components, second row represents component 1, third row for 
        compnent 2, etc. Columns represent variables.
        """
        return self.cumValExplVarXarr_indVar
    
    
    def X_cumValExplVar(self):
        """
        Returns a list holding the cumulative validated explained variance 
        for array X after each component. First number represents zero 
        components, second number represents component 1, etc. 
        """
        return self.XcumValExplVarList
    
    
    def X_predVal(self):
        """
        Returns dictionary holding arrays of predicted Xhat after each 
        component from validation. Dictionary key represents order of 
        component.
        """
        return self.valXpredDict
    
    
    def X_PRESSCV_indVar(self):
        """
        Returns array holding PRESSCV for each individual variable in X 
        acquired through cross validation after each computed component. First 
        row is PRESSCV for zero components, second row for component 1, third 
        row for component 2, etc.
        """
        return self.PRESSCVarr_indVar_X
    
    
    def X_PRESSCV(self):
        """
        Returns an array holding PRESSCV across all variables in X acquired  
        through cross validation after each computed component. First row is 
        PRESSCV for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.PRESSCV_total_list_X
    
    
    def X_MSECV_indVar(self):
        """
        Returns an arrary holding MSECV for each variable in X acquired through  
        cross validation. First row is MSECV for zero components, second row 
        for component 1, etc.
        """
        return self.MSECVarr_indVar_X
    
    
    def X_MSECV(self):
        """
        Returns an array holding MSECV across all variables in X acquired 
        through cross validation after each computed component. First row is 
        MSECV for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.MSECV_total_list_X
    
    
    def X_RMSECV_indVar(self):
        """
        Returns an arrary holding RMSECV for each variable in X acquired 
        through cross validation after each computed component. First row is 
        RMSECV for zero components, second row for component 1, third row for 
        component 2, etc.
        """
        return self.RMSECVarr_indVar_X


    def X_RMSECV(self):
        """
        Returns an array holding RMSECV across all variables in X acquired 
        through cross validation after each computed component. First row is 
        RMSECV for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.RMSECV_total_list_X
    
    
    def X_scores_predict(self, Xnew, numComp=1):
        """
        Returns array of X scores from new X data using the exsisting model. 
        Rows represent objects and columns represent components.
        """        
        
        # First pre-process new X data accordingly
        if self.Xstand == True:
        
            x_new = (Xnew - np.average(self.arrX_input, axis=0)) / \
                    np.std(self.arrX_input, ddof=1)
        
        else:
            
            x_new = (Xnew - np.average(self.arrX_input, axis=0))
                
        
        # Get all necessary matrices from calibration
        t_list = []
        for ind in range(numComp):
            
            # Module 8: Prediction STEP 1
            # ---------------------------
            t = np.dot(x_new, self.arrW[:, ind]).reshape(-1, 1)
            
            # Module 8: Prediction STEP 2
            # ---------------------------
            p = self.arrP[:, ind].reshape(-1,1)                    
            x_old = x_new
            x_new = x_old - np.dot(t, np.transpose(p))
            
            # Generate a vector t that gets longer by one element with
            # each PC
            t_list.append(list(t)[0])                   
        
        return np.array(t_list)
    
    
    def scoresRegressionCoeffs(self):
        """
        Returns a one dimensional array holding regression coefficients between
        scores of array X and Y.
        """ 
        return self.arrC    
    
    
    def Y_means(self):
        """
        Returns a vector holding the column means of array Y. 
        """
        return np.average(self.arrY_input, axis=0).reshape(1,-1)
    
    
    def Y_scores(self):
        """
        Returns an array holding loadings C of array Y. Rows represent 
        variables and columns represent components. First column for 
        component 1, second columns for component 2, etc.
        """
        return self.arrU
    
    
    def Y_loadings(self):
        """
        Returns an array holding loadings C of array Y. Rows represent 
        variables and columns represent components. First column for 
        component 1, second columns for component 2, etc.
        """
        return self.arrQ
    
    
    def Y_corrLoadings(self):
        """
        Returns array holding correlation loadings of array X. First column 
        holds correlation loadings for component 1, second column holds 
        correlation loadings for component 2, etc.
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
    
    
    def Y_residuals(self):
        """
        Returns a dictionary holding residuals F of array Y after each 
        component. Dictionary key represents order of component.
        """
        # Create empty dictionary that will hold residuals
        Y_residualsDict = {}
        
        # Fill dictionary with residuals arrays from residuals list
        for ind, item in enumerate(self.Y_residualsList):
            Y_residualsDict[ind] = item
        
        return Y_residualsDict
    
    
    def Y_calExplVar(self):
        """
        Returns a list holding the calibrated explained variance for each
        component. First number in list is for component 1, second number for 
        component 2, etc.
        """
        return self.YcalExplVarList
    
    
    def Y_cumCalExplVar_indVar(self):
        """
        Returns an array holding the cumulative calibrated explained variance
        for each variable in Y after each component. First row represents zero
        components, second row represents one component, third row represents 
        two components, etc. Columns represent variables.
        """
        return self.cumCalExplVarYarr_indVar
    
    
    def Y_cumCalExplVar(self):
        """
        Returns a list holding the cumulative calibrated explained variance 
        for array X after each component. First number represents zero 
        components, second number represents component 1, etc.
        """
        return self.YcumCalExplVarList
        
    
    def Y_predCal(self):
        """
        Returns dictionary holding arrays of predicted Yhat after each 
        component from calibration. Dictionary key represents order of 
        components.
        """
        return self.calYpredDict
    
    def Y_PRESSE_indVar(self):
        """
        Returns array holding PRESSE for each individual variable in Y
        acquired through calibration after each component. First row is 
        PRESSE for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.PRESSEarr_indVar
    
    
    def Y_PRESSE(self):
        """
        Returns array holding PRESSE across all variables in Y acquired  
        through calibration after each computed component. First row is PRESSE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.PRESSE_total_list
    
    
    def Y_MSEE_indVar(self):
        """
        Returns an array holding MSEE for each variable in array Y acquired 
        through calibration after each computed component. First row holds MSEE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.MSEEarr_indVar
    
    
    def Y_MSEE(self):
        """
        Returns an array holding MSEE across all variables in Y acquired 
        through calibration after each computed component. First row is MSEE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.MSEE_total_list
    
    
    def Y_RMSEE_indVar(self):
        """
        Returns an array holding RMSEE for each variable in array Y acquired 
        through calibration after each component. First row holds RMSEE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.RMSEEarr_indVar
    
    
    def Y_RMSEE(self):
        """
        Returns an array holding RMSEE across all variables in Y acquired 
        through calibration after each computed component. First row is RMSEE 
        for zero components, second row for component 1, third row for 
        component 2, etc.
        """   
        return self.RMSEE_total_list
    
    
    def Y_valExplVar(self):
        """
        Returns a list holding the validated explained variance for Y after
        each component. First number in list is for component 1, second number 
        for component 2, third number for component 3, etc.
        """
        return  self.YvalExplVarList
    
    
    def Y_cumValExplVar_indVar(self):
        """
        Returns an array holding the cumulative validated explained variance
        for each variable in Y after each component. First row represents 
        zero components, second row represents component 1, third row for 
        compnent 2, etc. Columns represent variables.
        """
        return self.cumValExplVarYarr_indVar
    
    
    def Y_cumValExplVar(self):
        """
        Returns a list holding the cumulative validated explained variance 
        for array X after each component. First number represents zero 
        components, second number represents component 1, etc.
        """
        return self.YcumValExplVarList
    
    
    def Y_predVal(self):
        """
        Returns dictionary holding arrays of predicted Yhat after each 
        component from validation. Dictionary key represents order of 
        component.
        """
        return self.valYpredDict
    
    
    def Y_PRESSCV_indVar(self):
        """
        Returns an array holding PRESSCV of each variable in array Y acquired 
        through cross validation after each computed component. First row is 
        PRESSCV for zero components, second row component 1, third row for 
        component 2, etc.
        """   
        return self.PRESSCVarr_indVar
    
    
    def Y_PRESSCV(self):
        """
        Returns an array holding PRESSCV across all variables in Y acquired  
        through cross validation after each computed component. First row is 
        PRESSCV for zero components, second row component 1, third row for 
        component 2, etc.
        """   
        return self.PRESSCV_total_list
    
    
    def Y_MSECV_indVar(self):
        """
        Returns an array holding MSECV of each variable in array Y acquired 
        through cross validation after each computed component. First row is 
        MSECV for zero components, second row component 1, third row for 
        component 2, etc.
        """   
        return self.MSECVarr_indVar
    
    
    def Y_MSECV(self):
        """
        Returns an array holding MSECV across all variables in Y acquired  
        through cross validation after each computed component. First row is 
        MSECV for zero components, second row component 1, third row for 
        component 2, etc.
        """   
        return self.MSECV_total_list
    
    
    def Y_RMSECV_indVar(self):
        """
        Returns an array holding RMSECV for each variable in array Y acquired 
        through cross validation after each computed component. First row is 
        RMSECV for zero components, second row component 1, third row for 
        component 2, etc.
        """   
        return self.RMSECVarr_indVar
    
    
    def Y_RMSECV(self):
        """
        Returns an array holding RMSECV across all variables in Y acquired 
        through cross validation after each computed component. First row is 
        RMSECV for zero components, second row component 1, third row for 
        component 2, etc.
        """   
        return self.RMSECV_total_list


    def Y_predict(self, Xnew, numComp=1):
        """
        Return predicted Yhat from new measurements X. 
        """        
        pred_Y_list = []
        for rowInd in range(np.shape(Xnew)[0]):
            print('Object', rowInd)
        
            # First pre-process new X data accordingly
            if self.Xstand == True:
            
                x_new = (Xnew[rowInd, :] - np.average(self.arrX_input, axis=0)) / \
                        np.std(self.arrX_input, ddof=1)
            
            else:
                
                x_new = (Xnew[rowInd, :] - np.average(self.arrX_input, axis=0))
        
            # Get all necessary matrices from calibration
            t_list = []
            for ind in range(numComp):
                
                # Module 8: Prediction STEP 1
                # ---------------------------
                t = np.dot(x_new, self.arrW[:, ind]).reshape(-1, 1)
                
                # Module 8: Prediction STEP 2
                # ---------------------------
                p = self.arrP[:, ind].reshape(-1,1)
                x_old = x_new
                x_new = x_old - np.dot(t, np.transpose(p))
                
                # Generate a vector t that gets longer by one element with
                # each PC
                t_list.append(list(t)[0])                   
                t_vec = np.transpose(np.array(t_list))
    
                # Give vector y_train_means the correct dimension in 
                # numpy, so matrix multiplication will be possible
                # i.e from dimension (x,) to (1,x)                    
                ytm = np.average(self.arrY_input, axis=0).reshape(1,-1)
                
                # Get relevant part of P, C anc Q for specific number of 
                # PC's
                part_arrQ = self.arrQ[:, 0:ind+1]
                part_arrC = self.arrC[0:ind+1, 0:ind+1]
                
                # Module 8: Prediction STEP 3 
                # ---------------------------                                       
                # First compute yhat                    
                if self.Ystand == True:
                    tCQ = np.dot(np.dot(t_vec, part_arrC), \
                            np.transpose(part_arrQ)) * \
                            np.std(self.arrY, ddof=1).reshape(1,-1)
                else:
                    tCQ = np.dot(np.dot(t_vec, part_arrC), \
                            np.transpose(part_arrQ))
                
                yhat = ytm + tCQ
            
            pred_Y_list.append(yhat)
        
        return np.vstack(pred_Y_list)
            
    
    def cvTrainAndTestData(self):
        """
        Returns a list consisting of dictionaries holding training and test 
        sets.
        """
        return self.cvTrainAndTestDataList


    def corrLoadingsEllipses(self):
        """
        Returns the coordinates of ellipses that represent 50% and 100% expl. 
        variance in correlation loadings plot.
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