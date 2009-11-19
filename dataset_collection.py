# coding=utf-8

# Enthought traits imports
from enthought.traits.api import \
    HasTraits, DictStrAny, ListStr, Int,\
     DelegatesTo, Instance, Bool
from enthought.traits.ui.api import View, Item, Group, ListStrEditor
from enthought.traits.ui.menu import OKButton, CancelButton

# Local imports
from dataset import DataSet


class DatasetCollection(HasTraits):
    """ Application wide collection of datasets

    Associated view as a subpanel.
    ListStrEditor() to list datsets
    """

    # Dictionary to hold dataset and a editor to select dataset
    _dataDict = DictStrAny()
    _keyIndex = ListStr()
    _dispNameIndex = ListStr()
    _selIndex = Int(0)
    _testBool = Bool()



    def retriveDatasetByName(self, internalName):
        """Return DataSet object specified by internal name"""
        return self._dataDict[internalName]




    def retriveDatasetByIndex(self, index):
        """Return DataSet object by selection index"""
        if index >= 0:
            iname = self._keyIndex[index]
            return self._dataDict[iname]
        else:
            return None




    def addDataset(self, dataSet):
        """Add or update dataset"""
        self._dataDict[dataSet._internalName] = dataSet
        self._buildIndex()
        




    def delDataset(self, internalName):
        """Remove dataset from collection"""
        pass




    def _buildIndex(self):
        """Build index for datasets"""
        # FIXME: To be called when _dataDict changes
        self._keyIndex = []
        self._dispNameIndex = []
        for k, v in self._dataDict.iteritems():
            self._keyIndex.append(k)
            self._dispNameIndex.append(v._displayName)



    def __str__(self):
        """Return object info"""
        return 'Matrix'



    def _genInternalName(self):
        """Generate unique internal name for datasets"""
        pass






# Bye naming the View traits_view and making it
# member of the DatasetCollectin class, this vill
# be the default view for that class
# collectionPanelView
coll_view = View(
    Group(
        Group(
            Item('coll._dispNameIndex',
                 editor = ListStrEditor(
                    editable=False,
                    multi_select=False,
                    activated_index='coll._selIndex',
                    selected_index='coll._selIndex',
                    ),
                 height = 75,
                 width = 200
                 ),
            label='Collection list'
            ),
        Group(
            Item('set._internalName'),
            Item('set._displayName'),
            Item('set._datasetType'),
            Item('set._matrixColumnHeader'),
            Item('set._isCalculated'),
            Item('set._isActive'),
            label='Collection'
            ),
        orientation = 'horizontal'
        ),
    title = 'Consumer Check',
    buttons = [OKButton, CancelButton]
    )



if __name__ == "__main__":
    dsc = DatasetCollection()
    ds = dsc.retriveDatasetByName('gurg1')

    dsc.configure_traits(
        view=coll_view,
        context = {'coll':dsc,
                   'set':ds}
        )
