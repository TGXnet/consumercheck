
# Std lib imports
import os.path

# Enthought imports
from traits.api import HasTraits, File, Bool, Str, List
# from traitsui.api import View, Group, Item, TabularEditor, EnumEditor, Handler
# from traitsui.tabular_adapter import TabularAdapter
# from traitsui.menu import OKButton, CancelButton

# Local imports
# from importer_interfaces import IDataImporter
from dataset import DS_TYPES


class ImporterFileBase(HasTraits):

    file_path = File()
    transpose = Bool(False)
    have_var_names = Bool(True)
    have_obj_names = Bool(True)
    ds_name = Str()
    kind = Str()
    kind_list = List(DS_TYPES)


    def _ds_name_default(self):
        # FIXME: Find a better more general solution
        fn = os.path.basename(self.file_path)
        fn = fn.partition('.')[0]
        fn = fn.lower()
        return fn


    def _kind_default(self):
        '''Available types:
         * Design variable
         * Sensory profiling
         * Consumer liking
         * Consumer characteristics
        Defined in dataset.py
        '''
        file_n = self.file_path.lower()
        if 'design' in file_n:
            return 'Design variable'
        elif 'liking' in file_n:
            return 'Consumer liking'
        elif 'attr' in file_n:
            return 'Consumer characteristics'
        elif 'sensory' in file_n:
            return 'Sensory profiling'
        elif 'qda' in file_n:
            return 'Sensory profiling'
        else:
            return 'Sensory profiling'
