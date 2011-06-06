
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
        self.x = sort(random(numpts))
        self.y = random(numpts)
        self.labels = []
        for i in xrange(numpts):
            self.labels.append("Test{0}".format(i))


    def testImport(self):
        plot = PlotScatter(
            ttext='PCA plot',
            titleX = 'PC1',
            titleY = 'PC2',
            valPtLabel = self.labels,
            valX=self.x,
            valY=self.y
            )
        ui = plot.configure_traits()


if __name__ == '__main__':
    import os
    import sys
    from numpy import array, ndarray, zeros, sort
    from numpy.random import random

    # path for local imports
    setConsumerCheckIncludePath()
    from plot_scatter import PlotScatter

    unittest.main()
