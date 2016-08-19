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
         * Product design
         * Descriptive analysis / sensory profiling
         * Consumer liking
         * Consumer characteristics
        Defined in dataset.py
        '''
        file_n = self.file_path.lower()
        if 'design' in file_n:
            return 'Product design'
        elif 'liking' in file_n:
            return 'Consumer liking'
        elif 'pref' in file_n:
            return 'Consumer liking'
        elif 'attr' in file_n:
            return 'Consumer characteristics'
        elif 'char' in file_n:
            return 'Consumer characteristics'
        elif 'sensory' in file_n:
            return 'Descriptive analysis / sensory profiling'
        elif 'qda' in file_n:
            return 'Descriptive analysis / sensory profiling'
        else:
            return 'Descriptive analysis / sensory profiling'
