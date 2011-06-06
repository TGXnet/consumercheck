
def setConsumerCheckIncludePath():
    consumerBase = findApplicationBasePath();
    addLoadPath(consumerBase)


def findApplicationBasePath():
    basePath = os.getcwd()
    while os.path.basename(basePath) != 'tests':
        basePath = os.path.dirname(basePath)
    basePath = os.path.dirname(basePath)
    return basePath


def addLoadPath(baseFolderPath):
    sys.path.append(baseFolderPath)


import unittest

class TestDatasetModel(unittest.TestCase):

    def setUp(self):
        # Create some data
        numpts = 10
        self.x = range(numpts)
        self.y = [sqrt(xel)*10 for xel in self.x]
        self.labels = []
        for i in xrange(numpts):
            self.labels.append("Test{0}".format(i))


    def testImport(self):
        plot = PlotLine(
            ttext = 'PCA explained variance',
            titleX = '# of principal components',
            titleY = 'Explainded variance [%]',
            valPtLabel = self.labels,
            valX = self.x,
            valY = self.y,
            limY = (0, 100),
            limX = (-2, 15),
            )
        ui = plot.configure_traits()


if __name__ == '__main__':
    import os
    import sys
    from math import sqrt
    from numpy import array, ndarray, zeros, sort
    from numpy.random import random

    # path for local imports
    setConsumerCheckIncludePath()
    from plot_line import PlotLine

    unittest.main()
