
# Stdlib imports
import sys
import logging
import traceback

logger = logging.getLogger('tgxnet.nofima.cc.exception')

# Enthought imports
from traits.api import HasTraits, Button, Str, push_exception_handler
from traitsui.api import View, Item
from traitsui.menu import OKButton


# Exception handler
def tgx_exception_handler(object, trait_name, old, new):
    """ Logs any exceptions generated in a trait notification handler.
    """
    # When the stack depth is too great, the logger can't always log the
    # message. Make sure that it goes to the console at a minimum:
    excp_class, excp = sys.exc_info()[:2]
    if ((excp_class is RuntimeError) and
        (excp.args[0] == 'maximum recursion depth exceeded')):
        sys.__stderr__.write( 'Exception occurred in traits notification '
            'handler for object: %s, trait: %s, old value: %s, '
            'new value: %s.\n%s\n' % ( object, trait_name, old, new,
            ''.join( traceback.format_exception( *sys.exc_info() ) ) ) )

    try:
        logger.exception(
            'Exception occurred in traits notification handler for '
            'object: %s, trait: %s, old value: %s, new value: %s' %
            ( object, trait_name, old, new ) )
    except Exception:
        # Ignore anything we can't log the above way:
        pass

    class ErrorDialog(HasTraits):
        message = Str('Something went wrong, check logfile for details')
        traits_view=View(
            Item('message', style='readonly', show_label=False, springy=True),
            buttons=[OKButton],
            resizable=True,
            width=300,
            height=150,
            )

    # FIXME: Make sure only one is open at the time
    # ErrorDialog().edit_traits()


if __name__ == '__main__':
    class TestException(HasTraits):
        test = Button('Test exception handler')

        def _test_fired(self):
            to = 1/0

        traits_view = View(
            Item('test', show_label=False)
            )

    old_handler = push_exception_handler(tgx_exception_handler)
    te = TestException()
    te.configure_traits()
