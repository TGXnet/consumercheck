'''
Created on Sep 11, 2012

@author: Thomas Graff <graff.thomas@gmail.com>
'''

from traits.api import HasTraits, Str, Tuple, WeakRef


def dclk_activator(obj):
    fn = obj.func_name
    open_win_func = getattr(obj.owner_ref, fn)
    if len(obj.func_parms) < 1:
        open_win_func()
    else:
        open_win_func(*obj.func_parms)


class WindowLauncher(HasTraits):
    node_name = Str()
    func_name = Str()
    owner_ref = WeakRef()
    func_parms = Tuple()
