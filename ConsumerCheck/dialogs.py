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

# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui


class ErrorMessage(_traits.HasTraits):
    err_msg = _traits.Str()
    msg_val = _traits.Str()

    traits_view = _traitsui.View(
        _traitsui.Item('err_msg', show_label=False, style='readonly'),
        _traitsui.Item('err_val', show_label=False, style='custom'),
        title='Warning',
        height=100,
        width=400,
        resizable=True,
        buttons=[_traitsui.OKButton],
        )



if __name__ == '__main__':
    em = ErrorMessage(err_msg='Zero variance variables', err_val='O1, O7, O45, O120')
    em.configure_traits()
