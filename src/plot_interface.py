'''ConsumerCheck
'''
#-----------------------------------------------------------------------------
#  Copyright (C) 2014 Thomas Graff <thomas.graff@tgxnet.no>
#
#  This file is part of ConsumerCheck.
#
#  ConsumerCheck is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  ConsumerCheck is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ConsumerCheck.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------

from traits.api import Interface


class IPlot(Interface):
    """Interface for ploting objects"""

    def show_labels(self, set_id=None, show=True):
        """Controls label visibility in plot"""

    def export_image(self, fname, size=(800, 600)):
        """Save this plot as an image"""


class IPCScatterPlot(IPlot):
    """Interface for scatter type plots for Principal Components"""

    def add_PC_set(self, matrix, labels=None, color=None, expl_vars=None):
        """Add different sets of plot data to plot window"""


class IEVLinePlot(IPlot):
    """Interface for line type plots for Explained variance."""

    def add_EV_set(self, ev_vector, color=None, legend=None):
        """Add a line to the plot window"""
