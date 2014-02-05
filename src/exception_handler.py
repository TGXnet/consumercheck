'''ConsumerCheck
'''
#-----------------------------------------------------------------------------
#  Copyright (C) 2014 Thomas Graff <thomas.graff@tgxnet.no>
#
#  This file is part of ConsumerCheck.
#
#  ConsumerCheck is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  ConsumerCheck is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ConsumerCheck.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------

# Std lib imports
import logging
logger = logging.getLogger('tgxnet.nofima.cc.'+__name__)
import sys
import time
import cStringIO
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

# ETS Traits exception handler
def tgx_exception_handler(obj, trait_name, old, new):
    """ Logs any exceptions generated in a trait notification handler.
    """
    print("Something went wrong")
    print("traits exception handler called")

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

    # Write to logfile
    try:
        logger.exception(
            'Exception occurred in traits notification handler for '
            'object: %s, trait: %s, old value: %s, new value: %s' %
            (obj, trait_name, old, new))
    except Exception:
        # Ignore anything we can't log the above way:
        pass

    if not shown:
        ed = ErrorDialog()
        ed.configure_traits(kind='modal')
        shown = True


# Activate by setting:
# sys.excepthook = excepthook

def excepthook(excType, excValue, tracebackobj):
    """
    Global function to catch unhandled exceptions.
    
    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """
    global shown

    print("Something went wrong")
    print("Excepthook called")

    separator = '-' * 80
    notice = \
        """An unhandled exception has been captured by excepthook()\n"""
    tbinfofile = cStringIO.StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = '%s: \n%s' % (str(excType), str(excValue))
    sections = [separator, errmsg, separator, tbinfo]
    msg = '\n'.join(sections)

    try:
        logger.error(str(notice)+str(msg))
    except Exception:
        # Ignore anything we can't log the above way:
        pass

    if not shown:
        ed = ErrorDialog()
        ed.configure_traits(kind='modal')
        shown = True



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ## class TestException(HasTraits):
    ##     test = Button('Test exception handler')

    ##     def _test_fired(self):
    ##         1/0

    ##     traits_view = View(
    ##         Item('test', show_label=False)
    ##         )

    ## old_handler = push_exception_handler(tgx_exception_handler)
    ## te = TestException()
    ## te.configure_traits()
    sys.excepthook = excepthook
    print("Start test")
    1/0
