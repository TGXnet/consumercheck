
# Enthought imports
from traits.api import HasTraits, Instance, Enum, Str, List, DelegatesTo, Bool, Set, on_trait_change
from traitsui.api import View, Item, ModelView, InstanceEditor

# Local imports
from combination_table import CombinationTable
from prefmap_mvc import APrefmapHandler, APrefmapModel


class PrefmapsContainer(HasTraits):
    """Prefmap plugin container."""
    name = Str('Define preference mapping')
    # Instance(MainUi)?
    # WeakRef?
    mother_ref = Instance(HasTraits)
    dsl = DelegatesTo('mother_ref')
    mappings = List(APrefmapHandler)

    # Fitting parameters
    standardize = Bool(False)
    max_n_pc = Enum(2,3,4,5,6)


    def add_mapping(self, id_x, id_y):
        set_x = self.dsl.get_by_id(id_x)
        set_y = self.dsl.get_by_id(id_y)
        map_name = id_x + id_y
        mapping_model = APrefmapModel(mother_ref=self, name=map_name,  dsX=set_x, dsY=set_y)
        mapping_handler = APrefmapHandler(mapping_model)
        self.mappings.append(mapping_handler)
        return map_name


    def remove_mapping(self, mapping_id):
        del(self.mappings[self.mappings.index(mapping_id)])



class PrefmapsHandler(ModelView):
    name = DelegatesTo('model')
    # Used by tre editor in ui_tab_prefmap
    mappings = DelegatesTo('model')
    comb = Instance(CombinationTable, CombinationTable())
    # [('a_labels','c_labels'),('sensorydata','consumerliking')]
    last_selection = Set()


    # @on_trait_change('model:dsl:datasets_event', post_init=True)
    ## def _datasets_changed(self, object, name, old, new):
    ##     print("datasets event fired")

    def model_dsl_dataset_event_changed(self, info):
        print("dataset event fired")
        # Sensory on columns
        self.comb.col_set = self.model.dsl.get_id_list_by_type('Sensory profiling')
        # Consumer liking on rows
        self.comb.row_set = self.model.dsl.get_id_list_by_type('Consumer liking')


    @on_trait_change('comb:combination_updated')
    def _handle_selection(self, object, name, old, new):
        print("comb.combination_updated")
        if not self.info:
            return

        selection = set(self.comb.get_selected_combinations())
        if selection.difference(self.last_selection):
            added = selection.difference(self.last_selection)
            self.last_selection = selection
            added = list(added)[0]
            print("Added", added)
            self.model.add_mapping(added[0], added[1])
        elif self.last_selection.difference(selection):
            removed = self.last_selection.difference(selection)
            removed = list(removed)[0]
            print("Removed", removed)
            rem_id = '{0}{1}'.format(removed[0], removed[1])
            self.last_selection = selection
            self.model.remove_mapping(rem_id)
        else:
            return



prefmaps_view = View(
    Item('comb', editor=InstanceEditor(),
         style='custom',
         show_label=False),
    Item('model.standardize'),
    Item('model.max_n_pc'),
    resizable=True,
    height=200,
    width=500,
    )



if __name__ == '__main__':
    print("prefmap container script start")
    import numpy as np
    from tests.conftest import TestContainer

    with np.errstate(invalid='ignore'):
        container = TestContainer()
        model = PrefmapsContainer(mother_ref=container)
        handler = PrefmapsHandler(model=model)
        container.test_subject = handler
        handler.configure_traits(view=prefmaps_view)
