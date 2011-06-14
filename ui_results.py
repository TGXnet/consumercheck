
# Std libs import
import tempfile
from numpy import array, arange, savetxt

# Enthough imports
from enthought.traits.api import HasTraits, Instance, Array, List, Button, DelegatesTo, Property
from enthought.traits.ui.api import ModelView, View, Item, TabularEditor
from enthought.traits.ui.tabular_adapter import TabularAdapter
from enthought.traits.ui.menu import OKButton
from enthought.pyface.clipboard import clipboard

# Local imports
from dataset import DataSet


class ArrayAdapter(TabularAdapter):
    
    # font = 'Courier 10'
    # default_bg_color = 'yellow'
    # default_text_color = 'red'
    # alignment = 'right'
    # format = '%.2f'
    width = 70

    # index_text = Property
    # index_alignment = Constant('right')

    ## def _get_index_text(self, name):
    ##     if self.model_ptr.objectNames:
    ##         return self.model_ptr.objectNames[self.row]
    ##     else:
    ##         return str(self.row)



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
        Item('table',
             editor=tab_ed,
             show_label=False,
             style='readonly',
             ),
        Item('cp_clip'),
        title='Dataset matrix',
        width=0.3,
        height=0.3,
        resizable=True,
        buttons=[OKButton],
        )

    def init_info(self, info):
        la = []
        keys = self.model.data.list_data()
        keys.sort()
        for row in keys:
            la.append(self.model.data.get_data(row))
        self.table = array(la)
        rows, cols = self.table.shape
        for i in range(cols):
            self.ad.columns.append(str(i))
        # self.ad.columns=[('en', 0), ('to', 1), ('tre', 2)]

    ## def init(self, info):
    ##     print("init runt")

    def object_cp_clip_changed(self, info):
        tf = tempfile.TemporaryFile()
        savetxt(tf, self.table, fmt='%.2f', delimiter='\t', newline='\n')
        tf.seek(0)
        txt_mat = tf.read()
        clipboard.data = txt_mat


if __name__ == '__main__':
    from numpy import array
    from enthought.chaco.api import ArrayPlotData
    from plots import CCPlotScatter

    pd = ArrayPlotData()
    pd.set_data('pc1', array([0.35, -0.92, 1.298]))
    pd.set_data('pc2', array([-0.984, 0.053, 0.52]))
    ps = CCPlotScatter(pd)
    mvc = TableViewController(model=ps)
    mvc.configure_traits()
