
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
    """Separate table view for the dataset matrix."""
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
        title='Dataset matrix',
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
    from chaco.api import ArrayPlotData
    from plots import CCPlotScatter

    pd = ArrayPlotData()
    pd.set_data('pc1', array([0.35, -0.92, 1.298]))
    pd.set_data('pc2', array([-0.984, 0.053, 0.52]))
    ps = CCPlotScatter(pd)
    mvc = TableViewController(model=ps)
    mvc.configure_traits()
