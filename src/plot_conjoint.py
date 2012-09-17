
# SciPy imports
import numpy as np

# Enthought library imports
from chaco.api import Plot, ArrayPlotData
from traits.api import List, HasTraits, implements
from enable.api import ColorTrait
from chaco.tools.api import ZoomTool, PanTool


class MainEffectsPlot(Plot):

    def __init__(self, conj_res, attr_name):
        super(MainEffectsPlot, self).__init__()
        self._adapt_conj_main_effect_data(conj_res, attr_name)


    def _adapt_conj_main_effect_data(self, conj_res, attr_name):
        ls_means = conj_res['lsmeansTable']['data']
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
        apd = ArrayPlotData()
        apd.set_data('index', [int(val) for val in selected[attr_name]])
        apd.set_data('values', [float(val) for val in selected[' Estimate ']])
        self.data = apd
        self.plot(('index', 'values'), type='line')



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
    import pickle
#    from conjoint_machine import ConjointMachine
#    from tests.conftest import make_dsl_mock
#    dsl = make_dsl_mock()
#    consAttr = dsl.get_by_id('consumerattributes')
#    odflLike = dsl.get_by_id('odour-flavour_liking')
#    consistencyLike = dsl.get_by_id('consistency_liking')
#    overallLike = dsl.get_by_id('overall_liking')
#    designVar = dsl.get_by_id('design')
#    selected_structure = 2
#    selected_consAttr = ['Sex']
#    selected_designVar = ['Flavour', 'Sugarlevel']
#    consLiking = odflLike
#
#    cm = ConjointMachine()
#    res = cm.synchronous_calculation(selected_structure,
#                                 consAttr, selected_consAttr,
#                                 designVar, selected_designVar,
#                                 consLiking)
#    with open('precomp.pkl', 'w') as fp:
#        pickle.dump(res, fp)

    with open('precomp.pkl', 'r') as fp:
        res = pickle.load(fp)

    mep = MainEffectsPlot(res, 'Sex')
    mep.new_window(True)
#    iap = InteractionPlot(res, 'Sex', 'Sugarlevel')
#    iap.new_window(True)
    print("The end")
