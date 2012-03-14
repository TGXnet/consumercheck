
# Enthought imports
from traits.api import HasTraits, Instance, Enum, Str, List, DelegatesTo, Bool, Set, on_trait_change
from traitsui.api import View, Group, Item, ModelView, InstanceEditor

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
    ds_event = DelegatesTo('mother_ref')
    dsname_event = DelegatesTo('mother_ref')
    mappings = List(APrefmapHandler)

    # Fitting parameters
    standardize = Bool(False)
    max_n_pc = Enum(2,3,4,5,6)


    def add_mapping(self, id_x, id_y):
        set_x = self.dsl.get_by_id(id_x)
        set_y = self.dsl.get_by_id(id_y)
        map_id = id_x+id_y
        map_name = set_x._ds_name + ' - ' + set_y._ds_name
        mapping_model = APrefmapModel(mother_ref=self, nid=map_id, name=map_name,  dsX=set_x, dsY=set_y)
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

    def update_comb(self):
        sens_list = []
        cons_list = []
        for a in self.model.dsl.get_id_list_by_type('Sensory profiling'):
            sens_list.append((a,self.model.dsl.get_by_id(a)._ds_name))
        # Consumer liking on rows
        for b in self.model.dsl.get_id_list_by_type('Consumer liking'):
            cons_list.append((b,self.model.dsl.get_by_id(b)._ds_name))
        
        self.comb.col_set = sens_list
        self.comb.row_set = cons_list

    def model_dsname_event_changed(self, info):
        self.update_comb()
        self.comb.update_names()

    def model_ds_event_changed(self, info):
        self.update_comb()
        self.comb._generate_combinations()


    @on_trait_change('comb:combination_updated')
    def _handle_selection(self, object, name, old, new):
        if not self.info:
            return

        selection = self.comb.get_selected_combinations()
        name_to_id = []
        for combinations in selection:
            name_to_id.append(combinations)
                
        selection = set(name_to_id)
        
        if selection.difference(self.last_selection):
            added = selection.difference(self.last_selection)
            self.last_selection = selection
            added = list(added)[0]
            self.model.add_mapping(added[0], added[1])
        elif self.last_selection.difference(selection):
            removed = self.last_selection.difference(selection)
            removed = list(removed)[0]
            rem_id = '{0}{1}'.format(removed[0],removed[1])
            self.last_selection = selection
            self.model.remove_mapping(rem_id)
        else:
            return



prefmaps_view = View(
    Group(
        Group(
            Group(
                Item('comb', editor=InstanceEditor(),
                     style='custom',
                     show_label=False),
                label='Select Prefmap combinations',
                show_border=True,
                ),
            Item('', springy=True),
            orientation='horizontal',
            ),
        Group(
            Group(
                Item('model.standardize'),
                Item('model.max_n_pc'),
                orientation='vertical',
                label='Prototype Prefmap settings',
                show_border=True,
                ),
            orientation='horizontal',
            springy=True,
            ),
        orientation='vertical',
        ),
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
