# coding=utf-8

# stdlib imports
import logging

# Enthought traits imports
from enthought.traits.api import \
    HasTraits, Dict, Str, ListStr, Int, List, Event, \
    Bool, Property, cached_property, on_trait_change, property_depends_on

# Local imports
from ds import DataSet


class DatasetCollection(HasTraits):
    """ Application wide collection of datasets
    """

    # Dictionary to hold dataset and a editor to select dataset
    _dataDict = Dict(Str, DataSet)

    # Events for dataset namechanges
    datasetNameChanged = Event

    # Dataset index list
    indexNameList = Property()


    def retriveDatasetByName(self, internalName):
        """Return DataSet object specified by internal name"""
        return self._dataDict[internalName]


    def addDataset(self, dataSet):
        """Add or update dataset"""
        name = dataSet._internalName
        if self._dataDict.__contains__(name):
            raise Exception("Key (%s) already exists", name)
        self._dataDict[name] = dataSet
        self.datasetNameChanged = True
        logging.info("addDataset: %s", name)


    def deleteDataset(self, internalName):
        """Remove dataset from collection"""
        del self._dataDict[internalName]
        self.datasetNameChanged = True
        logging.info("deleteDataset: %s", internalName)


    def _get_indexNameList(self):
        indexList = []
        for sn, so in self._dataDict.iteritems():
            tu = (sn, so._displayName)
            indexList.append(tu)
        return indexList


    @on_trait_change('_dataDict:_internalName')
    def dictNameChanged(self, object, name, old, new):
        """Update dictionary name"""
        toMove = self._dataDict.pop(old)
        self.addDataset(toMove)
        self.datasetNameChanged = True
        logging.info("dictNameChange: %s change from %s to %s", name, old, new)


    @on_trait_change('_dataDict:_displayName')
    def displayNameChanged(self, object, name, old, new):
        self.datasetNameChanged = True
        logging.info("displayNameChange: %s changed from %s to %s", name, old, new)
