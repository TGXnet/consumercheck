"""
Function to manipulate path variable for R.
Created on Fri Sep 24 12:02:52 2010

@author: Thomas Graff
"""

import os, sys

def set_rpy_env():
    Rver = 'R-2.11.1'
    execPath = os.path.dirname(sys.argv[0])
    absExecPath = os.path.abspath(execPath)
    RHOME = os.path.join(absExecPath, Rver)

    #Manipulate path env var
    paths = os.environ["PATH"]
    pathList = paths.split(';')
    localRpath = os.path.join(RHOME, 'bin')

    i = 0
    foundRhome = False
    for spath in pathList:
        if spath.find('R-') > 0:
            foundRhome = True
            pathList[i] = localRpath
        i = i + 1
    if not foundRhome:
        pathList.append(localRpath)
    newPaths = ";".join(pathList)
    os.environ["PATH"] = newPaths
