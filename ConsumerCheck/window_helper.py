"""ConsumerCheck"""

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

# Local imports
from plot_base import NoPlotControl
from plot_windows import SinglePlotWindow
from plot_pc_scatter import (PCScatterPlot, PCPlotControl,
                             ScatterSectorPlot, PCSectorPlotControl,
                             CLPlot, CLPlotControl,
                             CLSectorPlot, CLSectorPlotControl)


def multiplot_factory(plot_func, res, view_loop, title, parent_win=None):
    plot = plot_func(res)
    plot_creator = plot_win_creator_closure(plot_func, res, view_loop, title, parent_win)
    plot.add_left_down_action(plot_creator)

    return plot


def plot_win_creator_closure(plot_func, res, view_loop, title, parent_win):

    def plot_window_creator():
        plot = plot_func(res)

        if isinstance(plot, CLSectorPlot):
            plot_control = CLSectorPlotControl(plot)
            win = SinglePlotWindow(
                plot=plot_control,
                res=res,
                view_loop=view_loop
            )
        elif isinstance(plot, CLPlot):
            plot_control = CLPlotControl(plot)
            win = SinglePlotWindow(
                plot=plot_control,
                res=res,
                view_loop=view_loop
            )
        elif isinstance(plot, ScatterSectorPlot):
            plot_control = PCSectorPlotControl(plot)
            win = SinglePlotWindow(
                plot=plot_control,
                res=res,
                view_loop=view_loop
            )
        elif isinstance(plot, PCScatterPlot):
            plot_control = PCPlotControl(plot)
            win = SinglePlotWindow(
                plot=plot_control,
                res=res,
                view_loop=view_loop
            )
        else:
            plot_control = NoPlotControl(plot)
            win = SinglePlotWindow(
                plot=plot_control,
                res=res,
                view_loop=view_loop
            )

        if parent_win:
            win.edit_traits(parent=parent_win.hwin, kind='live')
        else:
            win.edit_traits(kind='live')

    return plot_window_creator
