# SciPy imports
import numpy as np

# Enthought library imports

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import Instance, Bool, Str, Button, on_trait_change
from traitsui.api import View, Group, Item, Label, Handler
#Local imports
from ui_results import TableViewController




from chaco.api import (ArrayPlotData, LabelAxis, DataView, Legend, PlotLabel,
                       ErrorBarPlot, ArrayDataSource, LinearMapper,DataRange1D,
                       add_default_grids, ScatterPlot, LinePlot, PlotAxis)
from chaco.tools.api import ZoomTool, PanTool, LegendTool
from chaco.example_support import COLOR_PALETTE

#Local imports
from plot_windows import PlotWindow



class MainEffectsPlot(DataView):
    def __init__(self, conj_res, attr_name, pl_ref):
        super(MainEffectsPlot, self).__init__()
        self.pl_ref = pl_ref
        self._adapt_conj_main_effect_data(conj_res, attr_name)
        self._create_plot()


    def _adapt_conj_main_effect_data(self, conj_res, attr_name):
        """FIXME: Can this bee extracted as an utility function
        that will return an result object but only with the needed values?
        """
        ls_means = conj_res['lsmeansTable']['data']
        ls_means_labels = conj_res['lsmeansTable']['rowNames']
        cn = list(conj_res['lsmeansTable']['colNames'])
        nli = cn.index('Estimate')
        cn = cn[:nli]

        # The folowing logic is about selecting rows from the result sets.
        # The picker i an boolean vector that selects the rows i will plot.

        # First; select all rows where the given attribute have an index value
        picker = ls_means[attr_name] != 'NA'

        # Then; exclude all the interaction rows where the given attribute
        # is a part of the interaction
        exclude = [ls_means[col] != 'NA' for col in cn if col != attr_name]
        for out in exclude:
            picker = np.logical_and(picker, np.logical_not(out))

        # Use the boolean selection vector to select the wanted rows from the result set
        selected = ls_means[picker]
        selected_labels = ls_means_labels[picker]

        self.ls_label_names = []
        self.ls_label_pos = []
        for i, pl in enumerate(selected_labels):
            self.ls_label_names.append(pl)
            self.ls_label_pos.append(i + 1)

        self.apd = ArrayPlotData()
        self.apd.set_data('index', [int(val) for val in selected[attr_name]])
        self.apd.set_data('values', [float(val) for val in selected[' Estimate ']])
        self.apd.set_data('ylow', [float(val) for val in selected[' Lower CI ']])
        self.apd.set_data('yhigh', [float(val) for val in selected[' Upper CI ']])
        self.apd.set_data('average', [conj_res['meanLiking'] for
                                      val in selected[attr_name]])
        self.data = self.apd


    def _create_plot(self):
        #Prepare data for plots
        x = ArrayDataSource(self.apd['index'])
        y = ArrayDataSource(self.apd['values'])
        ylow = ArrayDataSource(self.apd['ylow'])
        yhigh = ArrayDataSource(self.apd['yhigh'])
        yaverage = ArrayDataSource(self.apd['average'])
        
        index_mapper = LinearMapper(
            range=DataRange1D(x, tight_bounds=False, margin=0.05))
        value_mapper = LinearMapper(
            range=DataRange1D(ylow, yhigh, tight_bounds=False))
        
        #Create vertical bars to indicate confidence interval
        y_name='CIbars'
        plot_err = ErrorBarPlot(
            index=x, index_mapper=index_mapper,
            value_low = ylow, value_high = yhigh,
            value_mapper = value_mapper,
            name=y_name,
            bgcolor = "white", border_visible = True)

        #Append label and grid
        x_axis = LabelAxis(
            plot_err, name=y_name,
            orientation="bottom",
            tick_weight=1, tick_label_rotate_angle = 90,
            labels=self.ls_label_names,
            positions = self.ls_label_pos,
            )

        y_axis = PlotAxis(
            orientation='left', title= '',
            mapper=plot_err.value_mapper,
            component=plot_err)

        plot_err.underlays.append(x_axis)
        plot_err.underlays.append(y_axis)
        add_default_grids(plot_err)
        
        #Create averageplot
        y_name='average'
        plot_y_average = LinePlot(
            index=x, index_mapper=index_mapper,
            value=yaverage, value_mapper=value_mapper,
            name=y_name,
            color='green')

        #Create lineplot
        y_name='line'
        plot_line = LinePlot(
            index=x, index_mapper=index_mapper,
            value=y, value_mapper=value_mapper,
            name=y_name)
        
        #Create ScatterPlot
        y_name='scatter'
        plot_scatter = ScatterPlot(
            index=x, index_mapper=index_mapper,
            value=y, value_mapper=value_mapper,
            name=y_name,
            color="blue", marker_size=5)

        zoom = ZoomTool(plot_err, tool_mode="box", always_on=False)
        plot_err.tools.append(PanTool(plot_err))
        plot_err.overlays.append(zoom)  
        self.add(plot_y_average, plot_err ,plot_line, plot_scatter)


