
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
from plugin_base import Model
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
    owner_ref = _traits.WeakRef()
    # design = DataSet()
    design = _traits.DelegatesTo('owner_ref')
    design_vars = _traits.List(_traits.Str())
    # design_vars = _traits.DelegatesTo('owner_ref', 'sel_design_var')
    liking = DataSet()
    consumers = DataSet()
    consumers_vars = _traits.List(_traits.Str())

    # Conjoint settings
    model_struct = _traits.Enum('Struct 1', 'Struct 2', 'Struct 3')

    # Conjoint calculation state
    ccs = _traits.Instance(ConjointCalcState, ())
    cm = _traits.Instance(ConjointMachine, ())

    # depends_on
    res = _traits.Property(depends_on='design_vars, consumers_vars, model_struct')


    @_traits.cached_property
    def _get_res(self):
        if not self.cm.run_state:
            self.cm.run_state = self.ccs

        model = {'Struct 1': 1, 'Struct 2': 2, 'Struct 3': 3}[self.model_struct]

        self.cm.schedule_calculation(
            self.design, sorted(self.design_vars),
            self.liking, model,
            self.consumers, sorted(self.consumers_vars))
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
    cj = Conjoint(design=design, liking=liking, consumers=consumers)
    cj.design_vars = ['Flavour', 'Sugarlevel']
    cj.consumers_vars = ['Sex']
    cj.print_traits()
    ## cj_res = cj.res
    ## print(cj_res.keys())
