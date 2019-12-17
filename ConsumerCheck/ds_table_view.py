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

import numpy as _np

from traits.api import Color, Property, List, Button, Str
from traitsui.api import Controller, View, Item, TabularEditor
from traitsui.tabular_adapter import TabularAdapter
from traitsui.menu import OKButton
from pyface.api import clipboard
from PyQt4 import QtGui


class ArrayAdapter(TabularAdapter):
    bg_color = Color(0xFFFFFF)
    width = 75
    index_text = Property()

    obj_names = List()

    def _get_index_text(self, name):
        return unicode(self.obj_names[self.row])

    def get_format ( self, object, trait, row, column ):
        if isinstance(self.content, (_np.float64, float)):
            return '%.2f'
        return self._result_for( 'get_format', object, trait, row, column )

    def get_bg_color(self, object, trait, row, column=0):
        if len(object.subs) < 1 and len(object.rsubs) < 1:
            return None
        else:
            colcat = object.subs.keys()
            rowcat = object.rsubs.keys()
            if column > 0:
                ci = column - 1
            else:
                ci = 0
            cn = object.matcat.columns[ci][1:]
            rn = object.matcat.index[row][1:]
            if cn in colcat or rn in rowcat:
                col = QtGui.QColor(255, 71, 71)
            else:
                col = None
            return col



class DSTableViewer(Controller):
    header = Property()
    cp_clip = Button('Copy to clipboard')
    display_name = Str()


    def _get_header(self):
        varnames = [('Names', 'index')]
        if len(self.model.subs) < 1:
            for i, vn in enumerate(self.model.var_n):
                varnames.append((unicode(vn), i))
        else:
            # self.model._make_matcat()
            for i, vn in enumerate(self.model.matcat.columns):
                varnames.append((unicode(vn), i))
        return varnames


    def handler_cp_clip_changed(self, info):
        txt_var = unicode()
        for i in info.object.var_n:
            txt_var += u'{}"{}"'.format('\t', i)
        txt_var += '\n'

        txt_mat = unicode()
        for i, a in enumerate(info.object.values):
            txt_mat += u'"{}"'.format(info.object.obj_n[i])
            for e in a:
                txt_mat += u'{}{}'.format('\t', e)
            txt_mat += '\n'

        txt = txt_var + txt_mat
        clipboard.data = txt.encode('utf_8')


    def get_view(self):
        
        if self.model.display_name:
            header_txt=self.model.display_name
        else:
            header_txt=''
        
        aa = ArrayAdapter(
            columns = self.header,
            obj_names = list(self.model.matcat.index))


        if len(self.model.subs) < 1:
            view = View(
                Item('values', editor=TabularEditor(adapter=aa),
                     show_label=False),
                Item('handler.cp_clip', show_label=False),
                title=header_txt,
                resizable=True,
                width=900, height=400,
                buttons=[OKButton])
        else:
            view = View(
                Item('valuescat', editor=TabularEditor(adapter=aa),
                     show_label=False),
                Item('handler.cp_clip', show_label=False),
                title=header_txt,
                resizable=True,
                width=900, height=400,
                buttons=[OKButton])

        return view


if __name__ == '__main__':
    # from tests.conftest import simple_ds
    import os
    from importer_text_file import ImporterTextFile
    dpath = os.getenv('CC_TESTDATA', '.')
    dfile = os.path.join(dpath, 'Apples_DescrAnalysis_row&col_Cat.txt')
    itf = ImporterTextFile(
        file_path=dfile,
        delimiter='\t',
        have_obj_names=True
    )
    ds = itf.import_data()
    # import pudb; pu.db
    # ds = simple_ds()
    dstv = DSTableViewer(ds)
    dstv.configure_traits(view=dstv.get_view())
