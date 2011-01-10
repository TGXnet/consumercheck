# -*- coding: utf-8 -*-

# stdlib imports
import logging

# Enthought imports
from enthought.traits.api import HasTraits, Instance, Event, Str, List, on_trait_change, Enum, Button, Any
from enthought.traits.ui.api import View, Item, Group, Handler, EnumEditor, CheckListEditor, TreeEditor, TreeNode


# Local imports
from dataset_collection import DatasetCollection
from plot_scatter import PlotScatter
from plot_corr_load import PlotCorrLoad
from plot_line import PlotLine

from nipals import PCA
from dataset_selector_ui import dataset_selector
from pca_plots import PCAPlotFactory
# from dataset_collection_selection_list_ui import selection_list_view


class Options(HasTraits):
	name = Str( 'Options' )
	dsl = Instance(DatasetCollection)

	# Represent selections in tree
	overview = List()
	scores = List()
	loadings = List()
	corrLoadings = List()
	explResVar = List()


class PcaModel(HasTraits):
	"""Model for Pca"""
	dsl = Instance(DatasetCollection)
	datasetsAltered = Event
	treeObjects = Instance( Options, Options() )

	@on_trait_change('dsl:[dataDictContentChanged,datasetNameChanged]')
	def datasetsChanged(self, object, name, old, new):
		self.datasetsAltered = True


class PcaModelHandler(Handler):

	def init(self, info):
		info.object.treeObjects.dsl = info.object.dsl

# Double click handlers
# FIXME: Lot of repitation here
def clkOverview(obj):
	logging.info("Overview plot activated")
	PCAPlotFactory().plot_overview(obj.dsl)

def clkScores(obj):
	logging.info("Scoreplot activated")
	selDataset = getSelectedDataset(obj.dsl)
	PCAPlotFactory().plot_scores(selDataset)

def clkLoadings(obj):
	logging.info("Loadingplot activated")
	selDataset = getSelectedDataset(obj.dsl)
	PCAPlotFactory().plot_loadings(selDataset)

def clkCorrLoad(obj):
	logging.info("Loadingplot activated")
	selDataset = getSelectedDataset(obj.dsl)
	PCAPlotFactory().plot_corr_loading(selDataset)

def clkExplResVar(obj):
	logging.info("Explained variance plot activated")
	selDataset = getSelectedDataset(obj.dsl)
	PCAPlotFactory().plot_expl_var(selDataset)

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
#	 on_dclick = dbclicked,
#	 click = 'handler.clickert',
	nodes = [
		TreeNode( node_for = [ Options ],
				  children = '',
				  label = 'name',
				  tooltip = 'Oversikt',
				  view = no_view,
#				   view = dataset_selector,
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
				  on_dclick = clkOverview,
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
		TreeNode( node_for = [ Options ],
				  children = 'corrLoadings',
				  label = '=Correlation loadings',
				  on_dclick = clkCorrLoad,
				  view = dataset_selector,
				  ),
		TreeNode( node_for = [ Options ],
				  children = 'explResVar',
				  label = '=Explained variance',
				  on_dclick = clkExplResVar,
				  view = dataset_selector,
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
