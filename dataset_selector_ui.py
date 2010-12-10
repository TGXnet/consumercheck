# -*- coding: utf-8 -*-

# stdlib imports
import logging

# Enthought imports
from enthought.traits.api \
    import List, Str, Bool

from enthought.traits.ui.api \
    import EnumEditor, Handler, Item, View


class DatasetSelectorHandler( Handler ):
    """Handler for dataset view"""

    dsChoices = List(trait = Str)
    nameSetX = Str(label = 'PCA input matrix')
    eqPlotAxis = Bool(False)


    # Called when some value in object changes
    def setattr(self, info, object, name, value):
        super(DatasetSelectorHandler, self).setattr(
            info, object, name, value)
        logging.info("setattr: %s change to %s", name, value)


    def handler_nameSetX_changed(self, info):
        info.object.dsl.selectedSet = []
        selSet = info.object.dsl.retriveDatasetByDisplayName(self.nameSetX)
        if selSet:
            info.object.dsl.selectedSet.append(selSet._internalName)
        logging.info("Selection list updated: %s", info.object.dsl.selectedSet)


    def handler_eqPlotAxis_changed(self, info):
        info.object.dsl.eqPlotAxis = self.eqPlotAxis
        logging.info("eqPlotAxix changed")


    def init(self, info):
        self._buildSelectionList(info.object.dsl)


    def object_datasetsAltered_changed(self, info):
        logging.info("datasetAltered_changed: activated")
        self._buildSelectionList(info.object.dsl)


    def _buildSelectionList(self, dsl):
        self.dsChoices = []
        for kName, dName in dsl.indexNameList:
            self.dsChoices.append(dName)
        self._initChoices(dsl)


    def _initChoices(self, dsl):
        if len(dsl.selectedSet) > 0:
            self.nameSetX = dsl.selectedSet[0]
        elif len(self.dsChoices) > 0:
            self.nameSetX = self.dsChoices[0]

# end DatasetSelectorHandler


dataset_selector = View(
    Item('handler.nameSetX',
         editor = EnumEditor(name = 'handler.dsChoices'),
         ),
    Item('handler.eqPlotAxis'),
    resizable = True,
    handler = DatasetSelectorHandler,
    )
