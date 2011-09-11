
# stdlib imports
import logging

# Enthought imports
from traits.api import Str, List, DelegatesTo
from traitsui.api import View, Group, Item, Handler, EnumEditor, Controller


# Define the demo class:
class PrefmapSelectorController(Controller):
    """ Preference mapping selection tool

    The model attribute have to be set to the dataset collection (dsl)
    object in this object constructor.
    """
    # sel_list = DelegatesTo('model', prefix='indexNameList')
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
        for ds in self.model.getDatasetList():
            if ds._datasetType in ['Sensory profiling', 'Consumer liking']:
                self.dsChoices.append(ds._ds_name)

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
        self._update_mappings()

    def _yName_changed(self, name, old, new):
        self._update_mappings()

    def _update_mappings(self):
        dsx_id = ''
        dsy_id = ''
        if self.xName:
            dsx_id = self.model.idByName(self.xName)
        if self.yName:
            dsy_id = self.model.idByName(self.yName)
        self.xyMappings = [(dsx_id, dsy_id)]

# The view includes one group per column formation.      These will be displayed
# on separate tabbed panels.
prefmap_selector_view = View(
    Item('handler.xName'),
    Item('handler.yName'),
    resizable = True
)


if __name__ == '__main__':
    """Test run the View"""
    print("Interactive start")
    from dataset_collection import DatasetCollection
    from file_importer import FileImporter
    
    dsl = DatasetCollection()
    fi = FileImporter()
    dsl.addDataset(fi.noninteractiveImport('datasets/A_labels.txt'))
    dsl.addDataset(fi.noninteractiveImport('datasets/C_labels.txt'))
    dsl.addDataset(fi.noninteractiveImport('datasets/Ost_forbruker.txt'))
    dsl.addDataset(fi.noninteractiveImport('datasets/Ost_sensorikk.txt'))
    dsl._dataDict['a_labels']._ds_name = 'Set A tull'
    dsl._dataDict['c_labels']._ds_name = 'Set C tull'
    dsl._dataDict['ost_forbruker']._ds_name = 'Forbruker'
    dsl._dataDict['ost_forbruker']._datasetType = 'Consumer liking'
    dsl._dataDict['ost_sensorikk']._ds_name = 'Sensorikk'
    dsl._dataDict['ost_sensorikk']._datasetType = 'Sensory profiling'
    selector = PrefmapSelectorController(model=dsl)
    selector.configure_traits(view=prefmap_selector_view)
    
