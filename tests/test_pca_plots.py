# -*- coding: utf-8 -*-

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
import os
import sys

class TestPlotPca(unittest.TestCase):
	def setUp(self):
		self.ds1 = DataSet()
		self.ds1.importDataset('../testdata/Ost.txt')
		self.ds2 = DataSet()
		self.ds2.importDataset('../testdata/Polser.txt', True, True)
		self.dsl = DatasetCollection()
		self.dsl.addDataset(self.ds1)
		self.dsl.addDataset(self.ds2)
		self.pca_plotter = PCAPlotFactory()
		self.show = True

	def test1PlotOverview(self):
		self.pca_plotter.plot_overview(self.dsl, self.show)

	def test2PlotScores(self):
		self.pca_plotter.plot_scores(self.ds1, self.show)

	def test3PlotLoadings(self):
		self.pca_plotter.plot_loadings(self.ds1, self.show)

	def test4PlotCorrLoad(self):
		self.pca_plotter.plot_corr_loading(self.ds1, self.show)

	def test5PlotExplVar(self):
		self.pca_plotter.plot_expl_var(self.ds1, self.show)

if __name__ == '__main__':
	# path for local imports
	setConsumerCheckIncludePath()
	from dataset import DataSet
	from dataset_collection import DatasetCollection
	from pca_plots import PCAPlotFactory
	unittest.main()
