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
from ds import DataSet
from plot_pca_ui import PlotPca
from nipals import PCA


class PcaViewHandler(Handler):
    """Handler for dataset view"""

    _runPca = Button(label = 'Run PCA')


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
            dm = info.object.activeSet._matrix
            print "Data matrix\n", dm
            pca = PCA(dm, 2, 1)
            print "Principal components\n", pca.scores
            plot = PlotPca(pca.scores)
            
            plotUI = plot.edit_traits(kind='modal')

    # end PcaViewHandler



class PcaModel(HasTraits):
    """Model for PCA"""

    activeSet = DataSet()

    # View
    pca_view = View(
        Item('handler._runPca'),
        handler = PcaViewHandler,
        )

    #end PcaModel



if __name__ == '__main__':
    """Run the application. """
    testset = DataSet()
    testset.importDataset('./testdata/test.txt')
    pca = PcaModel(activeSet=testset)
    ui = pca.edit_traits()
