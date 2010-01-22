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
from dataset import DataSet



class PcaViewHandler(Handler):
    """Handler for dataset view"""

    # Test tab for PCA
    _pca = Str('PCA hei')
    _runPca = Button(label = 'Run PCA')

    # Called when some value in object changes
    def setattr(self, info, object, name, value):
        super(PcaViewHandler, self).setattr(info, object, name, value)
        print 'PcaViewHandler:setattr:', name, 'to', value


    def handler_runPca_changed(self, uiInfo):
        """PCA activated"""
        print "PcaViewHandle: RunPca pressed"


    # end PcaViewHandler



class PcaModel(HasTraits):
    """Model for PCA"""

    ds = Instance(DataSet)

    # View
    pca_view = View(
        Item('handler._pca'),
        Item('handler._runPca'),
        handler = PcaViewHandler,
        )

    #end PcaModel



if __name__ == '__main__':
    """Run the application. """
    from enthought.pyface.api import GUI
    testset = DataSet()
    testset.importDataset('./testdata/test.txt')
    pca = PcaModel(ds=testset)
    ui = pca.edit_traits()
