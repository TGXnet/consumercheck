
# Enthought imports
from traits.api import HasTraits, Enum, Instance, List, Str, DelegatesTo, on_trait_change
from traitsui.api import View, Group, Item, Spring, ModelView, CheckListEditor, EnumEditor

# Local imports
from conjoint_mvc import AConjointHandler, AConjointModel


class ConjointsContainer(HasTraits):
    """Conjoint plugin container."""
    name = Str('Conjoint results')
    mother_ref = Instance(HasTraits)
    dsl = DelegatesTo('mother_ref')
    mappings = List(AConjointHandler)

    selected_design = Str()
    chosen_design_vars = List(Str)
    selected_consumer_attr = Str()
    chosen_consumer_attr_vars = List(Str)
    chosen_consumer_likings = List(Str)
    model_structure_type = Enum(1, 2, 3)


    def add_mapping(self, liking_set_id):

        def get_set(set_id):
            return self.dsl.get_by_id(set_id)

        liking_set = get_set(liking_set_id)
        map_name = liking_set._ds_name
        map_id = liking_set._ds_id
        mapping_model = AConjointModel(
            mother_ref=self,
            nid=map_id, name=map_name,
            design=self.dsl.get_by_name(self.selected_design),
            sel_design_vars=self.chosen_design_vars,
            cons_attr=self.dsl.get_by_name(self.selected_consumer_attr),
            sel_cons_attr_vars=self.chosen_consumer_attr_vars,
            cons_liking=liking_set,
            structure=self.model_structure_type,
            )
        mapping_handler = AConjointHandler(mapping_model)
        self.mappings.append(mapping_handler)
        return map_name


    def remove_mapping(self, mapping_id):
        del(self.mappings[self.mappings.index(mapping_id)])


class ConjointsHandler(ModelView):
    name = DelegatesTo('model')
    # Used by tree editor in ui_tab_conjoint
    mappings = DelegatesTo('model')
    
    available_designs = List()
    available_design_vars = List()
    available_consumer_attrs = List()
    available_consumer_attr_vars = List()
    available_consumer_likings = List()


    @on_trait_change('model:mother_ref:[ds_event,dsname_event]')
    def _ds_changed(self, info):

        def id_by_type(type):
            return self.model.dsl.get_id_list_by_type(type)

        def name_from_id(id):
            return self.model.dsl.get_by_id(id)._ds_name

        self.available_designs = [name_from_id(i)
                                  for i in id_by_type('Design variable')]
        self.available_consumer_attrs = [name_from_id(i)
                                         for i in id_by_type('Consumer attributes')]
        self.available_consumer_likings = [(i, name_from_id(i))
                                           for i in id_by_type('Consumer liking')]


    @on_trait_change('model:selected_design')
    def _handle_design_choice(self, obj, ref, new):
        obj.chosen_design_vars = []
        self.available_design_vars = obj.dsl.get_by_name(new).variable_names


    # Not needed
    @on_trait_change('model:chosen_design_vars')
    def _handle_design_var_choice(self, obj, ref, old, new):
        print new


    @on_trait_change('model:selected_consumer_attr')
    def _handle_attributes(self, obj, ref, old, new):
        obj.chosen_consumer_attr_vars = []
        self.available_consumer_attr_vars = obj.dsl.get_by_name(new).variable_names


    # Not needed
    @on_trait_change('model:chosen_consumer_attr_vars')
    def _handle_attributes_var(self, obj, ref, old, new):
        print new


    # Not needed
    @on_trait_change('model:model_structure_type')
    def _handle_model_choice(self, obj, ref, old, new):
        print new


    @on_trait_change('model:chosen_consumer_likings')
    def _handle_liking_choice(self, obj, ref, old, new):
        old = set(old)
        new = set(new)
        odiff = old.difference(new)
        ndiff = new.difference(old)

        if odiff:
            obj.remove_mapping(list(odiff)[0])
        elif ndiff:
            obj.add_mapping(list(ndiff)[0])


conjoints_view = View(
    Group(
        Group(
            Group(
                Item('model.selected_design',
                     editor=EnumEditor(name='handler.available_designs'),
                     style='simple',
                     show_label=False),
                Item('model.chosen_design_vars',
                     editor=CheckListEditor(name='handler.available_design_vars'),
                     style='custom',
                     show_label=False),
                label='Consumer Design',
                show_border=True,
                ),
            Group(
                Item('model.chosen_consumer_likings',
                     editor=CheckListEditor(name='handler.available_consumer_likings'),
                     style='custom',
                     show_label=False),
                label='Consumer Liking',
                show_border=True,
                springy=True,
                ),
            Group(
                Item('model.selected_consumer_attr',
                     editor=EnumEditor(name='handler.available_consumer_attrs'),
                     style='simple',
                     show_label=False),
                Item('model.chosen_consumer_attr_vars',
                     editor=CheckListEditor(name='handler.available_consumer_attr_vars'),
                     style='custom',
                     show_label=False),
                label='Consumer Attributes',
                show_border=True,
                ),
            orientation='horizontal',
            ),
        Group(
            Group(
                Item('model.model_structure_type', show_label=False, width=150),
                show_border=True,
                label='Model structure',
                ),
            Spring(),
            orientation='horizontal',
            ),
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