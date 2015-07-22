# Enthought imports
from traits.api import HasTraits
from traitsui.api import View
from traitsui.menu import CloseAction, Menu, MenuBar


class MainUi(HasTraits):

    traits_view = View(
        resizable=True,
        width=600,
        height=400,
        menubar=MenuBar(
            Menu(CloseAction, name='&File'),
        ),
    )


if __name__ == '__main__':
    mother = MainUi()
    ui = mother.configure_traits()
