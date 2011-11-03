
# Enthought imports
from traits.api import List, Enum, Event, on_trait_change
from traitsui.api import View, Group, UCustom, Label, CheckListEditor, EnumEditor, Controller


class PrefmapUIController(Controller):
    """ Preference mapping selection tool

    The model attribute have to be set to the dataset collection (dsl)
    object in this object constructor.
    """
    _sens = List()
    _cons = List()
    sel_sens = List(
        label = 'Sensory profiling',
        editor = CheckListEditor(name='_sens',),
        )
    sel_cons = List(
        label = 'Consumer',
        editor = CheckListEditor(name='_cons'),
        )
    mapping = Enum('Int mapping', 'Ext mapping')
    ## method = Enum('PLSR', 'PCR')

    sel_updated = Event

    def get_cross_mappings(self):
        if self.mapping == 'Int mapping':
            return [(c, s) for c in self.sel_cons for s in self.sel_sens if c != s]
        elif self.mapping == 'Ext mapping':
            return [(s, c) for c in self.sel_cons for s in self.sel_sens if c != s]

    def init(self, info):
        self._build_sel_list()

    def _build_sel_list(self):
        datasets = self.model.get_dataset_list()
        self._sens =  [(ds._ds_id, ds._ds_name) for ds in datasets if ds._dataset_type == 'Sensory profiling']
        self._cons = [(ds._ds_id, ds._ds_name) for ds in datasets if ds._dataset_type == 'Consumer liking']

    @on_trait_change('sel_cons, sel_sens, mapping')
    def _choice_updated(self, obj, name, old, new):
        self.sel_updated = True

    @on_trait_change('model:[ds_name_event,datasets_event],model:_datasets:_dataset_type')
    def _dsl_altered(self, obj, name, new):
        self._build_sel_list()


prefmap_ui_controller = PrefmapUIController()

prefmap_ui_view = View(
    Group(
        Group(
            Group(
                Label('Sensory profiling'),
                UCustom('handler.sel_sens'),
                show_border=True,
                orientation='vertical',
                ),
            Group(
                Label('Consumer'),
                UCustom('handler.sel_cons'),
                show_border=True,
                orientation='vertical',
                ),
            orientation='horizontal',
            ),
        Group(
            Group(
                Label('Mapping'),
                UCustom('handler.mapping',
                        editor=EnumEditor(values=('Int mapping', 'Ext mapping')),
                        ),
                show_border=True,
                orientation='vertical',
                ),
            ## Group(
            ##     Label('Method'),
            ##     UCustom('handler.method',
            ##             editor=EnumEditor(values=('PLSR', 'PCR')),
            ##             ),
            ##     show_border=True,
            ##     orientation='vertical',
            ##     ),
            orientation='horizontal',
            ),
        orientation='vertical'
        ),
    resizable = True,
    handler = prefmap_ui_controller,
)


def show_change():
    xl = container.test_subject.get_cross_mappings()
    print("Show change run\nValues {}".format(xl))


if __name__ == '__main__':
    print("Interactive start")
    from tests.tools import TestContainer
    container = TestContainer()
    prefmap_ui_controller.model = container.dsl
    container.test_subject = prefmap_ui_controller
    container.test_subject.on_trait_event(show_change, name='sel_updated')
    container.test_subject.configure_traits(
        view=prefmap_ui_view,
        ## kind='nonmodal',
        )
    print("GUI started")
