# coding=utf-8

# stdlib imports
import logging

# Enthought imports
from enthought.traits.api import HasTraits, Instance, Event, Str, List, on_trait_change, Enum, Button, Any
from enthought.traits.ui.api import View, Item, Group, Handler, EnumEditor, CheckListEditor, TreeEditor, TreeNode


# Local imports
from dataset_collection import DatasetCollection
from plot_scatter import PlotScatter
from plot_line import PlotLine
from nipals import PCA
from dataset_selector_ui import dataset_selector
# from dataset_collection_selection_list_ui import selection_list_view


class Options(HasTraits):
    name = Str( 'Options' )
    dsl = Instance(DatasetCollection)

    # Represent selections in tree
    overview = List()
    scores = List()
    loadings = List()
#    corrLoadings = List()
    explResVar = List()
#    measVsPred = List()


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

#end PcaModelHandler


# Double click handlers
def clkScores(obj):
    logging.info("Scoreplot activated")
    selDataset = getSelectedDataset(obj.dsl)
    pcaResults = PCA(selDataset.matrix, numPC = 2, mode = 1)
    labels = selDataset.objectNames
    # T
    pcaMatrix = pcaResults.getScores()
    calExplVars = pcaResults.getCalExplVar()
    plotPcaResult(pcaMatrix, calExplVars, labels, "PCA Score plot")



def clkLoadings(obj):
    logging.info("Loadingplot activated")
    selDataset = getSelectedDataset(obj.dsl)
    labels = selDataset.variableNames
    pcaResults = PCA(selDataset.matrix, numPC = 2, mode = 1)
    pcaMatrix = pcaResults.getLoadings()
    calExplVars = pcaResults.getCalExplVar()
    plotPcaResult(pcaMatrix, calExplVars, labels, "PCA Loadings plot")



def plotPcaResult(pcaMatrix, calExplVars, labels, title):
    pc1 = pcaMatrix[:,0]
    pc2 = pcaMatrix[:,1]
    pc1CEV = int(calExplVars[1])
    pc2CEV = int(calExplVars[2])
    plot = PlotScatter(
        ttext = title,
        titleX = "PC1 ({0}%)".format(pc1CEV),
        titleY = "PC2 ({0}%)".format(pc2CEV),
        valPtLabel = labels,
        valX = pc1,
        valY = pc2
        )
    plotUI = plot.configure_traits()



def clkExplResVar(obj):
    logging.info("Explained variance plot activated")
    selDataset = getSelectedDataset(obj.dsl)
    pcaResults = PCA(selDataset.matrix, numPC = 2, mode = 1)
    calExplVars = pcaResults.getCalExplVar()

    accContrib = []
    index = []
    for i, contrib in calExplVars.iteritems():
        index.append(i)
        if i <= 1:
            accContrib.append(contrib)
        else:
            prevSum =  accContrib[i-2]
            accContrib.append(prevSum + contrib)

    plot = PlotLine(
        ttext = 'PCA explained variance',
        titleX = '# of principal components',
        titleY = 'Explainded variance [%]',
        valX = index,
        valY = accContrib,
        limY = (0, 100),
        )
    plotUI = plot.configure_traits()




def getSelectedDataset(dsl):
    if dsl.selectedSet[0]:
        setName = dsl.selectedSet[0]
        selSet = dsl.retriveDatasetByName(setName)
        return selSet
    else:
        return None


# Views
no_view = View()


options_tree = TreeEditor(
    hide_root = False,
    editable = True,
#    on_dclick = dbclicked,
#    click = 'handler.clickert',
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
                  view = dataset_selector,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'scores',
                  label = '=Scores',
                  on_dclick = clkScores,
                  view = dataset_selector,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'loadings',
                  label = '=Loadings',
                  on_dclick = clkLoadings,
                  view = dataset_selector,
                  ),
#        TreeNode( node_for = [ Options ],
#                  children = 'corrLoadings',
#                  label = '=Correlation loadings',
#                  view = no_view,
#                  ),
        TreeNode( node_for = [ Options ],
                  children = 'explResVar',
                  label = '=Expl. / res var',
                  on_dclick = clkExplResVar,
                  view = dataset_selector,
                  ),
#        TreeNode( node_for = [ Options ],
#                  children = 'measVsPred',
#                  label = '=Meas vs pred',
#                  view = no_view,
#                  ),
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
