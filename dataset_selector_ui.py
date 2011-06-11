
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


    # Called when some value in object changes
    def setattr(self, info, object, name, value):
        super(DatasetSelectorHandler, self).setattr(
            info, object, name, value)
        logging.info("setattr: %s change to %s", name, value)


    def handler_nameSetX_changed(self, info):
        info.object.mother.dsl.selectedSet = []
        selSet = info.object.mother.dsl.getByName(self.nameSetX)
        if selSet:
            info.object.mother.dsl.selectedSet.append(selSet._internalName)
        logging.info("Selection list updated: %s", info.object.mother.dsl.selectedSet)


    def init(self, info):
        self._buildSelectionList(info.object.mother.dsl)


    def object_datasetsAltered_changed(self, info):
        logging.info("datasetAltered_changed: activated")
        self._buildSelectionList(info.object.mother.dsl)


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
    resizable = True,
    handler = DatasetSelectorHandler,
    )
