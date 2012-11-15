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
    # width = 100
    # index_text = Property()
    # index_bg_color = Property()
    # bg_color = Color(0xE0E0E0)
    # text_color = Color(0xE0E0E0)

    def get_row_label(self, section, obj=None):
        row_names = getattr(obj, 'object_names', None)
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
            for i, vn in enumerate(info.object.variable_names)]


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


    traits_view = View(
        Item('matrix',
             editor=matrix_editor,
             show_label=False),
        Item('handler.cp_clip', show_label=False),
        buttons = OKCancelButtons,
        width=600,
        height=200,
        resizable=True,
        )


if __name__ == '__main__':
    from tests.conftest import simple_ds
    ds = simple_ds()
    tv = TableViewer(ds)
    tv.configure_traits()
