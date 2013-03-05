
"""This shows a table editor which has a checkbox column in addition to normal
data columns.
"""

#stdlib imports
import logging

# Enthoughg imports
from traits.api import HasStrictTraits, Str, List, Bool, Event
from traitsui.api import View, Handler, Item, TableEditor
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn


# Create a specialized column to set the text color differently based upon
# whether or not the dataset is in the is selected:
class DatasetColumn ( ObjectColumn ):

    # Override some default settings for the column:
    width                = 0.08
    horizontal_alignment = 'center'

    def get_text_color ( self, obj ):
        return [ 'light grey', 'black' ][ obj.isSelected ]


# The 'datasets' trait table editor:
dataset_editor = TableEditor(
    sortable     = False,
    configurable = False,
    auto_size    = False,
    selection_mode = 'row',
    selected = 'handler.clicked',
    columns      = [ CheckboxColumn( name  = 'isSelected',
                                 label = 'Selected',
                                 width = 0.12 ),
                 DatasetColumn( name = 'dName',
                                label = 'Dataset name',
                                editable = False,
                                width  = 0.24,
                               horizontal_alignment = 'left' )
                 ]
    )


# 'SelectableDataset' class:
class SelectableDataset ( HasStrictTraits ):

    isSelected = Bool( False )
    dName      = Str
    kName      = Str


class SelectionListHandler( Handler ):
    datasets = List( SelectableDataset )
    clicked = Event()

    def init(self, uiInfo):
        self._populateSelectionList(uiInfo.object.dsc)

    def object_datasetsAltered_changed(self, uiInfo):
        logging.info("datasetAltered_changed: activated")
        if uiInfo.initialized:
            self._populateSelectionList(uiInfo.object.dsc)

    def _populateSelectionList(self, dsc):
        self.datasets = []
        for kName, dName in dsc.id_name_list:
            isSelected = False
            for isHere in dsc.selectedSet:
                if isHere == kName:
                    isSelected = True
            ob = SelectableDataset(
                isSelected = isSelected,
                dName = dName,
                kName = kName)
            self.datasets.append(ob)

    def handler_clicked_changed(self, uiInfo):
        uiInfo.object.dsc.selectedSet = []
        for ob in uiInfo.handler.datasets:
            if ob.isSelected:
                uiInfo.object.dsc.selectedSet.append(ob.kName)

        logging.info("Selection list updated: %s", uiInfo.object.dsc.selectedSet)


selection_list_view = View(
    Item( 'handler.datasets',
          show_label = False,
          editor     = dataset_editor
    ),
    title     = 'Selection list',
    handler = SelectionListHandler
)
