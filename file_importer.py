# -*- coding: utf-8 -*-

# Scipy imports
from numpy import array, loadtxt


class FileImporter:
    """Class for for dataimport from files.

    First from tab separated text files.
    """

    def __init__(self, fileUri, haveVarNames = True, haveObjNames = False):
        """Try to read and parse file from given filepath"""
        self._fileUri = fileUri
        self._haveVarNames = haveVarNames
        self._haveObjNames = haveObjNames
        self._dataset = array([], ndmin=2)
        self._variableNames = []
        self._objectNames = []


    def readFile(self):
        if self._haveObjNames:
            self._readMatrixWithObjNames()
        else:
            # FIXME: May fail if file not foud
            # No, supose to fail if file not found
            skips = 0
            if self._haveVarNames:
                skips = 1
                self._readVarNames()
            # FIXME: Except open file error and dataformat error
            self._dataset = loadtxt(
                fname = self._fileUri,
                delimiter = "\t",
                skiprows = skips
                )



    def _probeFile(self):
        """Try to find formating of unknown file"""
        pass



    def _readVarNames(self):
        """Read Matrix column header from text file"""
        # Open file and read headers
        fp = open(self._fileUri, 'rU')
        line = fp.readline()
        fp.close()
        # Remove newline char
        line = line.rstrip()
        self._variableNames = line.split('\t')



    def _readMatrixWithObjNames(self):
        """
        This function reads data from text files. First row are
        variable names and first row are object names.

        INPUT:
        <fileName>: type string
        """

        # File is opened using name that is given by
        # the file-open dialog in the main file.
        dataFile = open(self._fileUri, 'r')

        # All the data is read into a list.
        # FIXME: Prefer to operate on line by line basis to save memory.
        allText = dataFile.readlines()

        # Initiate lists that will hold variable names, object names
        # and data.
        data = []


        # Loop through allText and extract variable names, object names and
        # data.
        for ind, row in enumerate(allText):

            # Get variable names from first row
            if ind == 0:
                firstRowList = row.split('\t')
                firstRowList[-1] = firstRowList[-1].rstrip()
                self._variableNames = firstRowList[1:]

            # Split remaining rows into object names and data
            else:
                rowObjectsList = row.split('\t')
                self._objectNames.append(rowObjectsList[0])
                rowObjectsList.pop(0)

                # Convert strings into floats
                floatList = []
                for item in rowObjectsList:
                    floatList.append(float(item))

                data.append(floatList)

        # Make variable names, object names and data available as
        # class variables.
        self._dataset = array(data)



    def _parseFile(self):
        """Open and manually parse file line by line"""
        pass


    def getMatrix(self):
        """Return imported matrix as ndarray"""
        return self._dataset


    def getVariableNames(self):
        """Return list of column headers as list"""
        return self._variableNames


    def getObjectNames(self):
        return self._objectNames

