
# Std libs import
import tempfile
from numpy import savetxt

# Enthough imports
from traits.api import Instance, Button, Property
from traitsui.api import Controller, View, Item, TabularEditor
from traitsui.tabular_adapter import TabularAdapter
from traitsui.menu import OKButton
from pyface.clipboard import clipboard

# Local imports
from dataset import DataSet


class ArrayAdapter(TabularAdapter):

    model_ptr = Instance(DataSet)

    # font = 'Courier 10'
    # default_bg_color = 'yellow'
    # default_text_color = 'red'
    # alignment = 'right'
    # format = '%.2f'
    width = 70

    index_text = Property
    # index_alignment = Constant('right')

    def _model_ptr_changed(self):
        self.columns = [('Index', 'index')]
        rows, cols = self.model_ptr.matrix.shape
        for i in xrange(cols):
            if self.model_ptr.variable_names:
                self.columns.append((self.model_ptr.variable_names[i], i))
            else:
                self.columns.append((str(i), i))

    def _get_index_text(self, name):
        if self.model_ptr.object_names:
            return self.model_ptr.object_names[self.row]
        else:
            return str(self.row)



class MatrixViewController(Controller):
    """Separate table view for the dataset matrix."""
    # data = DelegatesTo('model', prefix='matrix')
    cp_clip = Button('Copy to clipboard')
    ad = ArrayAdapter()
    tab_ed=TabularEditor(
        adapter=ad,
        operations=[],
        editable=False,
        show_titles=True,
        multi_select=True,
        )

    trait_view = View(
        Item(name='matrix',
             editor=tab_ed,
             show_label=False,
             style='readonly',
             ),
        Item('controller.cp_clip'),
        title='Dataset matrix',
        width=0.3,
        height=0.3,
        resizable=True,
        buttons=[OKButton],
        )

    def init_info(self, info):
        print("init info run")
        self.ad.model_ptr = self.model

    def init(self, info):
        print("init runt")

    def controller_cp_clip_changed(self, info):
        tf = tempfile.TemporaryFile()
        savetxt(tf, self.model.matrix, fmt='%.2f', delimiter='\t', newline='\n')
        tf.seek(0)
        txt_mat = tf.read()
        clipboard.data = txt_mat


if __name__ == '__main__':
    
    from importer_main import ImporterMain
    fi = ImporterMain()
    ds = fi.import_data('./datasets/A_labels.txt', True, True)
    mvc = MatrixViewController(model=ds)
    mvc.configure_traits()
