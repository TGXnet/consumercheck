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
    activeSet = DataSet()


    def retriveDatasetByName(self, internalName):
        """Return DataSet object specified by internal name"""
        return self._dataDict[internalName]


    def addDataset(self, dataSet):
        """Add or update dataset"""
        self._dataDict[dataSet._internalName] = dataSet
        self._updated = True
        print "DatasetCollection:addDataset:", dataSet._internalName


    def delDataset(self, internalName):
        """Remove dataset from collection"""
        self._updated = True



    # FIXME: does not handle change of _internalName correct
    @on_trait_change('_dataDict:_internalName')
    def dictNameChanged(self, object, name, old, new):
        """Update dictionary name"""
        self._updated = True
        print "DatasetCollection:", name, "changed from", old ,"to", new



#    def __str__(self):
#        """Return object info"""
#        return 'Matrix'



    def _genInternalName(self):
        """Generate unique internal name for datasets"""
        pass


# Unit test code
if __name__ == "__main__":
    dsc = DatasetCollection()
    ts1 = DataSet(_internalName='ts1', _displayName='Test set 1')
    ts2 = DataSet(_internalName='ts2', _displayName='Test set 2')
    dsc.addDataset(ts1)
    dsc.addDataset(ts2)
    ts2.importDataset('./testdata/test.txt', False)
    ds = dsc.retriveDatasetByName('ts1')
    ds._internalName = 'gurba'
