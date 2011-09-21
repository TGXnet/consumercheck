
# stdlib imports
import logging

# Enthought imports
from enthought.traits.api import List, Str

from enthought.traits.ui.api import EnumEditor, Handler, Item, View


class DatasetSelectorHandler( Handler ):
    """Handler for dataset view"""

    dsChoices = List(trait = Str)
    nameSetX = Str(label = 'PCA input matrix')


    # Called when some value in object changes
    def setattr(self, info, obj, name, value):
        super(DatasetSelectorHandler, self).setattr(
            info, obj, name, value)
        logging.info("setattr: %s change to %s", name, value)


    def handler_nameSetX_changed(self, info):
        info.object.mother.dsl.selectedSet = []
        selSet = info.object.mother.dsl.get_by_name(self.nameSetX)
        if selSet:
            info.object.mother.dsl.selectedSet.append(selSet._ds_id)
        logging.info("Selection list updated: %s", info.object.mother.dsl.selectedSet)


    def init(self, info):
        self._buildSelectionList(info.object.mother.dsl)


    def object_datasetsAltered_changed(self, info):
        logging.info("datasetAltered_changed: activated")
        self._buildSelectionList(info.object.mother.dsl)


    def _buildSelectionList(self, dsl):
        self.dsChoices = []
        for kName, dName in dsl.id_name_list:
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
