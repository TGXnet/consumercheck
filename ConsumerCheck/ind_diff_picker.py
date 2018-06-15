
from traits.api import HasTraits, Int, List, Event, Bool, on_trait_change, Tuple, Button
from traitsui.api import View, Item, CheckListEditor, Group, Label


class IndDiffPicker(HasTraits):
    '''UI for selecting datasets for Individual Differences analysis

    This is a dialogue for selecting a:
     * Consumer Liking dataset (X)
     * Consumer Characteristics dataset (Y)
    '''
    """UI for selecting datasets for Individual Differences analysis

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Attributes:
        sel_like (List): Description of `sel_like`.
        sel_attr (:obj:`List`, optional): Description of `sel_attr`.
        combination (Tuple): Description of `combination`.

    """
    # Consumer Liking (X)
    like_set = List(Tuple())
    # Consumer Characteristics (Y)
    attr_set = List(Tuple())
    sel_like = List()
    sel_attr = List()
    standardise_x = Bool()
    standardise_x_updated = Event()
    consumer_liking_updated = Event()
    consumer_attributes_updated = Event()


    @on_trait_change('sel_like')
    def _like_selection(self, obj, name, old, new):
        self.consumer_liking_updated = True


    @on_trait_change('sel_attr')
    def _attr_selection(self, obj, name, old, new):
        self.consumer_attributes_updated = True


    @on_trait_change('standardise_x')
    def _stdx_selection(self, obj, name, old, new):
        self.standardise_x_updated = True


    traits_view = View(
        Group(
            Group(
                Label('Consumer Liking (Y)'),
                Item('sel_like', editor=CheckListEditor(name='like_set'),
                     style='simple',
                     show_label=False),
                orientation='vertical',
            ),
            Group(
                Label('Consumer Characteristics (X)'),
                Item('sel_attr', editor=CheckListEditor(name='attr_set'),
                     style='simple',
                     show_label=False,
                     enabled_when='sel_like'),
                orientation='vertical',
            ),
            orientation='horizontal',
        ),
        Item('standardise_x', label='Standardise consumer characteristics', style='custom', enabled_when='sel_like', show_label=True),
        resizable=True,
    )


    test_view = View(
        resizable=True,
        width=300,
        height=200,
    )


if __name__ == '__main__':
    print("Test start")

    def liking_print():
        comb.sel_attr = [0]
        print("Liking:", comb.sel_like)

    def attr_print():
        print("Attr:", comb.sel_attr)

    like = [(0, ''), (1, 'Alfa'), (2, 'Bravo'), (3, 'Charlie')]
    attr = [(0, ''), (1, 'One'), (2, 'Two'), (3, 'Three')]
    comb = IndDiffPicker(
        like_set=like,
        attr_set=attr)
    comb.on_trait_change(liking_print, 'consumer_liking_updated')
    comb.on_trait_change(attr_print, 'consumer_attributes_updated')
    comb.configure_traits(view='traits_view')
