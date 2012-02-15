
# Stdlib imports
import pytest

# Local imports
import statTools as st
from mvr import plsr


# Load data in numpy arrays
arr1 = st.arrayIO('../datasets/Ost_forbruker.txt')
arr2 = st.arrayIO('../datasets/Ost_sensorikk.txt')

# Select what should be X and Y
case = 1

# arr1 = X and arr2 = Y
if case == 1:
    # List of object names    
    objNL = arr1.objNames    
    
    # Access list of variable names in X and its data   
    xVL = arr1.varNames
    xData = arr1.data
    
    # Access list of variable names in Y and its data
    yVL = arr2.varNames
    yData = arr2.data

# Run regression analysis.
model = plsr(xData, yData, centre="yes", fncomp=5, fmethod="oscorespls", fvalidation="LOO")
