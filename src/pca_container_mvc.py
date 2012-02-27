
# Enthought imports
from traits.api import HasTraits, Instance, Enum, Str, List, DelegatesTo, Bool, on_trait_change, Set
from traitsui.api import View, Item, ModelView, CheckListEditor

# Local imports
from pca_mvc import APCAHandler, APCAModel

class PCAsContainer(HasTraits):
    """PCA plugin container."""
    name = Str('Define preference mapping')
    # Instance(MainUi)?
    # WeakRef?
    mother_ref = Instance(HasTraits)
    dsl = DelegatesTo('mother_ref')
    mappings = List(APCAHandler)

    # Fitting parameters
    standardize = Bool(False)
    max_n_pc = Enum(2,3,4,5,6)


    def add_mapping(self, id):
        set_ds = self.dsl.get_by_id(id)
        map_name = id
        mapping_model = APCAModel(mother_ref=self, name=map_name,  ds=set_ds)
        mapping_handler = APCAHandler(mapping_model)
        self.mappings.append(mapping_handler)
        return map_name


    def remove_mapping(self, mapping_id):
        del(self.mappings[self.mappings.index(mapping_id)])



class PCAsHandler(ModelView):
    name = DelegatesTo('model')
    # Used by tree editor in ui_tab_pca
    mappings = DelegatesTo('model')
    selected = List()
    data = List(['test','test2'])
    last_selected = Set()
    
    def model_dsl_dataset__datasets_changed(self, info):
        print("dataset event fired")
        self.data = self.model.dsl.id_name_list

    @on_trait_change('selected')
    def handle_selected(self,obj,ref,old,new):
        old = set(old)
        new = set(new)
        odiff = old.difference(new)
        ndiff = new.difference(old)

        if odiff:
            print 'removed {}'.format(odiff)
            self.model.remove_mapping(list(odiff)[0])
        elif ndiff:
            print 'added {}'.format(ndiff)
            self.model.add_mapping(list(ndiff)[0])
            

pcas_view = View(
    Item('selected', editor=CheckListEditor(name='data'), style='custom'),
    Item('model.standardize'),
    Item('model.max_n_pc',springy = True),
    resizable=True,
    height=200,
    width=500,
    )



if __name__ == '__main__':
    print("pca container script start")
    import numpy as np
    from tests.conftest import TestContainer

    with np.errstate(invalid='ignore'):
        container = TestContainer()
        model = PCAsContainer(mother_ref=container)
        handler = PCAsHandler(model=model)
        container.test_subject = handler
        handler.configure_traits(view=pcas_view)
