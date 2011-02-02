# -*- coding: utf-8 -*-

# stdlib imports
import logging

# Enthought imports
from enthought.traits.api import HasTraits, Instance, Event, Str, List, on_trait_change, DelegatesTo, DictStrAny
from enthought.traits.ui.api import View, Item, Group, Handler, CheckListEditor, TreeEditor, TreeNode
from enthought.chaco.api import ArrayPlotData


# Local imports
from dataset_collection import DatasetCollection
from plots import PlotScatter, PlotLine, PlotCorrLoad
from plot_windows import SinglePlotWindow, MultiPlotWindow
from nipals import PCA
from dsl_check_list import CheckListController, check_view


class Options(HasTraits):
	name = Str( 'Options' )
	mother = Instance(HasTraits)
	list_control = Instance(CheckListController)

	# Represent selections in tree
	overview = List()
	scores = List()
	loadings = List()
	corrLoadings = List()
	explResVar = List()


class PcaModel(HasTraits):
	"""Model for Pca"""
	# FIXME: Bruke Traits notification til å oppdatere utregnede verdier
	#  It is worth using a WeakRef trait for the father trait to avoid reference cycles.
	mother = Instance(HasTraits)
	dsl = DelegatesTo('mother')
	results = DictStrAny()
	# To notify dataset selector
	datasetsAltered = Event
	treeObjects = Instance( Options, Options() )
	# Control UI in unittest
	show = False
	uis = List()

	@on_trait_change('mother:dsl:[dataDictContentChanged,datasetNameChanged]')
	def datasetsChanged(self, object, name, old, new):
		self.datasetsAltered = True

	def plot_overview(self, sel_ds_list, show = True):
		"""Make PCA overview plot.

		Plot an array of plots where we plot scores, loadings, corr. load and expl. var
		for each of the datasets.
		"""
		self.show = show
		# Run PCA for each of the datasets
		# Make a list of plots for each of the datasets
		# Put these lists into one list
		# Make multiplot window with all these plots
		for ds_name in sel_ds_list:
			s_plot = self._make_scores_plot(ds_name)
			l_plot = self._make_loadings_plot(ds_name)
			cl_plot = self._make_corr_load_plot(ds_name)
			ev_plot = self._make_expl_var_plot(ds_name)
			ds_plots = [[s_plot, l_plot], [cl_plot, ev_plot]]
			mpw = MultiPlotWindow()
			mpw.plots.component_grid = ds_plots
			mpw.plots.shape = (2, 2)
			if self.show:
				self.uis.append( mpw.edit_traits(kind='live') )

	def plot_scores(self, sel_ds_list, show = True):
		self.show = show
		for ds_name in sel_ds_list:
			s_plot = self._make_scores_plot(ds_name)
			self._show_plot(s_plot)

	def _make_scores_plot(self, ds_name):
		res = self._get_res(ds_name)
		pc_tab = res.getScores()
		labels = self.dsl.retriveDatasetByName(ds_name).objectNames
		plot = self._make_plot(pc_tab, ds_name, labels, "PCA Scores plot\n{0}".format(ds_name))
		return plot

	def plot_loadings(self, sel_ds_list, show = True):
		self.show = show
		for ds_name in sel_ds_list:
			l_plot = self._make_loadings_plot(ds_name)
			self._show_plot(l_plot)

	def _make_loadings_plot(self, ds_name):
		res = self._get_res(ds_name)
		pc_tab = res.getLoadings()
		labels = self.dsl.retriveDatasetByName(ds_name).variableNames
		plot = self._make_plot(pc_tab, ds_name, labels, "PCA Loadings plot\n{0}".format(ds_name))
		return plot

	def _make_plot(self, pc_tab, ds_name, labels, plot_title):
		expl_vars = self._get_res(ds_name).getCalExplVar()
		pd = ArrayPlotData()
		pd.set_data('pc_x', pc_tab[:,0])
		pd.set_data('pc_y', pc_tab[:,1])
		ps = PlotScatter(pd)
		ps.title = plot_title
		ps.x_axis.title = "PC1 ({0:.0f}%)".format(expl_vars[1])
		ps.y_axis.title = "PC2 ({0:.0f}%)".format(expl_vars[2])
		ps.addPtLabels(labels)
		return ps

	def plot_corr_loading(self, sel_ds_list, show = True):
		self.show = show
		for ds_name in sel_ds_list:
			cl_plot = self._make_corr_load_plot(ds_name)
			self._show_plot(cl_plot)

	def _make_corr_load_plot(self, ds_name):
		res = self._get_res(ds_name)
		labels = self.dsl.retriveDatasetByName(ds_name).variableNames
		pc_tab = res.getCorrLoadings()
		ellipses = res.getCorrLoadingsEllipses()
		expl_vars = res.getCalExplVar()
		pd = ArrayPlotData()
		pd.set_data('pc_x', pc_tab[:,0])
		pd.set_data('pc_y', pc_tab[:,1])
		pd.set_data('ell_full_x', ellipses['x100perc'])
		pd.set_data('ell_full_y', ellipses['y100perc'])
		pd.set_data('ell_half_x', ellipses['x50perc'])
		pd.set_data('ell_half_y', ellipses['y50perc'])
		pcl = PlotCorrLoad(pd)
		pcl.title = "PCA Correlation Loadings plot\n{0}".format(ds_name)
		pcl.x_axis.title = "PC1 ({0:.0f}%)".format(expl_vars[1])
		pcl.y_axis.title = "PC2 ({0:.0f}%)".format(expl_vars[2])
		pcl.addPtLabels(labels)
		return pcl

	def plot_expl_var(self, sel_ds_list, show = True):
		self.show = show
		for ds_name in sel_ds_list:
			ev_plot = self._make_expl_var_plot(ds_name)
			self._show_plot(ev_plot)

	def _make_expl_var_plot(self, ds_name):
		res = self._get_res(ds_name)
		expl_vars = res.getCalExplVar()
		expl_index = [0]
		expl_val = [0]
		for index, value in expl_vars.iteritems():
			expl_index.append(index)
			expl_val.append(expl_val[index-1] + value)
		pd = ArrayPlotData(index=expl_index, y_val=expl_val)
		pl = PlotLine(pd)
		pl.title = "PCA explained variance plot\n{0}".format(ds_name)
		pl.x_axis.title = "# f principal components"
		pl.y_axis.title = "Explained variance [%]"
		pl.y_mapper.range.set_bounds(0, 100)
		return pl

	def _show_plot(self, plot):
		spw = SinglePlotWindow(plot=plot)
		if self.show:
			self.uis.append( spw.edit_traits(kind='live') )

	def _get_res(self, name):
		try:
			return self.results[name]
		except KeyError:
			return self._run_pca(name)

	def _run_pca(self, ds_name):
		res = PCA(self.dsl.retriveDatasetByName(ds_name).matrix)
		self.results[ds_name] = res
		return res


