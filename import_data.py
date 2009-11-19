# coding=utf-8

# Scipy imports
from numpy import array, loadtxt


class FileData:
    """Class for for dataimport from files.

    First from tab separated text files.
    """

    def __init__(self, fileUri, colHead = True):
        """Try to read and parse file from given filepath"""
        self._fileUri = fileUri
        # FIXME: May fail if file not foud
        skips = 0
        if colHead:
            skips = 1
            self._readColumnHeader()
        else:
            self._columnHeader = []
        # FIXME: Except open file error and dataformat error
        self._dataset = loadtxt(fname=self._fileUri, delimiter="\t", skiprows=skips)


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


    def _parseFile(self):
        """Open and mannualy parse file line by line"""
        pass


    def getMatrix(self):
        """Return imported matrix as ndarray"""
        return self._dataset


    def getColumnHeader(self):
        """Return list of column headers as list"""
        return self._columnHeader



# Application entry point.
if __name__ == "__main__":
    # import sys
    readTest = FileData('./Ost.txt')
    headers = readTest.getColumnHeader()
    matrix = readTest.getMatrix()
    print len(headers)
    print matrix.shape


#### EOF ######################################################################
