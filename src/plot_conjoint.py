
# SciPy imports
import numpy as np
import pandas as _pd

# Enthought library imports
# FIXME: Namespace import
from traits.api import Bool, Delegate, Dict, Instance, List, on_trait_change, Property, Str
from traitsui.api import Group, Item
from chaco.api import (LabelAxis, DataView, Legend, PlotLabel,
                       ErrorBarPlot, ArrayDataSource,
                       add_default_grids, ScatterPlot, LinePlot,
                       PlotGraphicsContext)
from chaco.tools.api import ZoomTool, PanTool, LegendTool
from chaco.example_support import COLOR_PALETTE


#Local imports
# FIXME: Namespace import
from dataset import DataSet
from plot_base import BasePlot
from plot_windows import SinglePlotWindow



class ConjointBasePlot(BasePlot):
    """Base class for Conjoint plots
    """
    plot_data = Instance(DataSet)
    """The data that is plot
    
    This is a DataSet
    """

    index_labels = List(Str)


    def _label_axis(self):
        idx = range(len(self.index_labels))

        index_axis = LabelAxis(
            component=self,
            mapper=self.index_mapper,
            orientation="bottom",
            tick_weight=1,
            tick_label_rotate_angle = 90,
            labels=self.index_labels,
            positions = idx,
            )

        self.x_axis = index_axis


    def _add_avg_std_err(self, text):
        info_label = PlotLabel(
            text=text,
            component=self,
            overlay_position='outside bottom',
            border_width=4,
            fill_padding=False,
            hjustify='center',
        )
        self.overlays.append(info_label)



class MainEffectsPlot(ConjointBasePlot):
    
    def __init__(self, conj_res, attr_name):
        super(MainEffectsPlot, self).__init__()
        res = slice_main_effect_ds(conj_res.lsmeansTable, attr_name)
        self.plot_data = DataSet(mat=res, display_name='Main effects')
        self.p_value = get_main_p_value(conj_res.anovaTable, attr_name)
        self.average = conj_res.meanLiking
        self.avg_std_err = main_avg_std_err(conj_res.lsmeansTable, attr_name)

        self._make_plot_frame()
        self._label_axis()
        self._add_lines()
        self._add_ci_bars()
        self._add_avg_line()


    def _make_plot_frame(self):
        # Adjust spacing
        self.index_range.tight_bounds = False
        self.index_range.margin = 0.05
        self.value_range.tight_bounds = False

        # Update plot ranges and mappers
        self.index_labels = self.plot_data.obj_n
        index = ArrayDataSource(range(len(self.index_labels)))
        self.index_range.add(index)
        for name in ['values', 'ylow', 'yhigh']:
            value = self.mk_ads(name)
            self.value_range.add(value)

        # Add label with average standar error
        avg_text = "Average standar error: {}".format(self.avg_std_err)
        self._add_avg_std_err(avg_text)


        # FIXME: Join with interaction
        zoom = ZoomTool(self, tool_mode="box", always_on=False)
        pan = PanTool(self)
        self.tools.append(zoom)
        self.tools.append(pan)

        add_default_grids(self)

        # Set border color based on p_value
        self.border_width = 10

        if self.p_value < 0.001:
            self.border_color = (1.0, 0.0, 0.0, 0.8)
        elif self.p_value < 0.01:
            self.border_color = (0.0, 1.0, 0.0, 0.8)
        elif self.p_value < 0.05:
            self.border_color = (1.0, 1.0, 0.0, 0.8)
        else:
            self.border_color = (0.5, 0.5, 0.5, 0.8)


    def _add_lines(self):
        # index = self.mk_ads('index')
        index = ArrayDataSource(range(len(self.index_labels)))
        value = self.mk_ads('values')

        #Create lineplot
        plot_line = LinePlot(
            index=index, index_mapper=self.index_mapper,
            value=value, value_mapper=self.value_mapper,
            name='line')

        #Add datapoint enhancement
        plot_scatter = ScatterPlot(
            index=index, index_mapper=self.index_mapper,
            value=value, value_mapper=self.value_mapper,
            color="blue", marker_size=5,
            name='scatter',
        )

        self.add(plot_line, plot_scatter)


    def _add_ci_bars(self):
        #Create vertical bars to indicate confidence interval
        # index = self.mk_ads('index')
        index = ArrayDataSource(range(len(self.index_labels)))
        value_lo = self.mk_ads('ylow')
        value_hi = self.mk_ads('yhigh')

        plot_ci = ErrorBarPlot(
            index=index, index_mapper=self.index_mapper,
            value_low = value_lo, value_high = value_hi,
            value_mapper = self.value_mapper,
            border_visible=True,
            name='CIbars')

        self.add(plot_ci)


    def _add_avg_line(self):
        #Create averageplot
        # idx = self.plot_data.mat['index']
        idx = range(len(self.index_labels))
        span = idx[-1] - idx[0]
        index = ArrayDataSource([idx[0] - span, idx[-1] + span])

        avg = self.average
        value = ArrayDataSource([avg, avg])
        # value = self.mk_ads('average')

        plot_average = LinePlot(
            index=index, index_mapper=self.index_mapper,
            value=value, value_mapper=self.value_mapper,
            color='green',
            name='average',
        )

        self.add(plot_average)


    def mk_ads(self, name):
        return ArrayDataSource(self.plot_data.mat[name].values)



