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

# Enthough imports
from traits.etsconfig.api import ETSConfig
from traits.api import Button, Color, List, Font, Property
from traitsui.api import Controller, View, Item, TabularEditor
from traitsui.tabular_adapter import TabularAdapter
from traitsui.menu import OKCancelButtons
from pyface.api import clipboard


class DSArrayAdapter(TabularAdapter):

    # Will be overwritten by init() in TableViewer
    columns = [('dummy', 0)]

    # format = '%.4f'
    width = 50
    # index_text = Property()
    # index_bg_color = Property()
    # bg_color = Color(0xE0E0E0)
    # text_color = Color(0xE0E0E0)

    def get_row_label(self, section, obj=None):
        row_names = getattr(obj, 'obj_n', None)
        return row_names[section]


matrix_editor=TabularEditor(
    adapter=DSArrayAdapter(),
    operations=[],
    editable=False,
#    show_row_titles = ETSConfig.toolkit == 'qt4',
    )


class TableViewer(Controller):
    cp_clip = Button('Copy to clipboard')

    def init(self, info):
        matrix_editor.adapter.columns = [
            (vn.encode('utf-8'), i)
            for i, vn in enumerate(info.object.var_n)]


    def handler_cp_clip_changed(self, info):
        txt_var = unicode()
        for i in info.object.var_n:
            txt_var += u'{}"{}"'.format('\t', i)
        txt_var += '\n'

        txt_mat = unicode()
        for i, a in enumerate(info.object.matrix):
            txt_mat += u'"{}"'.format(info.object.obj_n[i])
            for e in a:
                txt_mat += u'{}{}'.format('\t', e)
            txt_mat += '\n'

        txt = txt_var + txt_mat
        clipboard.data = txt.encode('utf_8')


    def default_traits_view(self):
        return View(
                    Item('matrix',
                         editor=matrix_editor,
                         show_label=False),
                    Item('handler.cp_clip', show_label=False),
                    buttons = OKCancelButtons,
                    width=.5,
                    height=.5,
                    resizable=True,
                    title=self.model.display_name,
                    )


if __name__ == '__main__':
    from tests.conftest import simple_ds
    ds = simple_ds()
    tv = TableViewer(ds)
    tv.configure_traits()
