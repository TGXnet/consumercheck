
# stdlib imports
import logging


# Enthought imports
from enthought.traits.api import Str, List, Enum, Bool
from enthought.traits.ui.api import View, Item, Group, Handler, EnumEditor


class PrefmapControlHandler( Handler ):
    """Handler for dataset view"""

    dsChoices = List(trait = Str)
    nameSetX = Str(label = 'Sensory profiling (X)')
    nameSetY = Str(label = 'Consumer (Y)')
#    validate = Enum('None', ['None', 'Full cross'], label = 'Validation')
    eqPlotAxis = Bool(False)


    # Called when some value in object changes
    def setattr(self, info, object, name, value):
        super(PrefmapControlHandler, self).setattr(
            info, object, name, value)
        logging.info("setattr: %s change to %s", name, value)


    def handler_nameSetX_changed(self, info):
        info.object.setX = info.object.dsl.retriveDatasetByDisplayName(self.nameSetX)


    def handler_nameSetY_changed(self, info):
        info.object.setY = info.object.dsl.retriveDatasetByDisplayName(self.nameSetY)


    def handler_eqPlotAxis_changed(self, info):
        info.object.eqPlotAxis = self.eqPlotAxis


    def init(self, info):
        self._buildSelectionList(info.object.dsl)
        self._initChoices(info.object)


    def object_datasetsAltered_changed(self, info):
        self._buildSelectionList(info.object.dsl)
        self._initChoices(info.object)


    def _buildSelectionList(self, dsl):
        self.dsChoices = []
        for kName, dName in dsl.indexNameList:
            self.dsChoices.append(dName)


    def _initChoices(self, obj):
        if (len(self.dsChoices) > 0) and (not self.nameSetX or not self.nameSetY):
            if obj.setX:
                self.nameSetX = obj.setX._displayName
            else:
                self.nameSetX = self.dsChoices[0]
            if obj.setY:
                self.nameSetY = obj.setY._displayName
            else:
                self.nameSetY = self.dsChoices[0]

# end PrefmapControlHandler



prefmap_control = View(
    Item('handler.nameSetX',
         editor = EnumEditor(name = 'handler.dsChoices'),
         ),
    Item('handler.nameSetY',
         editor = EnumEditor(name = 'handler.dsChoices'),
         ),
#    Item('handler.validate'),
    Item('handler.eqPlotAxis'),
    resizable = True,
    handler = PrefmapControlHandler,
    )