class InteractionPlot(ConjointBasePlot):

    # LinPlot name to LinPlot mapper
    # Used by Plot legend
    plots = Dict(Str, LinePlot)


    def __init__(self, conj_res, attr_one_name, attr_two_name):
        super(InteractionPlot, self).__init__()
        res = slice_interaction_ds(conj_res.lsmeansTable, attr_one_name, attr_two_name)
        self.plot_data = DataSet(mat=res, display_name='Interaction')
        self.p_value = get_interaction_p_value(conj_res.anovaTable, attr_one_name, attr_two_name)
        self.avg_std_err = inter_avg_std_err(conj_res.lsmeansTable, attr_one_name, attr_two_name)
        self.plot_interaction()


    def plot_interaction(self, flip=False):
        self._nullify_plot()
        self._make_plot_frame()
        self._add_lines(flip)
        self._label_axis()
        self._add_line_legend()


    def _make_plot_frame(self):
        # Adjust spacing
        self.index_range.tight_bounds = False
        self.index_range.margin = 0.05
        self.value_range.tight_bounds = False

        self.tools.append(PanTool(self))
        self.tools.append(ZoomTool(self))

        # Set border color
        self.border_width = 10

        if self.p_value < 0.001:
            self.border_color = (1.0, 0.0, 0.0, 0.8)
        elif self.p_value < 0.01:
            self.border_color = (0.0, 1.0, 0.0, 0.8)
        elif self.p_value < 0.05:
            self.border_color = (1.0, 1.0, 0.0, 0.8)
        else:
            self.border_color = (0.5, 0.5, 0.5, 0.8)


    def _nullify_plot(self):
        # Nullify all plot related list to make shure we can
        # make the ploting idempotent
        self.plot_components = []
        self.plots = {}
        self.index_range.sources = []
        self.value_range.sources = []
        self.tools = []
        self.overlays = []
        self.overlays.append(self._title)
        # Add label with average standar error
        avg_text = "Average standar error: {}".format(self.avg_std_err)
        self._add_avg_std_err(avg_text)


    def _add_lines(self, flip=False):
        # When non fliped is index objects
        if flip:
            self.index_labels = self.plot_data.var_n
            pl_itr = self.plot_data.mat.iterrows()
        else:
            self.index_labels = self.plot_data.obj_n
            pl_itr = self.plot_data.mat.iteritems()
        idx = ArrayDataSource(range(len(self.index_labels)))
        self.index_range.add(idx)

        line_styles = ['solid', 'dot dash', 'dash', 'dot', 'long dash']
        i = 0
        for name, vec in pl_itr:
            i += 1
            vals = ArrayDataSource(vec.values)
            self.value_range.add(vals)
            plot = LinePlot(index=idx, index_mapper=self.index_mapper,
                            value=vals, value_mapper=self.value_mapper,
                            color=COLOR_PALETTE[i], line_style=line_styles[i%4]
            )
            self.add(plot)
            self.plots[name] = plot


    def _add_line_legend(self):
        # Add a legend in the upper right corner, and make it relocatable
        legend = Legend(
            component=self,
            padding=10,
            align="ur",
            plots=self.plots,
        )
        legend.tools.append(LegendTool(legend, drag_button="right"))
        self.overlays.append(legend)



class InteractionPlotWindow(SinglePlotWindow):
    """Window for embedding line plot

    """
    flip = Bool(False)

    @on_trait_change('flip')
    def flip_interaction(self, obj, name, new):
        obj.plot.plot_interaction(new)

    extra_gr = Group(Item('flip'))



