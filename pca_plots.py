# -*- coding: utf-8 -*-
""" Function to generate the PCA plots
Input:
the full list of datasets
Pointer to the selected dataset

This functions will run the PCA calculations and generate the Plots.

FIXME: These functions may be embedded in a plot factory class.
This factory object can hold cached PCA results as state and only recalculate
when necessary.
"""

from enthought.chaco.api import ArrayPlotData

from nipals import PCA
from plots import PlotScatter, PlotLine, PlotCorrLoad
from plot_windows import SinglePlotWindow, MultiPlotWindow
from dataset_collection import DatasetCollection

class PCAPlotFactory(object):
	results = {}
	dsl = DatasetCollection()
	show = True

	def __init__(self):
		pass

	def plot_overview(self, datasets, show = True):
		"""Make PCA overview plot.

		Plot an array of plots where we plot scores, loadings, corr. load and expl. var
		for each of the datasets.
		"""
		# Run PCA for each of the datasets
		# Make a list of plots for each of the datasets
		# Put these lists into one list
		# Make multiplot window with all these plots
		self.dsl = datasets
		plots = []
		for name, ds in self.dsl._dataDict.iteritems():
			self._run_pca(name)
			s_plot = self._make_scores_plot(name)
			l_plot = self._make_loadings_plot(name)
			cl_plot = self._make_corr_load_plot(name)
			ev_plot = self._make_expl_var_plot(name)
			ds_plots = [s_plot, l_plot, cl_plot, ev_plot]
			plots.append(ds_plots)
		n_ds = len(self.dsl._dataDict)
		n_plots = 4
		mpw = MultiPlotWindow()
		mpw.plots.component_grid = plots
		mpw.plots.shape = (n_ds, n_plots)
		if show:
			mpw_ui = mpw.configure_traits()

	def plot_scores(self, dataset, show = True):
		""" Activate score plot
		FIXME: Dataset internal name argument.
		Dataset list set in constructor.
		"""
		self.show = show
		name = self._add_ds(dataset)
		s_plot = self._make_scores_plot(name)
		self._show_plot(s_plot)

	def _make_scores_plot(self, ds_name):
		res = self._get_res(ds_name)
		pc_tab = res.getScores()
		labels = self.dsl.retriveDatasetByName(ds_name).objectNames
		plot = self._make_plot(pc_tab, ds_name, labels, "PCA Scores plot\n{0}".format(ds_name))
		return plot

	def plot_loadings(self, dataset, show = True):
		self.show = show
		name = self._add_ds(dataset)
		l_plot = self._make_loadings_plot(name)
		self._show_plot(l_plot)

	def _make_loadings_plot(self, ds_name):
		res = self._get_res(ds_name)
		pc_tab = res.getLoadings()
		labels = self.dsl.retriveDatasetByName(ds_name).variableNames
		plot = self._make_plot(pc_tab, ds_name, labels, "PCA Loadings plot\n{0}".format(ds_name))
		return plot

	def plot_corr_loading(self, dataset, show = True):
		self.show = show
		name = self._add_ds(dataset)
		cl_plot = self._make_corr_load_plot(name)
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


	def plot_expl_var(self, dataset, show = True):
		self.show = show
		name = self._add_ds(dataset)
		ev_plot = self._make_expl_var_plot(name)
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

	def _add_ds(self, ds):
		name = ds._internalName
		try:
			self.dsl.addDataset(ds)
		except Exception:
			pass
		return name

	def _get_res(self, name):
		try:
			return self.results[name]
		except KeyError:
			return self._run_pca(name)

	def _run_pca(self, ds_name):
		res = PCA(self.dsl.retriveDatasetByName(ds_name).matrix)
		self.results[ds_name] = res
		return res

	def _make_plot(self, pc_tab, ds_name, labels, plot_title):
		# labels = self.dsl.retriveDatasetByName(ds_name).objectNames
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

	def _show_plot(self, plot):
		spw = SinglePlotWindow(plot=plot)
		if self.show:
			spw_ui = spw.configure_traits()
