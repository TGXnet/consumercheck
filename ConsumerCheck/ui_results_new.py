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
from traits.api import HasTraits, List, Button, Str, Property
from traitsui.api import View, Group, Item, Handler
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


class TitleHandler(Handler):
    def object_title_text_changed(self, info):
        info.ui.title = info.object.title_text



class TableViewController(HasTraits):
    """Separate table view for the data set matrix."""
    # table = Array()
    table = Property()
    rows = List()
    title_text = Str(u"Result table", auto_set=True)
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
        width=0.3,
        height=0.3,
        resizable=True,
        buttons=[OKButton],
        handler=TitleHandler(),
        )


    def _get_table(self):
        return array(self.rows)


    def set_col_names(self, names):
        self.ad.columns = []
        for i, name in enumerate(names):
            self.ad.columns.append((name, i))


    def add_row(self, row_data, row_name):
        self.rows.append(row_data)


    def _cp_clip_changed(self, info):
        tf = tempfile.TemporaryFile()
        savetxt(tf, self.table, fmt='%.2f', delimiter='\t', newline='\n')
        tf.seek(0)
        txt_mat = tf.read()
        clipboard.data = txt_mat


if __name__ == '__main__':
    mvc = TableViewController(title_text='Test')
    mvc.set_col_names(['en', 'to', 'tre'])
    mvc.add_row(array([0.35, -0.92, 1.298]), 'pc1')
    mvc.add_row([-0.984, 0.053, 0.52], 'pc2')
    mvc.configure_traits()
