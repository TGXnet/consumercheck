from traits.api import Color, Property, List, Array, Button, Str
from traitsui.api import Controller, View, Item, TabularEditor
from traitsui.tabular_adapter import TabularAdapter
from traitsui.menu import OKButton
from pyface.api import clipboard


class ArrayAdapter(TabularAdapter):
    bg_color = Color(0xFFFFFF)
    width = 75
    index_text = Property()

    obj_names = List()

    def _get_index_text(self, name):
        return str(self.obj_names[self.row])



class DSTableViewer(Controller):
    header = Property()
    cp_clip = Button('Copy to clipboard')
    display_name = Str()


    def _get_header(self):
        varnames = [('Names', 'index')]
        for i, vn in enumerate(self.model.var_n):
            varnames.append((str(vn), i))
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
            obj_names = self.model.obj_n)

        view = View(
            Item('values', editor=TabularEditor(adapter=aa),
                 show_label=False),
            Item('handler.cp_clip', show_label=False),
            title=header_txt,
            resizable=True,
            width=900, height=400,
            buttons=[OKButton])

        return view


if __name__ == '__main__':
    from tests.conftest import simple_ds
    ds = simple_ds()
    dstv = DSTableViewer(ds)
    dstv.configure_traits(view=dstv.get_view())
