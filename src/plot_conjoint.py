
# SciPy imports
import numpy as np

# Enthought library imports
from chaco.api import Plot, ArrayPlotData, LabelAxis, OverlayPlotContainer, ErrorBarPlot, ArrayDataSource, LinearMapper,DataRange1D, add_default_axes, add_default_grids
from chaco.tools.api import ZoomTool

from plugin_tree_helper import WindowLauncher
from plot_windows import SinglePlotWindow, LinePlotWindow


class MainEffectsPlot(OverlayPlotContainer):
    def __init__(self, conj_res, attr_name, pl_ref):
        super(MainEffectsPlot, self).__init__()
        self.bgcolor = "lightgray"
        self.use_backbuffer=True
        
        self.pl_ref = pl_ref
        self._adapt_conj_main_effect_data(conj_res, attr_name)
        self._create_lineplot()
        self._create_errorplot()
        self._create_dottplott()
        

    def _adapt_conj_main_effect_data(self, conj_res, attr_name):
        ls_means = conj_res['lsmeansTable']['data']
        ls_means_labels = conj_res['lsmeansTable']['rowNames']
        cn = list(conj_res['lsmeansTable']['colNames'])
        nli = cn.index('Estimate')
        cn = cn[:nli]
        exclude = []
        for col in cn:
            if col == attr_name:
                continue
            else:
                exclude.append(ls_means[col] != 'NA')
        picker = ls_means[attr_name] != 'NA'
        
        for out in exclude:
            picker = np.logical_and(picker, np.logical_not(out))
        selected = ls_means[picker][[attr_name, ' Estimate ']]
        selected_labels = ls_means_labels[picker]
                
        self.ls_label_names = []
        self.ls_label_pos = []
        for i, pl in enumerate(selected_labels):
            self.ls_label_names.append(pl)
            self.ls_label_pos.append(i+1)
        
        self.apd = ArrayPlotData()
        self.apd.set_data('index', [int(val) for val in selected[attr_name]])
        self.apd.set_data('values', [float(val) for val in selected[' Estimate ']])
        self.apd.set_data('ylow', [float(val)-.1 for val in selected[' Estimate ']])
        self.apd.set_data('yhigh', [float(val)+.1 for val in selected[' Estimate ']])
        self.ads_x = ArrayDataSource(self.apd.arrays['index'])
        self.ads_y = ArrayDataSource(self.apd.arrays['values'])
        self.ads_yl = ArrayDataSource(self.apd.arrays['ylow'])
        self.ads_yh = ArrayDataSource(self.apd.arrays['yhigh'])

        
    def _create_lineplot(self):
        plot1 = Plot(self.apd)
        plot1.legend.visible = False
        y_name = "line"
        plot1.plot(('index', 'values'), color="black", name=y_name, line_width=1)            
        self.x_axis = plot1.x_axis = LabelAxis(plot1,
                            orientation="bottom",
                            tick_weight=1,
                            tick_label_rotate_angle = 90,
                            labels=self.ls_label_names,
                            positions = self.ls_label_pos,
                            )
        self.add(plot1)
        
    def _create_errorplot(self):
        index_range = DataRange1D(self.ads_x)
        index_mapper = LinearMapper(range=index_range)
        value_range = DataRange1D(self.ads_yl, self.ads_yh)
        value_mapper = LinearMapper(range=value_range)
        plot2 = ErrorBarPlot(index= self.ads_x, index_mapper=index_mapper,
                         value_low =  self.ads_yl,
                         value_high =  self.ads_yh,
                         value_mapper = value_mapper,
                         border_visible = True,
                        )
        add_default_axes(plot2)
        add_default_grids(plot2)
        self.add(plot2)
        

    def _create_dottplott(self):
        plot3 = Plot(self.apd)
        plot3.legend.visible = False
        y_name='points'
        plot3.plot(('index', 'values'), color="blue", type='scatter', marker_size=5, name=y_name, line_width=1)[0]
        plot3.x_axis = self.x_axis
        self.add(plot3)     
    
class InteractionPlot(Plot):

    def __init__(self, conj_res, attr_one_name, attr_two_name):
        super(InteractionPlot, self).__init__()
        self._adapt_conj_interaction_data(conj_res, attr_one_name, attr_two_name)


    def _adapt_conj_interaction_data(self, conj_res, attr_one_name, attr_two_name):
        """
        attr_one_name: Index axis
        attr_two_name: Lines
        """
        self.attr_one_name = attr_one_name
        self.attr_two_name = attr_two_name
        ls_means = conj_res['lsmeansTable']['data']
        print(ls_means)
        print(attr_one_name, attr_two_name)
        picker_one = ls_means[attr_one_name] != 'NA'
        picker_two = ls_means[attr_two_name] != 'NA'
        picker = np.logical_and(picker_one, picker_two)
        self.selected = ls_means[picker][[attr_one_name, attr_two_name, ' Estimate ']]
        lines = set(self.selected[attr_two_name])

        self.data = ArrayPlotData()
        line_data_picker = self.selected[self.attr_two_name] == list(lines)[0]
        line_data = self.selected[line_data_picker]
        self.data.set_data('index', [int(val) for val in line_data[attr_one_name]])

        for line in lines:
            self._plot_line(line)


    def _plot_line(self, line):
        line_data_picker = self.selected[self.attr_two_name] == line
        line_data = self.selected[line_data_picker]
        self.data.set_data('line{}'.format(line), [float(val) for val in line_data[' Estimate ']])
        self.plot(('index', 'line{}'.format(line)), type='line', name='lp{}'.format(line))


if __name__ == '__main__':
    print("Test start")
    from tests.conftest import conj_res
    res = conj_res()
    
    mep = MainEffectsPlot(res, 'Flavour', None)
    
    pw = LinePlotWindow(plot=mep)
    pw.configure_traits()
    #mep.new_window(True)
#    iap = InteractionPlot(res, 'Sex', 'Sugarlevel')
#    iap.new_window(True)
    print("The end")
