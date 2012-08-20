from traits.api import Color, Property, List, Array, Button, Str
from traitsui.api import Controller, View, Item, TabularEditor
from traitsui.tabular_adapter import TabularAdapter
from traitsui.menu import OKButton
from pyface.api import clipboard

class ArrayAdapter(TabularAdapter):
    bg_color = Color(0xFFFFFF)
    width = 75
    index_text = Property()
    #index_bg_color = Color(0xE0E0E0)

    obj_names = List()

    def _get_index_text(self, name):
        return self.obj_names[self.row]



class DSTableViewer(Controller):
    matrix = Array()
    row_names = List()
    col_names = List()
    header = Property()
    cp_clip = Button('Copy to clipboard')
    _ds_name = Str()

    def _get_header(self):
        varnames = [('Names', 'index')]
        for i, vn in enumerate(self.model.variable_names):
            varnames.append((vn, i))
        return varnames

    def handler_cp_clip_changed(self, info):
        txt_var = unicode()
        for i in info.object.variable_names:
            txt_var += u'{}"{}"'.format('\t', i)
        txt_var += '\n'

        txt_mat = unicode()
        for i, a in enumerate(info.object.matrix):
            txt_mat += u'"{}"'.format(info.object.object_names[i])
            for e in a:
                txt_mat += u'{}{}'.format('\t', e)
            txt_mat += '\n'

        txt = txt_var + txt_mat
        clipboard.data = txt.encode('utf_8')

    def get_view(self):
        
        if self.model._ds_name:
            header_txt=self.model._ds_name
        else:
            header_txt=''
        
        aa = ArrayAdapter(
            columns = self.header,
            obj_names = self.model.object_names)

        view = View(
            Item('matrix', editor=TabularEditor(adapter=aa),
                 # width=900, height=400,
                 show_label=False),
            Item('handler.cp_clip', show_label=False),
            title=header_txt,
            resizable=True,
            width=900, height=400,
            buttons=[OKButton])

        return view


if __name__ == '__main__':
    from tests.conftest import make_non_ascii_ds_mock    
    ds = make_non_ascii_ds_mock()
    dstv = DSTableViewer(ds)
    dstv.configure_traits(view=dstv.get_view())
