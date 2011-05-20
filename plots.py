# -*- coding: utf-8 -*-
"""Various ConsumerCheck plots
"""

# Enthought library imports
#from enthought.traits.api import HasTraits, Instance, Array, Str, List, Bool
from enthought.chaco.api import Plot, DataLabel

class PlotScatter(Plot):
	"""This is a specialization of the Plot class for convenience

	This have to be instantiated with an ArrayPlotData object.
	Where data key names is *pc_x* and *pc_y*.
	Other values to set:
	title
	[x|y]_axis.title

	The intended use of this plots is PC scatter plot.
	"""

	def __init__(self, *args, **kw):
		super(PlotScatter, self).__init__(*args, **kw)
		self._customize_settings()
		self.plot(
			("pc_x", "pc_y"), name="datapoints",
			type="scatter", index_sort="ascending",
			marker="circle", marker_size=3,
			color="orange", bgcolor="white")

	def _customize_settings(self):
		self.line_width = 0.5
		self.padding = 50

	def addPtLabels(self, valPtLabel):
		"""Labels for each datapoint in scatter plot

		Takes a list with the labels for datapoints
		"""
		for i in xrange(len(valPtLabel)):
			label = DataLabel(
				component = self,
				data_point = (self.data.get_data('pc_x')[i], self.data.get_data('pc_y')[i]),
				label_format = valPtLabel[i]
				)
			self.overlays.append(label)

	def set_eq_axis(self):
		"""To set the same range on both x and y axis
		"""
		xlim, ylim = self._calcBoundsLimits()
		self.x_mapper.range.set_bounds(*xlim)
		self.y_mapper.range.set_bounds(*ylim)

	def _calcBoundsLimits(self):
		# Return tuple of tuple with x and y bounds low and high limit
		iXMin = self.data.get_data('pc_x').argmin()
		iXMax = self.data.get_data('pc_x').argmax()
		xlim = (self.data.get_data('pc_x')[iXMin], self.data.get_data('pc_x')[iXMax])
		iYMin = self.data.get_data('pc_y').argmin()
		iYMax = self.data.get_data('pc_y').argmax()
		ylim = (self.data.get_data('pc_y')[iYMin], self.data.get_data('pc_y')[iYMax])
		if xlim[0] < ylim[0]:
			minLim = xlim[0]
		else:
			minLim = ylim[0]
		if xlim[1] > ylim[1]:
			maxLim = xlim[1]
		else:
			maxLim = ylim[1]
		minLim = minLim - maxLim * 0.1
		maxLim = maxLim + maxLim * 0.1
		return ((minLim, maxLim), (minLim, maxLim))

	def reset_axis(self):
		"""Reset axix to default
		"""
		self.x_mapper.range.reset()
		self.y_mapper.range.reset()


class PlotCorrLoad(PlotScatter):
	"""Specialization of the PlotScatter class customized for convenient correlation loading plotting

	This plots takes data for ploting 2 ellipses.

	This have to be instantiated with an ArrayPlotData object.
	Where data key names is *pc_x* and *pc_y* for PC data.
	ell_full_x and ell_full_y for full ellipse.
	ell_half_x and ell_half_y for half ellipse.
	Other values to set:
	title
	[x|y]_axis.title

	The intended use of this plots is PC scatter plot.
	"""

	def __init__(self, *args, **kw):
		super(PlotCorrLoad, self).__init__(*args, **kw)
		self.plot(
			("ell_full_x", "ell_full_y"),
			name="fullellipse", type="line")
		self.plot(
			("ell_half_x", "ell_half_y"),
			name="halfellipse", type="line")


class PlotLine(Plot):
	"""This is a specialization of the Plot class for convenience

	This have to be instantiated with an ArrayPlotData object.
	Where data key names is *index* and *y_val*.
	Other values to set:
	title
	[x|y]_axis.title
	[x|y]mapper.range.set_bounds(lo, hi)

	The intended use of this plot is PCA explained variance.
	"""

	def __init__(self, *args, **kw):
		super(PlotLine, self).__init__(*args, **kw)
		self._customize_settings()
		self.plot(
			("index", "y_val"), type="line",
			index_sort="ascending",
			color="orange", bgcolor="white")

	def _customize_settings(self):
		self.line_width = 0.5
		self.padding = 50
