
# Std lib imports
import logging
# logging.basicConfig()
logger = logging.getLogger('tgxnet.nofima.cc.'+__name__)
import sys
import traceback

# Enthought imports
from traits.api import HasTraits, Button, Str, push_exception_handler
from traitsui.api import View, Item
from traitsui.menu import OKButton

# Local imports
import cc_config as conf


class ErrorDialog(HasTraits):
    message = Str()
    def _message_default(self):
        msg = """
Something went wrong! :-(
Details can be found in the log file.
The logfile is:
{0}

The program may or may not continue to work after this.
""".format(conf.log_file_url())
        return msg

    traits_view=View(
        Item('message', style='readonly', show_label=False, springy=True),
        title="Error",
        buttons=[OKButton],
        resizable=True,
        width=300,
        height=150,
        )

# State variable to indicate whether the error dialoge have been shown or not
shown = False

# Exception handler
def tgx_exception_handler(obj, trait_name, old, new):
    """ Logs any exceptions generated in a trait notification handler.
    """
    global shown
    # When the stack depth is too great, the logger can't always log the
    # message. Make sure that it goes to the console at a minimum:
    excp_class, excp = sys.exc_info()[:2]
    if ((excp_class is RuntimeError) and
        (excp.args[0] == 'maximum recursion depth exceeded')):
        trace_text = ''.join(traceback.format_exception(*sys.exc_info()))
        sys.__stderr__.write(
            'Exception occurred in traits notification '
            'handler for object: %s, trait: %s, old value: %s, '
            'new value: %s.\n%s\n' % (obj, trait_name, old, new, trace_text))

    try:
        logger.exception(
            'Exception occurred in traits notification handler for '
            'object: %s, trait: %s, old value: %s, new value: %s' %
            (obj, trait_name, old, new))
    except Exception:
        # Ignore anything we can't log the above way:
        pass

    print("Something went wrong")
    # FIXME: Make sure only one is open at the time
    if not shown:
        ed = ErrorDialog()
        ed.edit_traits(kind='modal')
        shown = True


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
