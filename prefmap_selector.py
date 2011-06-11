
# stdlib imports
import logging

# Enthought imports
from enthought.traits.api import Str, List, Enum, Bool, DelegatesTo
from enthought.traits.ui.api import View, Group, Item, Handler, EnumEditor, CheckListEditor, Controller


# Define the demo class:
class PrefmapSelectorController(Controller):
    """ Preference mapping selection tool

    The model attribute have to be set to the dataset collection (dsl)
    object in this object constructor.
    """
    sel_list = DelegatesTo('model', prefix='indexNameList')
    dsChoices = List(trait = Str)
    xyMappings = List()
    xName = Str(
        label = 'Sensory profiling (X)',
        editor = EnumEditor(name = 'dsChoices'),
        )
    yName = Str(
        label = 'Consumer (Y)',
        editor = EnumEditor(name = 'dsChoices'),
        )

    def init(self, info):
        self._buildSelectionList()
        # self._initChoices(info.object)

    ## def object_datasetsAltered_changed(self, info):
    ##     self._buildSelectionList(info.object.dsl)
    ##     self._initChoices(info.object)

    def _buildSelectionList(self):
        self.dsChoices = []
        for kName, dName in self.sel_list:
            self.dsChoices.append(dName)

    ## def _initChoices(self, obj):
    ##     if (len(self.dsChoices) > 0) and (not self.nameSetX or not self.nameSetY):
    ##         if obj.setX:
    ##             self.nameSetX = obj.setX._ds_name
    ##         else:
    ##             self.nameSetX = self.dsChoices[0]
    ##         if obj.setY:
    ##             self.nameSetY = obj.setY._ds_name
    ##         else:
    ##             self.nameSetY = self.dsChoices[0]

    def _xName_changed(self, name, old, new):
        self.xyMappings = [(self.xName, self.yName)]
        logging.info("{0} changed from {1} to {2}".format(name, old, new))
        print(self.xyMappings)

    def _yName_changed(self, name, old, new):
        self.xyMappings = [(self.xName, self.yName)]
        logging.info("{0} changed from {1} to {2}".format(name, old, new))
        print(self.xyMappings)


# The view includes one group per column formation.      These will be displayed
# on separate tabbed panels.
prefmap_selector_view = View(
    Item('handler.xName'),
    Item('handler.yName'),
    resizable = True
)
