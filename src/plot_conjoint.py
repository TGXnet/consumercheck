# SciPy imports
import numpy as np

# Enthought library imports
from chaco.api import (Plot, ArrayPlotData, LabelAxis, DataView,
                       ErrorBarPlot, ArrayDataSource, LinearMapper,DataRange1D,
                       add_default_grids, ScatterPlot, LinePlot, PlotAxis)
from chaco.tools.api import ZoomTool, PanTool

#Local imports
from plot_windows import LinePlotWindow


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
            self.ls_label_pos.append(i+1)


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
            positions = self.ls_label_pos)

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


class InteractionPlot(Plot):
    def __init__(self, conj_res, attr_one_name, attr_two_name):
        super(InteractionPlot, self).__init__()
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
        self.selected = ls_means[picker][[self.index_attr, self.line_attr, ' Estimate ']]
        lines = set(self.selected[self.line_attr])

        self.data = ArrayPlotData()
        line_data_picker = self.selected[self.line_attr] == list(lines)[0]
        line_data = self.selected[line_data_picker]
        self.data.set_data('index', [int(val) for val in line_data[self.index_attr]])

        for line in lines:
            self._plot_line(line)


    def _plot_line(self, line):
        line_data_picker = self.selected[self.line_attr] == line
        line_data = self.selected[line_data_picker]
        self.data.set_data('line{}'.format(line), [float(val) for val in line_data[' Estimate ']])
        self.plot(('index', 'line{}'.format(line)), type='line', name='lp{}'.format(line))


if __name__ == '__main__':
    print("Test start")
    from tests.conftest import conj_res
    res = conj_res()

    # mep = MainEffectsPlot(res, 'Flavour', None)
    # pw = LinePlotWindow(plot=mep)
    # pw.configure_traits()
    # iap = InteractionPlot(res, 'Sex', 'Flavour')
    iap = InteractionPlot(res, 'Flavour', 'Sex')
    pw = LinePlotWindow(plot=iap)
    pw.configure_traits()
    print("The end")
