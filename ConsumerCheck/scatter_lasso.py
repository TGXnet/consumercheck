""" MixIn for lasso selection
"""
import numpy as np

# Enthought library imports
from chaco.api import LassoOverlay
from chaco.tools.api import LassoSelection, ScatterInspector
import traits.api as tr
# from traits.api import (Bool, Int, List, Long, HasTraits, implements,
#                         Property, Range, Str, Unicode, on_trait_change)
# from traitsui.api import Item, Group, View, Label, Include, CheckListEditor
import traitsui.api as tui

# Local imports



class LassoMixin(tr.HasTraits):
    """
    """

    def overlay_selection(self, plot):
        lasso_selection = LassoSelection(component=plot,
                                         selection_datasource=plot.index,
                                         drag_button="left")
        plot.active_tool = lasso_selection
        plot.tools.append(ScatterInspector(plot))
        lasso_overlay = LassoOverlay(lasso_selection=lasso_selection,
                                     component=plot)
        plot.overlays.append(lasso_overlay)

        # Uncomment this if you would like to see incremental updates:
        # lasso_selection.incremental_select = True
        self.index_datasource = plot.index
        lasso_selection.on_trait_change(self._selection_changed, 'selection_changed')


    def _selection_changed(self):
        mask = self.index_datasource.metadata['selection']
        print("New selection: ")
        # print(np.compress(mask, np.arange(len(mask))))
        labels = self.data.plot_data[0].labels
        print(np.array(labels)[mask])
        # Ensure that the points are printed immediately:
        # sys.stdout.flush()