def slice_main_effect_ds(ls_means_table, attr_name):
    # FIXME: Use proper Pandas DataFrame indexing
    ls_means = ls_means_table.mat
    ls_means_labels = ls_means_table.mat.index
    cn = list(ls_means_table.mat.columns)
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

    ls_label_names = []
    for i, pl in enumerate(selected_labels):
        ls_label_names.append(pl)

    pd = _pd.DataFrame(index=ls_label_names)
    # pd['index'] = [int(val) for val in selected[attr_name]]
    pd['values'] = [float(val) for val in selected['Estimate']]
    pd['ylow'] = [float(val) for val in selected['Lower CI']]
    pd['yhigh'] = [float(val) for val in selected['Upper CI']]
    # pd['average'] = [conj_res.meanLiking for val in selected[attr_name]]

    return pd


def slice_interaction_ds(ls_means_table, index_attr, line_attr):
    # FIXME: Use proper Pandas DataFrame indexing
    ls_means = ls_means_table.mat

    picker_one = ls_means[index_attr] != 'NA'
    picker_two = ls_means[line_attr] != 'NA'
    # Picker is an boolean selction vector
    picker = np.logical_and(picker_one, picker_two)
    selected = ls_means[picker][[index_attr, line_attr, 'Estimate']]

    lines = sorted(list(set(selected[line_attr])))
    indexes = sorted(list(set(selected[index_attr])))
    index_labels = ['{0} {1}'.format(index_attr, i) for i in indexes]

    # for hvert nytt plot trenger vi bare et nytt dataset
    vals = []
    for i, line in enumerate(lines):
        line_data_picker = selected[line_attr] == line
        line_data = selected[line_data_picker]
        vals.append([float(val) for val in line_data['Estimate']])
    ln = ["{0} {1}".format(line_attr, line) for line in lines]
    res = _pd.DataFrame(vals, index=ln, columns=index_labels)

    return res


def get_main_p_value(anova_table, attr_name):
    # Get p value for attribute
    anova_values = anova_table.mat
    anova_names = anova_table.mat.index
    picker = anova_names == attr_name
    # Check if it is only one bool value
    if isinstance(picker, bool):
        picker = np.array([picker])
    var_row = anova_values[picker]
    p_str = var_row['Pr(>F)'][0]
    try:
        p_value = float(p_str)
    except ValueError:
        p_value = 0.0

    return p_value


def get_interaction_p_value(anova_table, index_attr, line_attr):
    # Get p value for attribute
    anova_values = anova_table.mat
    anova_names = anova_table.mat.index
    try:
        attr_name = "{0}:{1}".format(index_attr, line_attr)
        var_row = anova_values[anova_names == attr_name]
        p_str = var_row['Pr(>F)'][0]
    except IndexError:
        attr_name = "{0}:{1}".format(line_attr, index_attr)
        var_row = anova_values[anova_names == attr_name]
        p_str = var_row['Pr(>F)'][0]
    try:
        p_value = float(p_str)
    except ValueError:
        p_value = 0.0
    
    return p_value


def main_avg_std_err(ls_means_table, var_name):
    picker = lsmeans_main_selector(ls_means_table.mat, var_name)
    std_err_vec = ls_means_table.mat.loc[picker, 'Standard Error']
    mean_std_err = std_err_vec.mean()
    return mean_std_err


def lsmeans_main_selector(df, var_name):
    # All column labels
    acl = df.columns
    # Result column labels
    rcl = _pd.Index([u'Estimate', u'Standard Error', u'DF', u't-value',
                     u'Lower CI', u'Upper CI', u'p-value'])
    # Selection column labels
    # Set arithmetic
    scl = acl - rcl - [var_name]

    # Picker
    p1 = df.loc[:,scl] == 'NA'
    p2 = p1.all(axis=1)

    return p2


def inter_avg_std_err(ls_means_table, var1_name, var2_name):
    picker = lsmeans_inter_selector(ls_means_table.mat, var1_name, var2_name)
    std_err_vec = ls_means_table.mat.loc[picker, 'Standard Error']
    mean_std_err = std_err_vec.mean()
    return mean_std_err


def lsmeans_inter_selector(df, var1_name, var2_name):
    vcl = [var1_name, var2_name]
    # Picker
    p1 = df.loc[:,vcl] != 'NA'
    p3 = p1.all(axis=1)

    return p3



if __name__ == '__main__':
    print("Test start")
    from tests.conftest import conj_res
    res = conj_res()

    mep = MainEffectsPlot(res, 'Flavour')
    spw = SinglePlotWindow(plot=mep)
    print(spw.plot.plot_data.mat)
    spw.configure_traits()
    iap = InteractionPlot(res, 'Sex', 'Flavour')
    ipw = InteractionPlotWindow(plot=iap)
    print(ipw.plot.plot_data.mat)
    ipw.configure_traits()
    print("The end")
