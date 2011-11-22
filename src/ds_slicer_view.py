
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
    ## def object_variable_names_changed(self, info):
    ##     self.var_basket = [(i, vn) for i, vn in enumerate(info.object.variable_names)]
    ## def object_object_names_changed(self, info):
    ##     self.obj_basket = [(i, vn) for i, vn in enumerate(info.object.object_names)]
    picked_var = List()
    picked_obj = List()

    def init(self, info):
        self.picked_var = [info.object.variable_names[vi] for vi in info.object.active_variables]
        self.picked_obj = [info.object.object_names[oi] for oi in info.object.active_objects]

    def handler_picked_var_changed(self, info):
        vi = [info.object.variable_names.index(pv) for pv in self.picked_var]
        vi.sort()
        info.object.active_variables = vi

    def handler_picked_obj_changed(self, info):
        oi = [info.object.object_names.index(po) for po in self.picked_obj]
        oi.sort()
        info.object.active_objects = oi


slicer_handler_instance = DSSlicerViewHandler()

ds_slicer_view = View(
    Group(
        Group(
            Item('handler.picked_var',
                 editor=CheckListEditor(
                     cols=1,
                     name='object.variable_names',
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
                     name='object.object_names',
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
    ds.configure_traits(view=ds_slicer_view)
    sub_ds = ds.subset()
    ## sub_ds.print_traits()
    ## print(sub_ds.matrix)
    print(sub_ds.variable_names)
    ## print(sub_ds.object_names)
