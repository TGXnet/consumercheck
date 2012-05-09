
# Enthought imports
from traits.api import HasTraits, Instance, Str, List, DelegatesTo, Bool, on_trait_change, Set
from traitsui.api import View, Group, Item, ModelView, CheckListEditor

# Local imports
from conjoint_mvc import AConjointHandler, AConjointModel


class ConjointsContainer(HasTraits):
    """Conjoint plugin container."""
    name = Str('Conjoint results')
    # Instance(MainUi)?
    # WeakRef?
    mother_ref = Instance(HasTraits)
    dsl = DelegatesTo('mother_ref')
    mappings = List(AConjointHandler)
    # Fitting parameters
    standardize = Bool(True)
    design = List()
    design_var = List()
    attributes = List()
    attributes_var = List()
    st = List()


    def add_mapping(self, ds_id):
        set_ds = self.dsl.get_by_id(ds_id)
        map_name = set_ds._ds_name
        map_id = set_ds._ds_id
        mapping_model = AConjointModel(mother_ref=self, nid=map_id, name=map_name,ds=set_ds)
        mapping_handler = AConjointHandler(mapping_model)
        self.mappings.append(mapping_handler)
        return map_name


    def remove_mapping(self, mapping_id):
        del(self.mappings[self.mappings.index(mapping_id)])


class ConjointsHandler(ModelView):
    name = DelegatesTo('model')
    # Used by tree editor in ui_tab_conjoint
    design = DelegatesTo('model')
    design_var = DelegatesTo('model')
    mappings = DelegatesTo('model')
    attributes = DelegatesTo('model')
    attributes_var = DelegatesTo('model')
    st = DelegatesTo('model')
    
    liking = List()
    
    data_design = List()
    data_design_var = List()
    data_liking = List()
    data_attributes = List()
    data_attributes_var = List()
    


    @on_trait_change('model:mother_ref:[ds_event,dsname_event]')
    def _ds_changed(self, info):
        data = []
        for i in self.model.dsl.get_id_list_by_type('Design variable'):
            data.append((self.model.dsl.get_by_id(i)._ds_name,i))
        self.data_design = data
        data = []
        for i in self.model.dsl.get_id_list_by_type('Consumer liking'):
            data.append((self.model.dsl.get_by_id(i)._ds_name,i))
        self.data_liking = data
        data = []
        for i in self.model.dsl.get_id_list_by_type('Consumer attributes'):
            data.append((self.model.dsl.get_by_id(i)._ds_name,i))
        self.data_attributes = data


    @on_trait_change('design')
    def handle_design(self, obj, ref, old, new):
        self.design_var = []
        self.data_design_var = self.model.dsl.get_by_name(new[0]).variable_names

    @on_trait_change('design_var')
    def handle_design_var(self, obj, ref, old, new):
        print new

    @on_trait_change('liking')
    def handle_liking(self, obj, ref, old, new):
        old = set(old)
        new = set(new)
        odiff = old.difference(new)
        ndiff = new.difference(old)

        if odiff:
            self.model.remove_mapping(list(odiff)[0])
        elif ndiff:
            self.model.add_mapping(list(ndiff)[0])
            
    @on_trait_change('attributes')
    def handle_attributes(self, obj, ref, old, new):
        self.attributes_var = []
        self.data_attributes_var = self.model.dsl.get_by_name(new[0]).variable_names

    @on_trait_change('attributes_var')
    def handle_attributes_var(self, obj, ref, old, new):
        print new

conjoints_view = View(
    Group(
        Group(
            Group(
                Item('design',
                     editor=CheckListEditor(name='data_design'),
                     style='simple',
                     show_label=False),
                Item('design_var',
                     editor=CheckListEditor(name='data_design_var'),
                     style='custom',
                     show_label=False),
                label='Consumer Design',
                show_border=True,
                ),
            Group(
                Item('liking',
                     editor=CheckListEditor(name='data_liking'),
                     style='custom',
                     show_label=False),
                label='Consumer Liking',
                show_border=True,
                springy=True,
                ),
            Group(
                Item('attributes',
                     editor=CheckListEditor(name='data_attributes'),
                     style='simple',
                     show_label=False),
                Item('attributes_var',
                     editor=CheckListEditor(name='data_attributes_var'),
                     style='custom',
                     show_label=False),
                label='Consumer Attributes',
                show_border=True,
                ),
            orientation='horizontal',
            ),
        Item('', springy=True),
        orientation='vertical',
        ),
    resizable=True,
    )



if __name__ == '__main__':
    print("conjoint container script start")
    import numpy as np
    from tests.conftest import TestContainer

    with np.errstate(invalid='ignore'):
        container = TestContainer()
        model = ConjointsContainer(mother_ref=container)
        handler = ConjointsHandler(model=model)
        container.test_subject = handler
        handler.configure_traits(view=conjoints_view)
