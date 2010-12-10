# -*- coding: utf-8 -*-

# stdlib imports
import logging

# Enthought imports
from enthought.traits.api import HasTraits, Instance, Event, Str, List, Bool, on_trait_change
from enthought.traits.ui.api import View, Item, Handler, TreeEditor, TreeNode

# Local imports
from dataset_collection import DatasetCollection
from ds import DataSet
from plot_scatter import PlotScatter
# import mvr
from mvr import plsr
from prefmap_control_ui import prefmap_control



class Options(HasTraits):
    name = Str( 'Options' )
    dsl = Instance(DatasetCollection)
    setX = DataSet()
    setY = DataSet()
    eqPlotAxis = Bool()

    # Represent selections in tree
    overview = List()
    # T scores
    scores = List()
    # Y loadings
    yloadings = List()
    # X loadings
    xloadings = List()
    #
    explResVar = List()
#    measVsPred = List()


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

#end PrefmapModelHandler


# Double click handlers
def clkScores(obj):
    logging.info("PLSR scores plot activated")
    model = plsr(obj.setX.matrix,
                 obj.setY.matrix,
                 centre="yes",
                 fncomp=4,
                 fmethod="oscorespls",
                 fvalidation="LOO")
    score1 = model['Scores T'][:,0]
    score2 = model['Scores T'][:,1]
    labels = obj.setX.objectNames
    plot = PlotScatter(
        ttext = "PLSR scores",
        valPtLabel = labels,
        valX = score1,
        valY = score2,
        eqAxis = obj.eqPlotAxis
        )
    plotUI = plot.configure_traits()


def clkYloadings(obj):
    logging.info("PLSR Y loadings plot activated")
    model = plsr(obj.setX.matrix,
                 obj.setY.matrix,
                 centre="yes",
                 fncomp=4,
                 fmethod="oscorespls",
                 fvalidation="LOO")
    score1 = model['Yloadings Q'][:,0]
    score2 = model['Yloadings Q'][:,1]
    calExplVars = model['YexplVar']
    pc1CEV = int(calExplVars[0])
    pc2CEV = int(calExplVars[1])
    labels = obj.setY.variableNames
    plot = PlotScatter(
        ttext = "PLSR Y loadings",
        titleX = "PC1 ({0}%)".format(pc1CEV),
        titleY = "PC2 ({0}%)".format(pc2CEV),
        valPtLabel = labels,
        valX = score1,
        valY = score2,
        eqAxis = obj.eqPlotAxis
        )
    plotUI = plot.configure_traits()


def clkXloadings(obj):
    logging.info("PLSR X loadings plot activated")
    model = plsr(obj.setX.matrix,
                 obj.setY.matrix,
                 centre="yes",
                 fncomp=4,
                 fmethod="oscorespls",
                 fvalidation="LOO")
    score1 = model['Xloadings P'][:,0]
    score2 = model['Xloadings P'][:,1]
    calExplVars = model['XexplVar']
    pc1CEV = int(calExplVars[0])
    pc2CEV = int(calExplVars[1])
    labels = obj.setX.variableNames
    plot = PlotScatter(
        ttext = "PLSR X loadings",
        titleX = "PC1 ({0}%)".format(pc1CEV),
        titleY = "PC2 ({0}%)".format(pc2CEV),
        valPtLabel = labels,
        valX = score1,
        valY = score2,
        eqAxis = obj.eqPlotAxis
        )
    plotUI = plot.configure_traits()




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
#                  view = prefmap_control,
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
                  view = prefmap_control,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'scores',
                  label = '=Scores',
                  on_dclick = clkScores,
                  view = prefmap_control,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'yloadings',
                  label = '=Y loadings',
                  on_dclick = clkYloadings,
                  view = prefmap_control,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'xloadings',
                  label = '=X loadings',
                  on_dclick = clkXloadings,
                  view = prefmap_control,
                  ),
#        TreeNode( node_for = [ Options ],
#                  children = 'explResVar',
#                  label = '=Expl. / res var',
#                  view = prefmap_control,
#                  ),
#        TreeNode( node_for = [ Options ],
#                  children = 'measVsPred',
#                  label = '=Meas vs pred',
#                  view = prefmap_control,
#                  ),
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
