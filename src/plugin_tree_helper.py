'''Plugin infrastructure.

Base classes for a statistics method plugin.

Created on Sep 11, 2012

@author: Thomas Graff <graff.thomas@gmail.com>
'''
# ETS imports
import traits.api as _traits


def dclk_activator(obj):
    open_win_func = obj.view_creator
    res = obj.owner_ref.get_result()
    loop = getattr(obj.owner_ref, obj.loop_name)
    if len(obj.func_parms) < 1:
        view = open_win_func(res)
    else:
        view = open_win_func(res, *obj.func_parms)
    obj.owner_ref.open_window(view, loop)


def overview_activator(obj):
    obj.open_overview()


class WindowLauncher(_traits.HasTraits):
    node_name = _traits.Str()
    # FIXME: Deprecated by view_creator
    # func_name = _traits.Str()
    view_creator = _traits.Callable()
    owner_ref = _traits.WeakRef()
    loop_name = _traits.Str()
    # FIXME: Rename to creator_parms
    func_parms = _traits.Tuple()



class ViewNavigator(_traits.HasTraits):
    view_loop = _traits.List(WindowLauncher)
    current_idx = _traits.Int(0)
    res = _traits.WeakRef()


    def show_next(self):
        if self.current_idx < len(self.view_loop)-1:
            self.current_idx += 1
        else:
            self.current_idx = 0
        vc = self.view_loop[self.current_idx]
        # return vc.view_creator(self.res, vc.func_parms)
        if len(vc.func_parms) < 1:
            return vc.view_creator(self.res)
        else:
            return vc.view_creator(self.res, *vc.func_parms)


    def show_previous(self):
        if self.current_idx > 0:
            self.current_idx -= 1
        else:
            self.current_idx = len(self.view_loop) - 1
        vc = self.view_loop[self.current_idx]
        if len(vc.func_parms) < 1:
            return vc.view_creator(self.res)
        else:
            return vc.view_creator(self.res, *vc.func_parms)
