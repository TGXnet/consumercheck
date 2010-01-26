# coding=utf-8

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
    _selIndex = Int(0)
    _selList = List

    # Called when some value in object changes
    def setattr(self, info, object, name, value):
        super(PcaViewHandler, self).setattr(info, object, name, value)
        print 'PcaViewHandler:setattr:', name, 'to', value


    def handler__runPca_changed(self, info):
        """PCA activated"""
        print "PcaViewHandle: RunPca pressed"
        if not info.initialized:
            pass
        else:
            # data matrix
            key = self._selList[self._selIndex]
            dm = info.object.dsl._dataDict[key]._matrix
            print "Data matrix\n", dm
            pca = PCA(dm, 2, 1)
            print "Principal components\n", pca.scores
#            plot = PlotPca(pca.scores)
            pc1 = pca.scores[:,0]
            pc2 = pca.scores[:,1]
            plot = PlotPcaNew(pc1=pc1, pc2=pc2)
            
            plotUI = plot.edit_traits(kind='modal')


    def handler__fillSel_changed(self, info):
        liste = []
        for sn, so in info.object.dsl._dataDict.iteritems():
            liste.append(sn)
        self._selList = liste
        print "PcaViewHandler: fillSell pressed", liste


    def handler__selIndex_changed(self, info):
        print "PcaViewHandler: selSet changed", self._selIndex


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
