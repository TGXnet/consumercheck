
# Enthought imports
from traits.api import (HasTraits, Any, Enum, Instance, List, Str, DelegatesTo,
                        on_trait_change, Event)
from traitsui.api import (View, Group, Item, spring, ModelView, CheckListEditor,
                          EnumEditor, HTMLEditor)
from traitsui.menu import OKButton

# Local imports
from conjoint_mvc import AConjointHandler, AConjointModel
from dataset import DataSet


class ConjointsContainer(HasTraits):
    """Conjoint plugin container."""
    name = Str('Conjoint results')
    win_handle = Any()
    mother_ref = Instance(HasTraits)
    dsc = DelegatesTo('mother_ref')
    mappings = List(AConjointHandler)

    selected_design = Str()
    design_set = Instance(DataSet)
    chosen_design_vars = List(Str)
    selected_consumer_attr = Str()
    consumer_attr_set = Instance(DataSet)
    chosen_consumer_attr_vars = List(Str)
    chosen_consumer_likings = List(Str)
    model_structure_type = Enum(1, 2, 3)

    update_conjoint_tree = Event()


    def add_mapping(self, liking_set_id):
        liking_set = self.dsc[liking_set_id]
        map_name = liking_set.display_name
        map_id = liking_set.id
        mapping_model = AConjointModel(
            mother_ref=self,
            nid=map_id, name=map_name,
            cons_liking=liking_set,
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

    

    model_desc = Str(
        '''
        Consumer characteristics and design values can only be categorical values.<br /><br />
        Model structure descriptions:
        <ul>
        <li>1. Analysis of main effects, Random consumer effect AND interaction between consumer and the main effects. (Automized reduction in random part, no reduction in fixed part).</li>
        <li>2. Main effects AND all 2-factor interactions. Random consumer effect AND interaction between consumer and all fixed effects (both main and interaction ones).</li>
        <li>3. Full factorial model with ALL possible fixed and random effects. (Automized reduction in random part, AND automized reduction in fixed part).</li>
        </ul>
        ''')


    def init(self, info):
        self.model.win_handle = info.ui.control


    @on_trait_change('model:mother_ref:[ds_event,dsname_event]')
    def _ds_changed(self, info):

        dsc = self.model.dsc

        designs = dsc.get_id_name_map('Design variable')
        self.available_designs = [idn[1] for idn in designs]

        consc = dsc.get_id_name_map('Consumer characteristics')
        self.available_consumer_attrs = [idn[1] for idn in consc]

        self.available_consumer_likings = dsc.get_id_name_map('Consumer liking')

        # Reset design whne dataset is removed
        if self.model.selected_design and (self.model.selected_design not in self.available_designs):
            self.model.chosen_design_vars = []
            self.available_design_vars = []
            # self.model.selected_design = ''
        # Reset consumer chararcteristics when dataset i removed
        if self.model.selected_consumer_attr and (self.model.selected_consumer_attr not in self.available_consumer_attrs):
            self.model.choosen_consumer_attr_vars = []
            self.available_consumer_attr_vars = []
            # self.model.selected_consumer_attr = ''


    @on_trait_change('model:selected_design')
    def _handle_design_choice(self, obj, ref, new):
        idn_map = obj.dsc.get_id_name_map()
        nid_map = dict([(idn[1], idn[0]) for idn in idn_map])
        ds_id = nid_map[new]
        self.model.design_set = obj.dsc[ds_id]
        obj.chosen_design_vars = []
        self.available_design_vars = self.model.design_set.var_n


    @on_trait_change('model:selected_consumer_attr')
    def _handle_attributes(self, obj, ref, old, new):
        idn_map = obj.dsc.get_id_name_map()
        nid_map = dict([(idn[1], idn[0]) for idn in idn_map])
        ds_id = nid_map[new]
        self.model.consumer_attr_set = obj.dsc[ds_id]
        obj.chosen_consumer_attr_vars = []
        self.available_consumer_attr_vars = self.model.consumer_attr_set.var_n


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


    @on_trait_change('model:chosen_consumer_attr_vars')
    def _check_consumer_attr_warning(self, obj, ref, old, new):
        if len(new) > 2 and len(old) == 2:
            warn = CAWarning()
            warn.edit_traits()


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
                     height=150,
                     show_label=False),
                label='Consumer Design',
                padding=5,
                show_border=True,
                ),
            Group(
                Item('model.chosen_consumer_likings',
                     editor=CheckListEditor(name='handler.available_consumer_likings'),
                     style='custom',
                     height=150,
                     width=150,
                     resizable=False,
                     show_label=False),
                label='Consumer Liking',
                padding=5,
                show_border=True,
                springy=False,
                ),
            Group(
                Item('model.selected_consumer_attr',
                     editor=EnumEditor(name='handler.available_consumer_attrs'),
                     style='simple',
                     show_label=False),
                Item('model.chosen_consumer_attr_vars',
                     editor=CheckListEditor(name='handler.available_consumer_attr_vars'),
                     style='custom',
                     height=150,
                     show_label=False),
                label='Consumer Characteristics',
                padding=5,
                show_border=True,
                ),
            orientation='horizontal',
            ),
        Group(
            Group(
                Item('model.model_structure_type', show_label=False, width=100),
                show_border=True,
                label='Model structure',
                padding=5,
                ),
            spring,
            orientation='horizontal',
            ),
          Group(
                Item('model_desc',
                     editor=HTMLEditor(),
                     height=220,
                     width=460,
                     resizable=False,
                     show_label=False),
                orientation='horizontal',
                ),
        ),
    resizable=True,
    )


class CAWarning(HasTraits):
    warning = Str(
        'Too many consumer characteristics variables may result in complicated model and computations may not finish.')
    traits_view = View(
        Item('warning',
             width=250,
             height=100,
             style='readonly',
             show_label=False
             ),
        title='Warning',
        buttons=[OKButton],
        )


if __name__ == '__main__':
    print("conjoint container script start")
    import numpy as np
    from tests.conftest import plugin_mother_mock

    with np.errstate(invalid='ignore'):
        container = plugin_mother_mock()
        model = ConjointsContainer(mother_ref=container)
        handler = ConjointsHandler(model=model)
        container.test_subject = handler
        handler.configure_traits(view=conjoints_view)
