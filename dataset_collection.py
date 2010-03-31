# coding=utf-8

# Enthought traits imports
from enthought.traits.api import \
    HasTraits, Dict, Str, ListStr, Int, List, Event, \
    Bool, Property, cached_property, on_trait_change, property_depends_on

# Local imports
from ds import DataSet


class DatasetCollection(HasTraits):
    """ Application wide collection of datasets

    Associated view as a subpanel.
    ListStrEditor() to list datsets
    """

    # Dictionary to hold dataset and a editor to select dataset
    _dataDict = Dict(Str, DataSet)
    _updated = Bool(False)

    indexNameList = Property()



    def retriveDatasetByName(self, internalName):
        """Return DataSet object specified by internal name"""
        return self._dataDict[internalName]


    def addDataset(self, dataSet):
        """Add or update dataset"""
        name = dataSet._internalName
        if self._dataDict.__contains__(name):
            raise Exception('Key (' + name + ') already exists')
        self._dataDict[name] = dataSet
        self._updated = True
        print "DatasetCollection:addDataset:", name


    def deleteDataset(self, internalName):
        """Remove dataset from collection"""
        del self._dataDict[internalName]
        self._updated = True


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
        self._updated = True
        print "DatasetCollection:", name, "changed from", old ,"to", new


    def _genInternalName(self):
        """Generate unique internal name for datasets"""
        pass
