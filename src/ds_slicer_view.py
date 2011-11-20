
# Enthough imports
from traits.api import List
from traitsui.api import Handler, View, Group, Item, CheckListEditor
from traitsui.menu import OKButton, CancelButton


class DSSlicerViewHandler(Handler):
    var_basket = List()
    obj_basket = List()

    def object_variable_names_changed(self, info):
        self.var_basket = [(i, vn) for i, vn in enumerate(info.object.variable_names)]

    def object_object_names_changed(self, info):
        self.obj_basket = [(i, vn) for i, vn in enumerate(info.object.object_names)]


slicer_handler_instance = DSSlicerViewHandler()

ds_slicer_view = View(
    Group(
        Group(
            Item('active_variables',
                 editor=CheckListEditor(
                     cols=1,
                     name='handler.var_basket',
                     ),
                 style='custom',
                 show_label=False,
                 ),
            label='Variable names',
            show_border=True,
            scrollable=True,
            ),
        Group(
            Item('active_objects',
                 editor=CheckListEditor(
                     cols=1,
                     name='handler.obj_basket',
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
    sub_ds.print_traits()
    print(sub_ds.matrix)
    print(sub_ds.variable_names)
    print(sub_ds.object_names)
