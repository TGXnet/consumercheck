'''ConsumerCheck
'''
#-----------------------------------------------------------------------------
#  Copyright (C) 2014 Thomas Graff <thomas.graff@tgxnet.no>
#
#  This file is part of ConsumerCheck.
#
#  ConsumerCheck is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  ConsumerCheck is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ConsumerCheck.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------

# Std lib imports
import logging
logger = logging.getLogger('tgxnet.nofima.cc.'+__name__)

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
        buttons=[
            _traitsui.Action(name='Cancel', action='_on_close', enabled_when='not is_done'),
            _traitsui.Action(name='OK', action='_on_close', enabled_when='is_done')],
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
    liking = DataSet()
    # consumers = DataSet()
    consumers = _traits.DelegatesTo('owner_ref')
    consumers_vars = _traits.List(_traits.Str())

    # Conjoint settings
    model_struct = _traits.Enum('Struct 1', 'Struct 2', 'Struct 3')

    # Conjoint calculation state
    ccs = _traits.Instance(ConjointCalcState, ())
    cm = _traits.Instance(ConjointMachine, ())

    # depends_on
    res = _traits.Property(depends_on='design_vars, consumers_vars, model_struct')


    @_traits.on_trait_change('owner_ref.model_struct')
    def _struc_altered(self, new):
        self.model_struct = new


    @_traits.on_trait_change('owner_ref.sel_design_var')
    def _des_var_altered(self, new):
        self.design_vars = new


    @_traits.on_trait_change('owner_ref.sel_cons_char')
    def _cons_char_altered(self, new):
        self.consumers_vars = new


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
