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
# from dataset_selector_ui import dataset_selector
from dataset_collection_selection_list_ui import selection_list_view


class Options(HasTraits):
    name = Str( 'Options' )
    dsl = Instance(DatasetCollection)

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
        selDataset = self.getSelectedDataset(object.dsl)
        selDataset.print_traits()
        objNames = selDataset.objectNames
        pca = PCA(selDataset.matrix, numPC = 2, mode = 1)
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


    def getSelectedDataset(self, dsl):
        if dsl.selectedSet[0]:
            setName = dsl.selectedSet[0]
            selSet = dsl.retriveDatasetByName(setName)
            return selSet
        else:
            return None


#end PcaModelHandler


# Actions used by tree editor context menu
plot_scores = Action(
    name = 'Plot scores',
    action = 'handler.activate_score_plot(editor, object)'
    )


# Views
no_view = View()


options_tree = TreeEditor(
    hide_root = False,
    editable = True,
    nodes = [
        TreeNode( node_for = [ Options ],
                  children = '',
                  label = 'name',
                  tooltip = 'Oversikt',
                  view = no_view,
#                  view = dataset_selector,
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
                  view = selection_list_view,
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
