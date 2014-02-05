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

# Enthough imports
from traits.api import List, Str
from traitsui.api import Handler, View, Group, Item, CheckListEditor
from traitsui.menu import OKButton, CancelButton


class DSSlicerViewHandler(Handler):
    # FIXME: I had to to this differently from the way I intended
    # beacaus CheckListEditor reset my selected list when i "picked
    # from and generated tuple list
    ## var_basket = List()
    ## obj_basket = List()
    ## def object_var_n_changed(self, info):
    ##     self.var_basket = [(i, vn) for i, vn in enumerate(info.object.var_n)]
    ## def object_obj_n_changed(self, info):
    ##     self.obj_basket = [(i, vn) for i, vn in enumerate(info.object.obj_n)]
    picked_var = List()
    picked_obj = List()

    def init(self, info):
        self.picked_var = [info.object.var_n[vi] for vi in info.object.active_variables]
        self.picked_obj = [info.object.obj_n[oi] for oi in info.object.active_objects]

    def handler_picked_var_changed(self, info):
        vi = [info.object.var_n.index(pv) for pv in self.picked_var]
        vi.sort()
        info.object.active_variables = vi

    def handler_picked_obj_changed(self, info):
        oi = [info.object.obj_n.index(po) for po in self.picked_obj]
        oi.sort()
        info.object.active_objects = oi


slicer_handler_instance = DSSlicerViewHandler()

ds_slicer_view = View(
    Group(
        Group(
            Item('handler.picked_var',
                 editor=CheckListEditor(
                     cols=1,
                     name='object.var_n',
                     ),
                 style='custom',
                 show_label=False,
                 ),
            label='Variable names',
            show_border=True,
            scrollable=True,
            ),
        Group(
            Item('handler.picked_obj',
                 editor=CheckListEditor(
                     cols=1,
                     name='object.obj_n',
                     ),
                 style='custom',
                 show_label=False,
                 ),
            label='Object names',
            show_border=True,
            scrollable=True,
            ),
        orientation='horizontal',
        ),
    resizable=True,
    handler=slicer_handler_instance,
    width=300,
    height=300,
    buttons=[OKButton]
    )


ds_var_slicer_view = View(
    Group(
        Group(
            Item('handler.picked_var',
                 editor=CheckListEditor(
                     cols=1,
                     name='object.var_n',
                     ),
                 style='custom',
                 show_label=False,
                 ),
            label='Variable names',
            show_border=True,
            scrollable=True,
            ),
        orientation='horizontal',
        ),
    resizable=True,
    handler=slicer_handler_instance,
    width=300,
    height=300,
    buttons=[OKButton]
    )


ds_obj_slicer_view = View(
    Group(
        Group(
            Item('handler.picked_obj',
                 editor=CheckListEditor(
                     cols=1,
                     name='object.obj_n',
                     ),
                 style='custom',
                 show_label=False,
                 ),
            label='Object names',
            show_border=True,
            scrollable=True,
            ),
        orientation='horizontal',
        ),
    resizable=True,
    handler=slicer_handler_instance,
    width=300,
    height=300,
    buttons=[OKButton]
    )


if __name__ == '__main__':
    from importer_main import ImporterMain
    fi = ImporterMain()
    ds = fi.import_data('./datasets/Vine/A_labels.txt', True, True)
    # ds.configure_traits(view=ds_slicer_view)
    ds.configure_traits(view=ds_obj_slicer_view)
    ds.configure_traits(view=ds_var_slicer_view)
    sub_ds = ds.subset()
    print(sub_ds.var_n)
    print(sub_ds.obj_n)
    sub_ds.print_traits()
    print(sub_ds.values)
