# -*- coding: utf-8 -*-
"""
statTools.py

Info: A collection of tools for data analysis

Author: Oliver Tomic

Date: 20.06.2009
"""
import numpy

def RVcoeff(dataList):
    """
    This function computes the Rv coefficients between two matrices at the
    time. The results are stored in a matrix described as 'between cosine
    matrix' and is labled C.

    REF: H. Abdi, D. Valentin; 'The STATIS method' (unofficial paper)

    <dataList>: type list holding rectangular matrices (no need for equal dim)
    """

    # First centre matrices column-wise
    centArrList = []
    for arr in dataList:
        colMeans = numpy.mean(arr, axis=0)
        centArr = arr - colMeans
        centArrList.append(centArr)

    # First compute the scalar product matrices for each data set X
    scalArrList = []

    for arr in centArrList:
        scalArr = numpy.dot(arr, numpy.transpose(arr))
        scalArrList.append(scalArr)


    # Now compute the 'between study cosine matrix' C
    C = numpy.zeros((len(dataList), len(dataList)), float)


    for index, element in numpy.ndenumerate(C):
        nom = numpy.trace(numpy.dot(numpy.transpose(scalArrList[index[0]]), \
            scalArrList[index[1]]))
        denom1 = numpy.trace(numpy.dot(numpy.transpose(scalArrList[index[0]]), \
            scalArrList[index[0]]))
        denom2 = numpy.trace(numpy.dot(numpy.transpose(scalArrList[index[1]]), \
            scalArrList[index[1]]))
        Rv = nom / numpy.sqrt(denom1 * denom2)
        C[index[0], index[1]] = Rv

    return C




def ortho(arr1, arr2):
    """
    This function orthogonalises arr1 with respect to arr2. The function then
    returns orthogonalised array arr1_orth.
    """

    # Find number of rows, such that identity matrix I can be created
    numberRows = numpy.shape(arr1)[0]
    I = numpy.identity(numberRows, float)

    # Compute transpose of arr1
    arr2_T = numpy.transpose(arr2)

    term1 = numpy.linalg.inv(numpy.dot(arr2_T, arr2))
    term2 = numpy.dot(arr2, term1)
    term3 = numpy.dot(term2, arr2_T)
    arr1_orth = numpy.dot((I - term3), arr1)

    return arr1_orth



def centre(Y):
    """
    This function centers an array column-wise.
    """

    # First make a copy of input matrix and make it a matrix with float
    # elements
    X = numpy.array(Y, float)
    numberOfObjects, numberOfVariables = numpy.shape(X)
    variableMean = numpy.average(X, 0)


    # Now center and divide by standard deviation
    for row in range(0, numberOfObjects):
        X[row] = X[row] - variableMean

    return X



def STD(Y, selection):
    """
    This function standardises the input array either
    column-wise (selection = 0) or row-wise (selection = 1).
    """
    # First make a copy of input array
    #X = array(Y, float)
    X = Y.copy()
    numberOfObjects, numberOfVariables = numpy.shape(X)
    colMeans = numpy.mean(X, axis=0)
    colSTD = numpy.std(X, axis=0, ddof=1)


    # Standardisation column-wise
    if selection == 0:
        centX = X - colMeans
        stdX = centX / colSTD


    # Standardisation of row-wise
    # Transpose array first, such that broadcasting procedure works easier.
    # After standardisation transpose back to get final array.
    if selection == 1:
        transX = numpy.transpose(X)
        transColMeans = numpy.mean(transX, axis=0)
        transColSTD = numpy.std(transX, axis=0, ddof=1)

        centTransX = transX - transColMeans
        stdTransX = centTransX / transColSTD
        stdX = numpy.transpose(stdTransX)


    return stdX



class arrayIO:
    def __init__(self, fileName):
        """
        This class reads data from text files. First row are variable names
        and first row are object names.

        INPUT:
        <fileName>: type string
        """

        # File is opened using name that is given by
        # the file-open dialog in the main file.
        dataFile = open(fileName, 'r')


        # All the data is read into a list.
        allText = dataFile.readlines()


        # Initiate lists that will hold variable names, object names and data.
        varNames = []
        objNames = []
        data = []


        # Loop through allText and extract variable names, object names and
        # data.
        for ind, row in enumerate(allText):

            # Get variable names from first row
            if ind == 0:
                firstRowList = row.split('\t')
                firstRowList[-1] = firstRowList[-1].rstrip()
                varNames = firstRowList[1:]

            # Split remaining rows into object names and data
            else:
                rowObjectsList = row.split('\t')
                objNames.append(rowObjectsList[0])
                rowObjectsList.pop(0)

                # Convert strings into floats
                floatList = []
                for item in rowObjectsList:
                    floatList.append(float(item))

                data.append(floatList)


        # Make variable names, object names and data available as
        # class variables.
        self.varNames = varNames[:]
        self.objNames = objNames[:]
        self.data = numpy.array(data)
