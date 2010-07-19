# coding=utf-8

# stdlib imports
import logging

# Enthought imports
from enthought.traits.api import HasTraits, Instance, Event, Str, List, on_trait_change
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
    logging.info("Plot scores activated")
    model = plsr(obj.setX.matrix,
                 obj.setY.matrix,
                 centre="yes",
                 fncomp=4,
                 fmethod="oscorespls",
                 fvalidation="LOO")
    score1 = model['Scores T'][:,0]
    score2 = model['Scores T'][:,1]
    plot = PlotScatter(
        ttext = "Prefmap plot",
        valX = score1,
        valY = score2
        )
    plotUI = plot.configure_traits()


def clkYloadings(obj):
    logging.info("Plot Y loadings activated")
    model = plsr(obj.setX.matrix,
                 obj.setY.matrix,
                 centre="yes",
                 fncomp=4,
                 fmethod="oscorespls",
                 fvalidation="LOO")
    score1 = model['Yloadings Q'][:,0]
    score2 = model['Yloadings Q'][:,1]
    plot = PlotScatter(
        ttext = "Y loadings Q",
        valX = score1,
        valY = score2
        )
    plotUI = plot.configure_traits()


def clkXloadings(obj):
    logging.info("Plot X loadings activated")
    model = plsr(obj.setX.matrix,
                 obj.setY.matrix,
                 centre="yes",
                 fncomp=4,
                 fmethod="oscorespls",
                 fvalidation="LOO")
    score1 = model['Xloadings P'][:,0]
    score2 = model['Xloadings P'][:,1]
    plot = PlotScatter(
        ttext = "X loadings P",
        valX = score1,
        valY = score2
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
                  label = '=Scores T',
                  on_dclick = clkScores,
                  view = prefmap_control,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'yloadings',
                  label = '=Y loadings Q',
                  on_dclick = clkYloadings,
                  view = prefmap_control,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'xloadings',
                  label = '=X loadings P',
                  on_dclick = clkXloadings,
                  view = prefmap_control,
                  ),
        TreeNode( node_for = [ Options ],
                  children = 'explResVar',
                  label = '=Expl. / res var',
                  view = prefmap_control,
                  ),
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
