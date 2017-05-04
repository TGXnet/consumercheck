
from traits.api import HasTraits, Int, List, Event, on_trait_change, Tuple, Button
from traitsui.api import View, Item, CheckListEditor, Group, Label


class IndDiffPicker(HasTraits):
    '''UI for selecting datasets for Individual Differences analysis

    This is a dialogue for selecting a:
     * Consumer Liking dataset (X)
     * Consumer Attributes dataset (Y)
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
    # Consumer Attributes (Y)
    attr_set = List(Tuple())
    sel_like = List()
    sel_attr = List()
    combination = Tuple()
    combination_updated = Event()
    consumer_liking_updated = Event()
    consumer_attributes_updated = Event()


    # @on_trait_change('sel_like,sel_attr')
    # def _new_selection(self, obj, name, old_value, new_value):
    #     """Example of docstring on the _new_selection method.

    #     The _new_selection method may be documented in either the class level
    #     docstring, or as a docstring on the _new_selection method itself.

    #     Either form is acceptable, but the two should not be mixed. Choose one
    #     convention to document the _new_selection method and be consistent with it.

    #     Note:
    #         Do not include the `self` parameter in the ``Args`` section.

    #     Args:
    #         param1 (str): Description of `param1`.
    #         param2 (:obj:`int`, optional): Description of `param2`. Multiple
    #             lines are supported.
    #         param3 (:obj:`list` of :obj:`str`): Description of `param3`.

    #     """
    #     if not (self.sel_like and self.sel_attr):
    #         return
    #     sel = (self.sel_like[0], self.sel_attr[0])
    #     self.combination = sel
    #     self.combination_updated = True


    @on_trait_change('sel_like')
    def _like_selection(self, obj, name, old, new):
        self.consumer_liking_updated = True


    @on_trait_change('sel_attr')
    def _attr_selection(self, obj, name, old, new):
        self.consumer_attributes_updated = True


    # def get_selected_combination(self):
    #     """Example of docstring on the _new_selection method.

    #     The _new_selection method may be documented in either the class level
    #     docstring, or as a docstring on the _new_selection method itself.

    #     Either form is acceptable, but the two should not be mixed. Choose one
    #     convention to document the _new_selection method and be consistent with it.

    #     Note:
    #         Do not include the `self` parameter in the ``Args`` section.

    #     Args:
    #         param1 (str): Description of `param1`.
    #         param2 (:obj:`int`, optional): Description of `param2`. Multiple
    #             lines are supported.
    #         param3 (:obj:`list` of :obj:`str`): Description of `param3`.

    #     """
    #     return self.combination


    traits_view = View(
        Group(
            Group(
                Label('Consumer Liking (X)'),
                Item('sel_like', editor=CheckListEditor(name='like_set'),
                     style='simple',
                     show_label=False),
                orientation='vertical',
            ),
            Group(
                Label('Consumer Attributes (Y)'),
                Item('sel_attr', editor=CheckListEditor(name='attr_set'),
                     style='simple',
                     show_label=False,
                     enabled_when='sel_like'),
                orientation='vertical',
            ),
            orientation='horizontal',
        ),
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
        print(comb.sel_like)

    def attr_print():
        print(comb.sel_attr)

    like = [(1, 'Alfa'), (2, 'Bravo'), (3, 'Charlie')]
    attr = [(1, 'One'), (2, 'Two'), (3, 'Three')]
    comb = IndDiffPicker(
        like_set=like,
        attr_set=attr)
    comb.on_trait_change(liking_print, 'consumer_liking_updated')
    comb.on_trait_change(attr_print, 'consumer_attributes_updated')
    comb.configure_traits(view='traits_view')
