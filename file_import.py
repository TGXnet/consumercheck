# -*- coding: utf-8 -*-

# Scipy imports
from numpy import array, loadtxt


class FileData:
    """Class for for dataimport from files.

    First from tab separated text files.
    """

    def __init__(self, fileUri, colHead = True, objName = False):
        """Try to read and parse file from given filepath"""
        self._fileUri = fileUri
        if objName:
            self._readObjNames()
        else:
            # FIXME: May fail if file not foud
            skips = 0
            if colHead:
                skips = 1
                self._readColumnHeader()
            else:
                self._columnHeader = []
            # FIXME: Except open file error and dataformat error
            self._dataset = loadtxt(
                fname=self._fileUri,
                delimiter="\t",
                skiprows=skips
                )


    def _fileProbe(self):
        """Try to find formating of unknown file"""
        pass


    def _readColumnHeader(self, lineNumber=1):
        """Read Matrix column header from text file"""
        # Open file and read headers
        fp = open(self._fileUri, 'rU')
        line = fp.readline()
        # Remove newline char
        line = line.rstrip()
        self._columnHeader = line.split('\t')
        fp.close()


    def _readObjNames(self):
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
        # Variable names
        self._columnHeader = varNames[:]
        # Object names
        self._rowNames = objNames[:]
        self._dataset = array(data)



    def _parseFile(self):
        """Open and manually parse file line by line"""
        pass


    def getMatrix(self):
        """Return imported matrix as ndarray"""
        return self._dataset


    def getColumnHeader(self):
        """Return list of column headers as list"""
        return self._columnHeader

#end FileData
