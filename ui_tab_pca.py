# coding=utf-8

# stdlib imports
import logging

# Enthought imports
from enthought.traits.api \
    import HasTraits, Instance, DelegatesTo, Event, Button, Str, Int,\
    File, Bool, List, on_trait_change
from enthought.traits.ui.api \
    import View, Item, Group, ListStrEditor, Handler, FileEditor,\
    InstanceEditor, ButtonEditor
from enthought.traits.ui.menu \
    import Action, Menu, MenuBar

# Local imports
from dataset_collection import DatasetCollection
from ds import DataSet
from plot_scatter import PlotScatter
from nipals import PCA


class PcaViewHandler(Handler):
    """Handler for dataset view"""

    _runPca = Button(label = 'Run PCA')

    # list of tuples (internalName, displayName)
    _indexList = List()

    # View list of dataset names
    _nameList    = List()

    # Index to the selected dataset name
    _selIndex = Int(-1)


    # Called when some value in object changes
    def setattr(self, info, object, name, value):
        super(PcaViewHandler, self).setattr(info, object, name, value)
        logging.info("setattr: %s change to %s", name, value)


    def handler__runPca_changed(self, uiInfo):
        """PCA activated"""
        logging.info("runPca_changed: RunPca pressed")
        if uiInfo.initialized:
            key = self._indexToName(self._selIndex)
            dm = uiInfo.object.dsl._dataDict[key]._matrix
            pca = PCA(dm, numPC = 2, mode = 1)
            T = pca.getScores()
            pc1 = T[:,0]
            pc2 = T[:,1]
            plot = PlotScatter(
                ttext = "PCA Scores Plot",
                valX = pc1,
                valY = pc2
                )
            plotUI = plot.edit_traits(kind='modal')


    def _indexToName(self, index):
        """Return dataset name from list index"""
        return self._indexList[index][0]


    def object_datasetsAltered_changed(self, uiInfo):
        self._buildIndexList(uiInfo.object.dsl)
        logging.info("datasetAltered: activated")


    # FIXME: Copy from ui_tab_ds_list
    def _buildIndexList(self, datasetCollectionObject):
        self._indexList = datasetCollectionObject.indexNameList
        self._nameList = []
        for kName, dName in self._indexList:
            self._nameList.append(dName)


    def handler__selIndex_changed(self, uiInfo):
        logging.info("selIndex_changed: to %s", self._selIndex)


    # end PcaViewHandler



class PcaModel(HasTraits):
    """Model for PCA"""
    dsl = Instance(DatasetCollection)
    datasetsAltered = Event


    @on_trait_change('dsl:[dataDictContentChanged,datasetNameChanged]')
    def datasetsChanged(self, object, name, old, new):
        self.datasetsAltered = True



    # View
    pca_view = View(
        Item('handler._nameList',
             editor = ListStrEditor(
                editable=False,
                multi_select=False,
                activated_index='_selIndex',
                selected_index='_selIndex',
                ),
             show_label = False
             ),
        Item('handler._runPca',
             show_label = False
             ),
        handler = PcaViewHandler,
        )

    #end PcaModel



if __name__ == '__main__':
    """Run the application. """
    testset = DataSet()
    testset.importDataset('./testdata/test.txt')
    pca = PcaModel()
    ui = pca.edit_traits()
