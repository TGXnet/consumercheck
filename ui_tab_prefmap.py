# coding=utf-8

# stdlib imports
import logging

# Enthought imports
from enthought.traits.api \
    import HasTraits, Instance, Event, Str,\
    List, on_trait_change, Enum, Button
from enthought.traits.ui.api \
    import View, Item, Group, Handler, EnumEditor, CheckListEditor,\
    TreeEditor, TreeNode
from enthought.traits.ui.menu \
    import Action, Menu, MenuBar

# Local imports
from dataset_collection import DatasetCollection
from ds import DataSet
from plot_pca_ui import PlotPcaNew
import mvr


class PrefmapOverviewHandler( Handler ):
    """Handler for dataset view"""

    dsChoices = List(trait = Str)
    nameSetX = Str(label = 'Sensory profiling (X)')
    nameSetY = Str(label = 'Consumer (Y)')
    validate = Enum('None', ['None', 'Full cross'], label = 'Validation')
    _runPrefmap = Button(label = 'Do PrefMap')


    # Called when some value in object changes
    def setattr(self, info, object, name, value):
        super(PrefmapOverviewHandler, self).setattr(
            info, object, name, value)
        logging.info("setattr: %s change to %s", name, value)


    def handler__runPrefmap_changed(self, info):
        logging.info("Do prefmap pressed")
        model = mvr.plsr(info.object.setX._matrix,
                         info.object.setY._matrix,
                         centre="yes",
                         fncomp=4,
                         fmethod="oscorespls",
                         fvalidation="LOO")
        score1 = model['Scores T'][:,0]
        score2 = model['Scores T'][:,1]
        plot = PlotPcaNew(pc1=score1, pc2=score2)
        plotUI = plot.edit_traits(kind='modal')



    def handler_nameSetX_changed(self, info):
        info.object.setX = info.object.dsl.retriveDatasetByDisplayName(
            info.handler.nameSetX)


    def handler_nameSetY_changed(self, info):
        info.object.setY = info.object.dsl.retriveDatasetByDisplayName(
            info.handler.nameSetY)


    def init(self, info):
        self._buildSelectionList(info.object)


    def object_datasetsAltered_changed(self, info):
        self._buildSelectionList(info.object)


    def _buildSelectionList(self, prefmapObj):
        self.dsChoices = []
        for kName, dName in prefmapObj.dsl.indexNameList:
            self.dsChoices.append(dName)
        if len(self.dsChoices) > 0:
            self.nameSetX = self.dsChoices[0]
            self.nameSetY = self.dsChoices[0]

# end PrefmapOverviewHandler


class Options(HasTraits):
    name = Str( 'Options' )
    dsl = Instance(DatasetCollection)
    setX = DataSet()
    setY = DataSet()
    overview = List()
    scores = List()


class PrefmapModel(HasTraits):
    """Model for Prefmap"""
    dsl = Instance(DatasetCollection)
    datasetsAltered = Event
    treeObjects = Instance( Options, Options() )


    @on_trait_change('dsl:[dataDictContentChanged,datasetNameChanged]')
    def datasetsChanged(self, object, name, old, new):
        self.datasetsAltered = True

#end PrefmapModel


class PrefmapModelHandler( Handler ):

    def init(self, info):
        info.object.treeObjects.dsl = info.object.dsl
        print 'Init run'

#end PrefmapModelHandler


# Views
no_view = View()

prefmap_overview = View(
    Item('handler.nameSetX',
         editor = EnumEditor(name = 'handler.dsChoices'),
         ),
    Item('handler.nameSetY',
         editor = EnumEditor(name = 'handler.dsChoices'),
         ),
    Item('handler.validate'),
    Item('handler._runPrefmap',
         show_label = False
         ),
    resizable = True,
    handler = PrefmapOverviewHandler(),
    )

options_tree = TreeEditor(
    hide_root = False,
    nodes = [
        TreeNode( node_for = [ Options ],
                  children = '',
                  label = 'name',
                  tooltip = 'Oversikt',
                  view = no_view,
#                  view = prefmap_overview,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'overview',
                  label = '=Overview',
                  view = prefmap_overview,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'scores',
                  label = '=Scores',
                  view = no_view,
                  ),
        ]
    )

prefmap_tree_view = View(
    Item( 'treeObjects',
          editor = options_tree,
          resizable = True,
          show_label = False
          ),
    title = 'Options tree',
    resizable = True,
    width = .4,
    height = .3,
    handler = PrefmapModelHandler(),
    )
