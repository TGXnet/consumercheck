
# Std libs import
import tempfile
from numpy import savetxt

# Enthough imports
from traits.api import Button, List, Property
from traitsui.api import Handler, View, Item, TabularEditor
from traitsui.tabular_adapter import TabularAdapter
from traitsui.menu import OKButton
from pyface.api import clipboard


class ArrayAdapter(TabularAdapter):
    width = 100
    obj_name_text = Property()
    obj_names = List([])

    def _get_obj_name_text(self, name):
        return self.obj_names[self.row]


matrix_editor=TabularEditor(
    adapter=ArrayAdapter(),
    operations=[],
    editable=False,
    show_titles=True,
    multi_select=True,
    )


class MatrixViewHandler(Handler):
    """Separate table view for the dataset matrix."""
    cp_clip = Button('Copy to clipboard')

    def init(self, info):
        varnames = self._make_header(info.object)
        matrix_editor.adapter.columns = varnames
        matrix_editor.adapter.obj_names = info.object.object_names

    def _make_header(self, ds):
        if ds.variable_names:
            varnames = []
            varlist = []
            if ds.object_names:
                varnames = [('SampleName', 'obj_name')]
            for i,vn in enumerate(ds.variable_names):
                a = vn.encode('utf-8')
                varlist.append((a,i))
            varnames += varlist
            return varnames
        else:
            return [("var{}".format(col+1), col) for col in range(ds.n_cols)]

    def handler_cp_clip_changed(self, info):
        txt_var = unicode()
        for i in info.object.variable_names:
            txt_var += u'{}"{}"'.format('\t', i)
        txt_var += '/n'

        txt_mat = unicode()
        for i, a in enumerate(info.object.matrix):
            txt_mat += u'"{}"'.format(info.object.object_names[i])
            for e in a:
                txt_mat += u'{}{}'.format('\t', e)
            txt_mat += '\n'

        txt = txt_var + txt_mat
        clipboard.data = txt.encode('utf_8')


matrix_view = View(
    Item(name='matrix',
         editor=matrix_editor,
         show_label=False,
         style='readonly',
         ),
    Item('handler.cp_clip', show_label=False),
    title='Dataset matrix',
    width=0.3,
    height=0.3,
    resizable=True,
    buttons=[OKButton],
    handler=MatrixViewHandler(),
    )


if __name__ == '__main__':
    from tests.conftest import make_non_ascii_ds_mock
    ds = make_non_ascii_ds_mock()
    ds.print_traits()
    # ds.configure_traits(view=matrix_view)
