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

class TestDatasetModel(unittest.TestCase):

	def setUp(self):
		self.testSet = DataSet()


	def testImport(self):
		path = findApplicationBasePath() + '/testdata/test.txt'
		self.testSet.importDataset(path, True)
		self.assertEqual('test', self.testSet._displayName)
		self.assertEqual(11, self.testSet.nRows)
		self.assertEqual(5, self.testSet.nCols)
		self.testSet.configure_traits(view=ds_list_tab)



if __name__ == '__main__':
	import os
	import sys

	# path for local imports
	setConsumerCheckIncludePath()
	from ds_ui import DataSet, ds_list_tab

	unittest.main()
