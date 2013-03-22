
# Std lib imports
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    # datefmt='%m-%d %H:%M',
                    datefmt='%y%m%dT%H:%M:%S',
                    # filename='/temp/myapp.log',
                    # filemode='w',
                    )
if __name__ == '__main__':
    logger = logging.getLogger('tgxnet.nofima.cc.' + __file__.split('.')[0])
else:
    logger = logging.getLogger(__name__)

# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui

# Local imports
from dataset import DataSet
from plugin_tree_helper import Model
from conjoint_machine import ConjointMachine


class ConjointCalcState(_traits.HasTraits):
    messages = _traits.Str()
    is_done = _traits.Bool(True)

    traits_view = _traitsui.View(
        _traitsui.Item('messages', show_label=False, springy=True, style='custom' ),
        title='Conjoint calculation status',
        height=300,
        width=600,
        resizable=True,
        buttons=[_traitsui.OKButton],
        )

    def _messages_changed(self, new):
        self.messages = '\n'.join(
            [line for line in new.split('\n') if not line.startswith('try')])

    def _is_done_changed(self, new):
        pass
        ## if new:
        ##     logger.info('Conjoint result ready')
        ## else:
        ##     logger.info('Staring conjoint calculation')


class Conjoint(Model):
    # The imput data for calculation
    design_set = DataSet()
    chosen_design_vars = _traits.List(_traits.Str())
    consumer_attr_set = DataSet()
    chosen_consumer_attr_vars = _traits.List(_traits.Str())
    cons_liking = DataSet()

    # Conjoint settings
    model_structure_type = _traits.Enum('Struct 1', 'Struct 2', 'Struct 3')

    # Conjoint calculation state
    ccs = _traits.Instance(ConjointCalcState, ())
    cm = _traits.Instance(ConjointMachine, ())

    # depends_on
    res = _traits.Property(depends_on='chosen_design_vars, chosen_consumer_attr_vars, model_structure_type')


    @_traits.cached_property
    def _get_res(self):
        if not self.cm.run_state:
            self.cm.run_state = self.ccs

        struct = {'Struct 1': 1, 'Struct 2': 2, 'Struct 3': 3}[self.model_structure_type]

        self.cm.schedule_calculation(
            struct,
            self.consumer_attr_set, sorted(self.chosen_consumer_attr_vars),
            self.design_set, sorted(self.chosen_design_vars),
            self.cons_liking)
        self.ccs.edit_traits(kind='livemodal')
        return self.cm.get_result()


if __name__ == '__main__':
    print("Conjoint start")
    from tests.conftest import conjoint_dsc
    from dataset_container import get_ds_by_name
    conjoint_dsc = conjoint_dsc()
    design = get_ds_by_name('Tine yogurt design', conjoint_dsc)
    liking = get_ds_by_name('Odour-flavor', conjoint_dsc)
    consumers = get_ds_by_name('Consumers', conjoint_dsc)
    cj = Conjoint(design_set=design, cons_liking=liking, consumer_attr_set=consumers)
    cj.chosen_design_vars = ['Flavour', 'Sugarlevel']
    cj.chosen_consumer_attr_vars = ['Sex']
    cj.print_traits()
    ## cj_res = cj.res
    ## print(cj_res.keys())