class PcaModelHandler(Handler):
	# plot_uis = List()

	def init(self, info):
		# info.object.treeObjects.dsl = info.object.dsl
		info.object.treeObjects.mother = info.object
		info.object.treeObjects.list_control = CheckListController( model=info.object.dsl)
		check_view.handler = info.object.treeObjects.list_control

	## def closed(self, info, is_ok):
	## 	while self.plot_uis:
	## 		plot_ui = self.plot_uis.pop()
	## 		plot_ui.dispose()


# Double click handlers
def clkOverview(obj):
	logging.info("Overview plot activated")
	obj.mother.plot_overview(obj.list_control.selected)

def clkScores(obj):
	logging.info("Scoreplot activated")
	obj.mother.plot_scores(obj.list_control.selected)

def clkLoadings(obj):
	logging.info("Loadingplot activated")
	obj.mother.plot_loadings(obj.list_control.selected)

def clkCorrLoad(obj):
	logging.info("Loadingplot activated")
	obj.mother.plot_corr_loading(obj.list_control.selected)

def clkExplResVar(obj):
	logging.info("Explained variance plot activated")
	obj.mother.plot_expl_var(obj.list_control.selected)


# Views
no_view = View()

options_tree = TreeEditor(
	nodes = [
		TreeNode( node_for = [ Options ],
				  children = '',
				  label = 'name',
				  tooltip = 'Oversikt',
				  view = no_view,
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
				  view = check_view,
				  ),
		TreeNode( node_for = [ Options ],
				  children = 'scores',
				  label = '=Scores',
				  on_dclick = clkScores,
				  view = check_view,
				  ),
		TreeNode( node_for = [ Options ],
				  children = 'loadings',
				  label = '=Loadings',
				  on_dclick = clkLoadings,
				  view = check_view,
				  ),
		TreeNode( node_for = [ Options ],
				  children = 'corrLoadings',
				  label = '=Correlation loadings',
				  on_dclick = clkCorrLoad,
				  view = check_view,
				  ),
		TreeNode( node_for = [ Options ],
				  children = 'explResVar',
				  label = '=Explained variance',
				  on_dclick = clkExplResVar,
				  view = check_view,
				  ),
		],
	hide_root = False,
	editable = True
	)


pca_tree_view = View(
	Item('treeObjects',
		 editor=options_tree,
		 resizable=True,
		 show_label=False
		 ),
	title='Options tree',
	resizable=True,
	width=.4,
	height=.3,
	handler=PcaModelHandler(),
	)
