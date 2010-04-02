# coding=utf-8

# stdlib imports
import logging

# Enthought imports
from enthought.traits.api \
    import HasTraits, Instance, DelegatesTo, Button, Str, Int,\
    File, Bool, List, on_trait_change
from enthought.traits.ui.api \
    import View, Item, Group, ListStrEditor, Handler, FileEditor,\
    InstanceEditor, ButtonEditor
from enthought.traits.ui.menu \
    import Action, Menu, MenuBar

# Local imports
from dataset_collection import DatasetCollection
from ds import DataSet
from plot_pca_ui import PlotPca, PlotPcaNew
from nipals import PCA


class PcaViewHandler(Handler):
    """Handler for dataset view"""

    _runPca = Button(label = 'Run PCA')
    _fillSel = Button(label = 'Update list')
    _selIndex = Int(-1)
    _selList = List

    # Called when some value in object changes
    def setattr(self, info, object, name, value):
        super(PcaViewHandler, self).setattr(info, object, name, value)
        logging.info("setattr: %s change to %s", name, value)


    def handler__runPca_changed(self, info):
        """PCA activated"""
        logging.info("runPca_changed: RunPca pressed")
        if not info.initialized:
            pass
        else:
            # data matrix
            key = self._selList[self._selIndex]
            dm = info.object.dsl._dataDict[key]._matrix
            pca = PCA(dm, 2, 1)
            pc1 = pca.scores[:,0]
            pc2 = pca.scores[:,1]
            plot = PlotPcaNew(pc1=pc1, pc2=pc2)
            plotUI = plot.edit_traits(kind='modal')


    def handler__fillSel_changed(self, info):
        liste = []
        for sn, so in info.object.dsl._dataDict.iteritems():
            liste.append(sn)
        self._selList = liste
        logging.info("fillSel_changed: fillSell pressed")


    def handler__selIndex_changed(self, info):
        logging.info("selIndex_changed: to %s", self._selIndex)


    # end PcaViewHandler



class PcaModel(HasTraits):
    """Model for PCA"""
    dsl = Instance(DatasetCollection)

    # View
    pca_view = View(
        Item('handler._selList',
             editor = ListStrEditor(
                editable=False,
                multi_select=False,
                activated_index='_selIndex',
                selected_index='_selIndex',
                ),
             ),
        Item('handler._fillSel'),
        Item('handler._runPca'),
        handler = PcaViewHandler,
        )

    #end PcaModel



if __name__ == '__main__':
    """Run the application. """
    testset = DataSet()
    testset.importDataset('./testdata/test.txt')
    pca = PcaModel()
    ui = pca.edit_traits()
