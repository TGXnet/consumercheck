# -*- coding: utf-8 -*-
"""
Created on Apr 19 14:45:17 2012

@author: oliver.tomic

@purpose:
Run Conjoint class.
 - uses Alexandra's R package MixMod
 - accessed via pyper
"""

# Import necessary modules
import conjoint_one as cj
import statTools as st


#==============================================================================
# Load data that will be used in conjoint function (God Morgen TINE)
#==============================================================================

# Consumer attributes
consAttr = st.arrayIO('datasets/Conjoint/consumerAttributes.txt')

# Three different types of liking
odflLike = st.arrayIO('datasets/Conjoint/odour-flavour_liking.txt')
consistencyLike = st.arrayIO('datasets/Conjoint/consistency_liking.txt')
overallLike = st.arrayIO('datasets/Conjoint/overall_liking.txt')

# Design
designVar = st.arrayIO('datasets/Conjoint/design.txt')


#==============================================================================
# Simulate selected settings from conjoint GUI
#==============================================================================

# From radio button box choose model structure (possible choices are 1, 2 or 3)
selected_structure = 2

# From check box list submit selected consumer attributes.
# They are found in consAtt.varNames
#selected_consAttr = ['Sex', 'Age']
selected_consAttr = ['Sex']

# From check box list submit selected design variables. 
# They are found in design.varNames
selected_designVar = ['Flavour', 'Sugarlevel']

# From check box list submit selected consumer liking data sets
selected_consLiking = [odflLike, consistencyLike, overallLike]
selected_consLiking_tags = ['odourflavour', 'consistency', 'overall']



#==============================================================================
# Submit settings to conjoint class
#==============================================================================

# Temporary used consumer liking
consLiking = odflLike
consLikingTag = 'odourflavour'

# Call conjoint class in Python to do analysis
conjMod = cj.RConjoint(selected_structure, \
                       consAttr, selected_consAttr, \
                       designVar, selected_designVar, \
                       consLiking, consLikingTag)


finalDataArr = conjMod.inputData()

randomTable = conjMod.randomTable()
anovaTable = conjMod.anovaTable()
lsmeansTable = conjMod.lsmeansTable()
lsmeansDiffTable = conjMod.lsmeansDiffTable()
residualsTable = conjMod.residualsTable()
infoDict = conjMod.infoDict()
