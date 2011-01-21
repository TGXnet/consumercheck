# -*- coding: utf-8 -*-

import unittest
import test_tools

# ConsumerCheck imports
from file_importer import FileImporter


class TestReadDataFile(unittest.TestCase):

	def setUp(self):
		self.testDir = test_tools.findApplicationBasePath() + '/testdata/'

	def tearDown(self):
		pass

	def testReadSimpleDatafile(self):
		readTest = FileImporter(self.testDir + 'test.txt', False, False)
		readTest.readFile()
		matrix = readTest.getMatrix()
		nRows, nCols = matrix.shape
		self.assertEqual(nRows, 12)
		self.assertEqual(nCols, 5)

	def testReadVarnameDatafile(self):
		readTest = FileImporter(self.testDir + 'Ost.txt', True, False)
		readTest.readFile()
		matrix = readTest.getMatrix()
		nRows, nCols = matrix.shape
		self.assertEqual(nRows, 336)
		self.assertEqual(nCols, 20)
		varNames = readTest.getVariableNames()
		nVarName = len(varNames)
		self.assertEqual(nVarName, nCols)

	def testReadVarnameObjecnameDatafile(self):
		readTest = FileImporter(self.testDir + 'C_lables.txt', True, True)
		readTest.readFile()
		matrix = readTest.getMatrix()
		nRows, nCols = matrix.shape
		self.assertEqual(nRows, 21)
		self.assertEqual(nCols, 3)
		varNames = readTest.getVariableNames()
		nVarName = len(varNames)
		self.assertEqual(nVarName, nCols)
		objNames = readTest.getObjectNames()
		nObjNames = len(objNames)
		self.assertEqual(nObjNames, nRows)


if __name__ == '__main__':
	unittest.main()