class InteractionPlot(DataView):

    def __init__(self, conj_res, attr_one_name, attr_two_name, pl_ref):
        super(InteractionPlot, self).__init__()
        self.pl_ref = pl_ref
        self.conj_res = conj_res
        self.attr_one_name = attr_one_name
        self.attr_two_name = attr_two_name
        self._adapt_conj_interaction_data()


    def _adapt_conj_interaction_data(self, flip=False):
        """
        attr_one_name: Default index axis
        attr_two_name: Default lines
        flip: Decide which attribute to be index and which to be lines
        """
        if not flip:
            self.index_attr, self.line_attr = self.attr_one_name, self.attr_two_name
        else:
            self.index_attr, self.line_attr = self.attr_two_name, self.attr_one_name

        ls_means = self.conj_res['lsmeansTable']['data']

        picker_one = ls_means[self.index_attr] != 'NA'
        picker_two = ls_means[self.line_attr] != 'NA'
        # Picker is an boolean selction vector
        picker = np.logical_and(picker_one, picker_two)
        selected = ls_means[picker][[self.index_attr, self.line_attr, ' Estimate ']]

        lines = sorted(list(set(selected[self.line_attr])))
        indexes = sorted(list(set(selected[self.index_attr])))
        index_labels = ['{0} {1}'.format(self.index_attr, i) for i in indexes]

        # Nullify all plot related list to make shure we can
        # make the ploting idempotent
        self.plot_components = []
        self.index_range.sources = []
        self.value_range.sources = []
        self.tools = []
        self.overlays = []

        self.index_range.tight_bounds = False
        self.value_range.tight_bounds = False

        idx = ArrayDataSource([int(val) for val in indexes])
        self.index_range.sources.append(idx)

        #Append label and grid
        x_axis = LabelAxis(
            self,
            orientation="bottom",
            tick_weight=1,
            tick_label_rotate_angle = 90,
            labels=index_labels,
            positions = [int(val) for val in indexes],
            )

        self.index_axis = x_axis

        # Add a legend in the upper right corner, and make it relocatable
        plots = {}
        legend = Legend(component=self, padding=10, align="ur")
        legend.tools.append(LegendTool(legend, drag_button="right"))
        self.overlays.append(legend)

        # for hvert nytt plot trenger vi bare et nytt dataset

        for i, line in enumerate(lines):
            line_data_picker = selected[self.line_attr] == line
            line_data = selected[line_data_picker]
            vals = ArrayDataSource([float(val) for val in line_data[' Estimate ']])
            self.value_range.sources.append(vals)
            plot = LinePlot(index=idx, value=vals,
                            index_mapper=LinearMapper(range=self.index_range),
                            value_mapper=LinearMapper(range=self.value_range),
                            color=COLOR_PALETTE[i],
                            )
            self.add(plot)
            plots["{0} {1}".format(self.line_attr, line)] = plot

        legend.plots = plots

        self.tools.append(PanTool(self))
        self.overlays.append(ZoomTool(self))
        # Add the title at the top
        self.overlays.append(PlotLabel("Conjoint interaction plot",
                                       component=self,
                                       font = "swiss 16",
                                       overlay_position="top"))

        # Add the traits inspector tool to the container
        # self.tools.append(TraitsTool(self))


#===============================================================================
# Attributes to use for the plot view.
size = (850, 650)
bg_color="white"
#===============================================================================

class TitleHandler(Handler):
    """ Change the title on the UI.

    """
    def object_title_text_changed(self, info):
        """ Called whenever the title_text attribute changes on the handled object.

        """
        info.ui.title = info.object.title_text



class InteractionPlotWindow(PlotWindow):
    """Window for embedding line plot

    """
    plot = Instance(Component)
    eq_axis = Bool(False)
    show_labels = Bool(True)
    view_table = Button('View result table')
    title_text = Str("ConsumerCheck")
    flip = Bool(False)

    @on_trait_change('show_labels')
    def switch_labels(self, obj, name, new):
        # ds_id = name.partition('_')[2]
        obj.plot.show_labels(show=new)

    @on_trait_change('eq_axis')
    def switch_axis(self, obj, name, new):
        obj.plot.toggle_eq_axis(new)

    @on_trait_change('view_table')
    def show_table(self, obj, name, new):
        tvc = TableViewController(model=obj.plot)
        tvc.configure_traits()

    @on_trait_change('flip')
    def flip_interaction(self, obj, name, new):
        obj.plot._adapt_conj_interaction_data(new)


    traits_view = View(
        Group(
            Group(
                Item('plot',
                     editor=ComponentEditor(
                         size = size,
                         bgcolor = bg_color),
                     show_label=False),
                orientation = "vertical"
                ),
            Label('Scroll to zoom and drag to pan in plot.'),
            Group(
                Item('view_table', show_label=False),
                Item('previous_plot', show_label=False),
                Item('next_plot', show_label=False),
                Item('flip', show_label=True),
                orientation="horizontal",
                ),
            layout="normal",
            ),
        resizable=True,
        handler=TitleHandler(),
        # kind = 'nonmodal',
        width = .5,
        height = .7,
        buttons = ["OK"]
        )



if __name__ == '__main__':
    print("Test start")
    from tests.conftest import conj_res
    res = conj_res()

    # mep = MainEffectsPlot(res, 'Flavour', None)
    # pw = LinePlotWindow(plot=mep)
    # pw.configure_traits()
    # iap = InteractionPlot(res, 'Sex', 'Flavour')
    iap = InteractionPlot(res, 'Flavour', 'Sex')
    pw = InteractionPlotWindow(plot=iap)
    pw.configure_traits()
    print("The end")
