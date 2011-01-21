# -*- coding: utf-8 -*-

import unittest
import test_tools

# ConsumerCheck imports
from dataset_collection import DatasetCollection
from dataset import DataSet


class TestDatasetCollection(unittest.TestCase):

	def setUp(self):
		self.testSetsCollection = DatasetCollection()
		self.keyNames = ['ts2', 'ts1']
		self.dispNames = ['DisplayName for ts2', 'DisplayName for ts1']

	def testAddTwoSets(self):
		self._initAndAddTwoUniqueDataset()
		self.assertEquals(self.keyNames, self._getKeyNames())
		self.assertEquals(self.dispNames, self._getDispNames())
		dupDataSet = DataSet(_internalName='ts2', _displayName='Failed duplicate')
		self.assertRaises(Exception, self.testSetsCollection.addDataset, dupDataSet)

	def testChangeNames(self):
		testSet = self._addDummyDataset('ts')
		self.assertEquals(['ts'], self._getKeyNames() )
		testSet._internalName = 'newname'
		self.assertEquals(['newname'], self._getKeyNames() )

	def testNameLists(self):
		self._addDummyDataset('ts')
		self.assertEquals(['ts'], self._getKeyNames() )
		self.assertEquals(['DisplayName for ts'], self._getDispNames() )

	def testRemoveDataset(self):
		self._initAndAddTwoUniqueDataset()
		self.assertEquals(['ts2', 'ts1'], self._getKeyNames() )
		self.testSetsCollection.deleteDataset('ts1')
		self.assertEquals(['ts2'], self._getKeyNames() )
		self.testSetsCollection.deleteDataset('ts2')
		self.assertEquals([], self._getKeyNames() )
		self.assertRaises(KeyError, self.testSetsCollection.deleteDataset, 'nonExixtingKey')

	def _initAndAddTwoUniqueDataset(self):
		self._addDummyDataset('ts1')
		self._addDummyDataset('ts2')

	def _addDummyDataset(self, internalName):
		testSet = DataSet(_internalName=internalName, _displayName='DisplayName for ' + internalName)
		self.testSetsCollection.addDataset(testSet)
		return testSet

	def _getKeyNames(self):
		keys = []
		for kname, dname in self.testSetsCollection.indexNameList:
			keys.append(kname)
		return keys

	def _getDispNames(self):
		disp = []
		for kname, dname in self.testSetsCollection.indexNameList:
			disp.append(dname)
		return disp


if __name__ == '__main__':
	unittest.main()
