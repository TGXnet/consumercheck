
# Enthought imports
from traits.api import HasTraits, Instance, Int, Str, List, DelegatesTo, Bool, Set, on_trait_change, Enum
from traitsui.api import View, Group, Item, ModelView, InstanceEditor, RangeEditor, EnumEditor


# Local imports
from combination_table import CombinationTable
from prefmap_mvc import APrefmapHandler, APrefmapModel


class PrefmapsContainer(HasTraits):
    """Prefmap plugin container."""
    name = Str('Prefmap results')
    # Instance(MainUi)?
    # WeakRef?
    mother_ref = Instance(HasTraits)
    dsl = DelegatesTo('mother_ref')
    mappings = List(APrefmapHandler)

    # Fitting parameters
    standardise = Bool(False)
    pc_to_calc = Int(2)
    radio = Enum('Internal mapping', 'External mapping')


    def add_mapping(self, id_c, id_s):
        ''' Add a preference mapping object

        id_c - Consumer dataset id
        id_s - Sensory dataset id
        '''
        ds_c = self.dsl.get_by_id(id_c)
        ds_s = self.dsl.get_by_id(id_s)
        map_id = id_c+id_s
        map_name = ds_c._ds_name + ' - ' + ds_s._ds_name
        mapping_model = APrefmapModel(
            mother_ref=self, nid=map_id, name=map_name,  ds_C=ds_c, ds_S=ds_s)
        mapping_handler = APrefmapHandler(mapping_model)
        self.mappings.append(mapping_handler)
        return map_name


    def remove_mapping(self, mapping_id):
        del(self.mappings[self.mappings.index(mapping_id)])


class PrefmapsHandler(ModelView):
    name = DelegatesTo('model')
    # Used by tre editor in ui_tab_prefmap
    mappings = DelegatesTo('model')
    pc_to_calc = DelegatesTo('model')
    comb = Instance(CombinationTable, CombinationTable())
    radio = DelegatesTo('model')
    # [('a_labels','c_labels'),('sensorydata','consumerliking')]
    last_selection = Set()
       
        
    @on_trait_change('model:mother_ref:dsname_event')
    def dsname_changed(self):
        self._update_comb()
        self.comb.update_names()


    @on_trait_change('model:mother_ref:ds_event')
    def dsl_changed(self):
        self._update_comb()
        self.comb._generate_combinations()


    def _update_comb(self):
        sens_list = []
        cons_list = []
        
        for a in self.model.dsl.get_id_list_by_type('Sensory profiling'):
            sens_list.append((a, self.model.dsl.get_by_id(a)._ds_name))
        for b in self.model.dsl.get_id_list_by_type('Consumer liking'):
            cons_list.append((b, self.model.dsl.get_by_id(b)._ds_name))
        self.comb.col_set = sens_list
        self.comb.row_set = cons_list
            


    @on_trait_change('comb:combination_updated')
    def _handle_selection(self, obj, name, old, new):
        if not self.info:
            return

        selection = set(self.comb.get_selected_combinations())
        if selection.difference(self.last_selection):
            added = selection.difference(self.last_selection)
            self.last_selection = selection
            added = list(added)[0]
            self.model.add_mapping(added[0], added[1])
        elif self.last_selection.difference(selection):
            removed = self.last_selection.difference(selection)
            removed = list(removed)[0]
            rem_id = '{0}{1}'.format(removed[0], removed[1])
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
                Item('radio', editor=EnumEditor(values={
                    'Internal mapping' : '1:Internal mapping',
                    'External mapping'    : '2:External mapping',
                    }),
                     style='custom',
                     show_label=False),
                label='Select mapping',
                show_border=True,
                ),
            Item('', springy=True),
            orientation='horizontal',
            ),
          
        Group(
            Group(
                Item('model.standardise'),
                Item('pc_to_calc',
                     editor=RangeEditor(low='2',high='20',mode='spinner',is_float=False)),
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
