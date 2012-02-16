
from traits.api import HasTraits, Str, List, Bool, on_trait_change

from traitsui.api import View, Item, TableEditor

from traitsui.table_column import ObjectColumn

from traitsui.extras.checkbox_column import CheckboxColumn


# Create a specialized column to set the text color differently based upon
# whether or not the player is in the lineup:
class DSColumn ( ObjectColumn ):

    # Override some default settings for the column:
    width                = 0.08
    horizontal_alignment = 'center'

    def get_text_color ( self, object ):
        return [ 'light grey', 'black' ][ object.a ]
        

def generate_columns(col):
    list = [DSColumn( name = 'name',label = 'Datasets', editable = False, width  = 0.24,
                          horizontal_alignment = 'left' )]
    
    for i in col:
        list.append(CheckboxColumn( name  = '{}'.format(i),  label = i, width=0.1, horizontal_alignment = 'center'))
    return list

ds_list = ['a','b','c']

# The 'checkbox' trait table editor:
checkbox_editor = TableEditor(
    sortable     = False,
    configurable = False,
    auto_size    = True,
    columns  = generate_columns(ds_list) )


# 'Dataset' class:
class _dataset ( HasTraits ):

    # Trait definitions:
    name = Str
    _ = Bool(False)


class table_checklist ( HasTraits ):

    # Trait definitions:
    cols = List ()
    rows = List( _dataset )
    test = Item( 'rows',
                 show_label = False,
                 editor     = checkbox_editor
                 )
    # Trait view definitions:
    traits_view = View(
        Item( 'rows',
                 show_label = False,
                 editor     = checkbox_editor
                 ),
        title     = 'Checklist for selection of datasets',
        width     = 0.5,
        height    = 0.5,
        resizable = True
    )
    
class checkbox_init(HasTraits):
    
    def __init__(self):
        self.ds_name_list = ['set1', 'set2', 'set3', 'set4']
        self.cols = ['a','b','c']
        self.rows = [ _dataset(name=ds) for ds in self.ds_name_list]
        
        self.a = table_checklist(cols=self.cols, rows=self.rows)
        
        self._preset_checkboxes()
        
        def _a_changed():
            print 'a'
        
        self.a.configure_traits()
        
        
    
    def _preset_checkboxes(self):
        for i in range(len(self.a.rows)):
            for e in self.a.cols:
                setattr(self.a.rows[i],e,False)
    
    

#ds_name_list = ['set1', 'set2', 'set3', 'set4']
#
## Create the demo:
#demo = table_checklist( cols = ds_list, rows = [ _dataset(name=ds) for ds in ds_name_list ]  )
#
#print demo.rows
#
#demo.rows[0].print_traits()
#demo.rows[0].c = True
#demo.rows[0].print_traits()
# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    #demo.configure_traits()
    a = checkbox_init()