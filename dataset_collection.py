"""Datasets container

Dictionary to hold all datasets.
Datasets can be imported or genrated.

"""
# stdlib imports
import logging

# Enthought traits imports
from enthought.traits.api import \
    HasTraits, Dict, Str, List, Event, \
    Bool, Property, on_trait_change, property_depends_on

# Local imports
from dataset import DataSet

class DatasetCollection(HasTraits):
    """ Application wide collection of datasets

	Members
	=======
	  * dataDict
	  * indexNameList

    Description
	===========
	Collection of all the data in the application.

    """
    # Dictionary to hold dataset and a editor to select dataset
    _dataDict = Dict(Str, DataSet)

    # Events for dataset namechanges
    datasetNameChanged = Event

    # Events for dictionari content change
    dataDictContentChanged = Event

    # Dataset index list
    indexNameList = Property()

    # indexNameList = Property( depends_on = '_dataDict' )

    def retriveDatasetByName(self, internalName):
        """Return DataSet object specified by internal name"""
        return self._dataDict[internalName]


    def retriveDatasetByDisplayName(self, name):
        """Return DataSet object by display name"""
        # FIXME: This is dirty
        for do in self._dataDict.itervalues():
            if do.isEqDisplayName(name):
                return do


    def addDataset(self, dataSet):
        """Add or update dataset"""
        name = dataSet._internalName
        if self._dataDict.__contains__(name):
            raise Exception("Key ({0}) already exists".format(name))
        self._dataDict[name] = dataSet
        self.dataDictContentChanged = True
        logging.info("addDataset: %s", name)


    def deleteDataset(self, internalName):
        """Remove dataset from collection"""
        del self._dataDict[internalName]
        self.dataDictContentChanged = True
        logging.info("deleteDataset: %s", internalName)


    def getDatasetList(self):
        return self._dataDict.values()

    @property_depends_on( '_dataDict' )
    def _get_indexNameList(self):
        logging.info("Update indexNameList")
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
        self.dataDictContentChanged = True
        logging.info("dictNameChange: %s change from %s to %s", name, old, new)


    @on_trait_change('_dataDict:_displayName')
    def displayNameChanged(self, object, name, old, new):
        self.datasetNameChanged = True
        logging.info("displayNameChange: %s changed from %s to %s", name, old, new)
