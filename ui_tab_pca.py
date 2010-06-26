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
    import Action, Menu, MenuBar, Separator
from enthought.traits.ui.wx.tree_editor \
    import NewAction, CopyAction, CutAction, \
    PasteAction, DeleteAction, RenameAction


# Local imports
from dataset_collection import DatasetCollection
from ds import DataSet
from plot_scatter import PlotScatter
#import mvr
from nipals import PCA


class PcaOverviewHandler( Handler ):
    """Handler for dataset view"""

    dsChoices = List(trait = Str)
    nameSetX = Str(label = 'PCA input matrix')


    # Called when some value in object changes
    def setattr(self, info, object, name, value):
        super(PcaOverviewHandler, self).setattr(
            info, object, name, value)
        logging.info("setattr: %s change to %s", name, value)


    def handler_nameSetX_changed(self, info):
        info.object.setX = info.object.dsl.retriveDatasetByDisplayName(
            info.handler.nameSetX)

    def init(self, info):
        self._buildSelectionList(info.object)


    def object_datasetsAltered_changed(self, info):
        self._buildSelectionList(info.object)


    def _buildSelectionList(self, pcaObj):
        self.dsChoices = []
        for kName, dName in pcaObj.dsl.indexNameList:
            self.dsChoices.append(dName)
        if len(self.dsChoices) > 0:
            self.nameSetX = self.dsChoices[0]


# end PcaOverviewHandler


class Options(HasTraits):
    name = Str( 'Options' )
    dsl = Instance(DatasetCollection)
    setX = DataSet()

    # Represent selections in tree
    overview = List()
    scores = List()
    loadings = List()
    corrLoadings = List()
    explResVar = List()
    measVsPred = List()


class PcaModel(HasTraits):
    """Model for Pca"""
    dsl = Instance(DatasetCollection)
    datasetsAltered = Event
    treeObjects = Instance( Options, Options() )


    @on_trait_change('dsl:[dataDictContentChanged,datasetNameChanged]')
    def datasetsChanged(self, object, name, old, new):
        self.datasetsAltered = True

#end PcaModel


class PcaModelHandler( Handler ):

    def init(self, info):
        info.object.treeObjects.dsl = info.object.dsl


    def activate_score_plot(self, editor, object):
        logging.info("Do pca pressed")
        # pca = editor.get_parent( object )
        objNames = object.setX.objectNames
        pca = PCA(object.setX.matrix, numPC = 2, mode = 1)
        T = pca.getScores()
        calExplVars = pca.getCalExplVar()
        pc1 = T[:,0]
        pc2 = T[:,1]
        pc1CEV = int(calExplVars[1])
        pc2CEV = int(calExplVars[2])
        plot = PlotScatter(
            ttext = "PCA Scores Plot",
            titleX = "PC1 ({0}%)".format(pc1CEV),
            titleY = "PC2 ({0}%)".format(pc2CEV),
            valPtLabel = objNames,
            valX = pc1,
            valY = pc2
            )
#       plotUI = plot.edit_traits(kind='modal')
        plotUI = plot.configure_traits()

#end PcaModelHandler


# Actions used by tree editor context menu
plot_scores = Action(
    name = 'Plot scores',
    action = 'handler.activate_score_plot(editor, object)'
    )

# Views
no_view = View()

pca_overview = View(
    Item('handler.nameSetX',
         editor = EnumEditor(name = 'handler.dsChoices'),
         ),
    resizable = True,
    handler = PcaOverviewHandler(),
    )

options_tree = TreeEditor(
    hide_root = False,
    editable = True,
    nodes = [
        TreeNode( node_for = [ Options ],
                  children = '',
                  label = 'name',
                  tooltip = 'Oversikt',
                  view = no_view,
#                  view = pca_overview,
                  rename = False,
                  rename_me = False,
                  copy = False,
                  delete = False,
                  delete_me = False,
                  insert = False,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'overview',
                  label = '=Overview',
                  view = pca_overview,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'scores',
                  label = '=Scores',
                  menu = Menu( plot_scores ),
                  view = no_view,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'loadings',
                  label = '=Loadings',
                  menu = Menu( plot_scores ),
                  view = no_view,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'corrLoadings',
                  label = '=Correlation loadings',
                  menu = Menu( plot_scores ),
                  view = no_view,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'explResVar',
                  label = '=Expl. / res var',
                  menu = Menu( plot_scores ),
                  view = no_view,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'measVsPred',
                  label = '=Meas vs pred',
                  menu = Menu( plot_scores ),
                  view = no_view,
                  ),
        ]
    )

pca_tree_view = View(
    Item( 'treeObjects',
          editor = options_tree,
          resizable = True,
          show_label = False
          ),
    title = 'Options tree',
    resizable = True,
    width = .4,
    height = .3,
    handler = PcaModelHandler(),
    )
