
# Enthought imports
from traits.api import HasTraits, Any, Instance, Str, List, Int,DelegatesTo, Bool, on_trait_change, Set
from traitsui.api import View, Group, Item, ModelView, CheckListEditor, RangeEditor

# Local imports
from pca_mvc import APCAHandler, APCAModel


class PCAsContainer(HasTraits):
    """PCA plugin container."""
    name = Str('PCA results')
    win_handle = Any()
    # Instance(MainUi)?
    # WeakRef?
    mother_ref = Instance(HasTraits)
    dsl = DelegatesTo('mother_ref')
    mappings = List(APCAHandler)
    # Fitting parameters
    standardise = Bool(False)
    pc_to_calc = Int(2)


    def add_mapping(self, ds_id):
        set_ds = self.dsl[ds_id]
        map_name = set_ds.display_name
        map_id = set_ds.id
        mapping_model = APCAModel(mother_ref=self, nid=map_id, name=map_name, ds=set_ds)
        mapping_handler = APCAHandler(mapping_model)
        self.mappings.append(mapping_handler)
        return map_name


    def remove_mapping(self, mapping_id):
        del(self.mappings[self.mappings.index(mapping_id)])


class PCAsHandler(ModelView):
    name = DelegatesTo('model')
    # Used by tree editor in ui_tab_pca
    mappings = DelegatesTo('model')
    pc_to_calc = DelegatesTo('model')
    selected = List()
    data = List()
    last_selected = Set()


    def init(self, info):
        self.model.win_handle = info.ui.control


    @on_trait_change('model:mother_ref:[ds_event,dsname_event]')
    def _ds_changed(self, obj):
        self.data = self.model.dsl.get_id_name_map()


    @on_trait_change('selected')
    def handle_selected(self, obj, ref, old, new):
        old = set(old)
        new = set(new)
        odiff = old.difference(new)
        ndiff = new.difference(old)

        if odiff:
            self.model.remove_mapping(list(odiff)[0])
        elif ndiff:
            self.model.add_mapping(list(ndiff)[0])


pcas_view = View(
    Group(
        Group(
            Group(
                Item('selected',
                     editor=CheckListEditor(name='data'),
                     style='custom',
                     width=100,
                     height=200,
                     show_label=False),
                label='Select dataset',
                show_border=True,
                ),
            Group(
                Item('model.standardise'),
                Item('pc_to_calc',
                     editor=RangeEditor(low='2',high='20',mode='spinner',is_float=False)),
                label='Default PC #',
                show_border=True,
                ),
            orientation='vertical',
            ),
        Item('', springy=True),
        orientation='horizontal',
        ),
    resizable=True,
    )



if __name__ == '__main__':
    print("pca container script start")
    import numpy as np
    from tests.conftest import PluginMotherMock

    with np.errstate(invalid='ignore'):
        container = PluginMotherMock()
        model = PCAsContainer(mother_ref=container)
        handler = PCAsHandler(model=model)
        container.test_subject = handler
        handler.configure_traits(view=pcas_view)
