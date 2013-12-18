
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
