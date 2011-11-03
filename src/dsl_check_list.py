
# stdlib imports
import logging

from traits.api import List, on_trait_change
from traits.ui.api import Item, View, CheckListEditor, Controller


# Define the demo class:
class CheckListController(Controller):
    """ Define the main CheckListEditor demo class.

    The model attribute have to be set to the dataset collection (dsl)
    object in this object constructor.
    FIXME: Compare with prefmapUIController to equalize API for dataset collection
    """
#    sel_list = DelegatesTo('model', prefix='id_name_list')
    sel_list = List()

    # Define a trait for each of three formations:
    selected = List(
        editor = CheckListEditor(
            name = 'sel_list',
            cols = 1 )
        )

    @on_trait_change('model.[ds_name_event,datasets_event]')
    def _update_selection(self, obj, name, new):
        datasets = self.model.get_dataset_list()
        self.sel_list =  [(ds._ds_id, ds._ds_name) for ds in datasets]



    def _selected_changed(self, old, new):
        logging.info("Selection list changed from {0} to {1}".format(old, new))


# The view includes one group per column formation.      These will be displayed
# on separate tabbed panels.
check_view = View(
    Item('handler.selected', style='custom', show_label=False),
    resizable = True
)
