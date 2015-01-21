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
from traits.api import HasTraits, Array, Color, List, Property
from traitsui.api import View, Item, TabularEditor
from traitsui.tabular_adapter import TabularAdapter
from traitsui.menu import OKButton


class ArrayAdapter(TabularAdapter):
    bg_color = Color(0xFFFFFF)
    vidth = 200
    index_text = Property()
    # index_bg_color = Color(0xE0E0E0)

    obj_names = List()

    def _get_index_text(self, name):
        return self.obj_names[self.row]


class DatasetMatrix(HasTraits):
    matrix = Array()
    row_names = List()
    col_names = List()
    header = Property()


    def _get_header(self):
        varnames = [('Names', 'index')]
        for i, vn in enumerate(self.col_names):
            varnames.append((vn, i))
        return varnames
        

    def get_view(self, header_txt):
        aa = ArrayAdapter(
            columns = self.header,
            obj_names = self.row_names)

        view = View(
            Item('values', editor=TabularEditor(adapter=aa),
                 # width=900, height=400,
                 show_label=False),
            title=header_txt,
            resizable=True,
            width=900, height=400,
            buttons=[OKButton])

        return view


if __name__ == '__main__':
    import numpy as np
    ds1 = DatasetMatrix(
        matrix = np.array([[1, 2],[3, 4]]),
        row_names = ['one', 'two'],
        col_names = ['tit', 'tat'])
    ds1.configure_traits(view=ds1.get_view('Data set 1'))

    ds2 = DatasetMatrix(
        matrix = np.array([[10, 20],[30, 40]]),
        row_names = ['ten', 'twenty'],
        col_names = ['check', 'mate'])
    ds2.configure_traits(view=ds2.get_view('Data set 2'))
