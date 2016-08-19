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

# Std libs import
import tempfile
from numpy import array, savetxt

# Enthough imports
from traits.api import Array, List, Button, Property
from traitsui.api import ModelView, View, Group, Item
from traitsui.editors.tabular_editor import TabularEditor
from traitsui.tabular_adapter import TabularAdapter
from traitsui.menu import OKButton
from pyface.api import clipboard


class ArrayAdapter(TabularAdapter):
    index = List()
    # font = 'Courier 10'
    # default_bg_color = 'yellow'
    # default_text_color = 'red'
    # alignment = 'right'
    format = '%.2f'
    width = 70

    index_text = Property
    # index_alignment = Constant('right')

    def _get_index_text(self, name):
        return self.index[self.row]



class TableViewController(ModelView):
    """Separate table view for the data set matrix."""
    table = Array()
    cp_clip = Button('Copy to clipboard')
    ad = ArrayAdapter()
    tab_ed=TabularEditor(
        adapter=ad,
        operations=[],
        editable=False,
        show_titles=True,
        # multi_select=True,
        )

    trait_view = View(
        Group(
            Item('table',
                 editor=tab_ed,
                 show_label=False,
                 style='readonly',
                 ),
            Group(
                Item('cp_clip', show_label=False),
                orientation="horizontal",
                ),
            layout="normal",
            ),
        title='Data set matrix',
        width=0.3,
        height=0.3,
        resizable=True,
        buttons=[OKButton],
        )


    def init_info(self, info):
        la = []
        self.ad.index = self.model.data.list_data()
        self.ad.index.sort()
        for name in self.ad.index:
            # FIXME: Lot of hack here
            # needs redesign
            if name in ['ell_full_x', 'ell_full_y', 'ell_half_x', 'ell_half_y', 'pcy1', 'pcy2']:
                continue
            vec = self.model.data.get_data(name)
            la.append(vec)
        self.table = array(la)
        rows, cols = self.table.shape
        # self.ad.columns = [('i', 'index')]
        self.ad.columns = []
        for i in range(cols):
            self.ad.columns.append((str(i), i))
        # self.ad.columns=[('en', 0), ('to', 1), ('tre', 2)]


    def object_cp_clip_changed(self, info):
        tf = tempfile.TemporaryFile()
        savetxt(tf, self.table, fmt='%.2f', delimiter='\t', newline='\n')
        tf.seek(0)
        txt_mat = tf.read()
        clipboard.data = txt_mat



if __name__ == '__main__':
    print("Start test")
