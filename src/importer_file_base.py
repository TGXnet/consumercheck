
# Std lib imports
import os.path

# Enthought imports
from traits.api import implements, HasTraits, File, Bool, Str, Int, List
# from traitsui.api import View, Group, Item, TabularEditor, EnumEditor, Handler
# from traitsui.tabular_adapter import TabularAdapter
# from traitsui.menu import OKButton, CancelButton

# Local imports
# from importer_interfaces import IDataImporter
from dataset import DS_TYPES, DataSet




class ImporterFileBase(HasTraits):

    file_path = File()
    transpose = Bool(False)
    have_var_names = Bool(True)
    have_obj_names = Bool(True)
    ds_name = Str('Unnamed dataset')
    kind = Str('Design variable')
    kind_list = List(DS_TYPES)


    def _ds_name_default(self):
        # FIXME: Find a better more general solution
        fn = os.path.basename(self.file_path)
        fn = fn.partition('.')[0]
        fn = fn.lower()
        return fn
