
# Local imports
from plot_windows import SinglePlotWindow


def multiplot_factory(plot_func, res, view_loop, title):
    plot = plot_func(res)
    plot_creator = plot_win_creator_closure(plot_func, res, view_loop, title)
    plot.add_left_down_action(plot_creator)

    return plot


def plot_win_creator_closure(plot_func, res, view_loop, title):

    def plot_window_creator():
        plot = plot_func(res)
        win = SinglePlotWindow(
            plot=plot,
            res=res,
            title_text=title,
            view_loop=view_loop
            )
        win.edit_traits(kind='live')

    return plot_window_creator
