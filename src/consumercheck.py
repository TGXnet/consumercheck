# stdlib imports
import logging
import os.path as op
import numpy as np
import __builtin__
import sys

# Enthought imports
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

import traits.has_traits
# 0: no check, 1: log warings, 2: error
traits.has_traits.CHECK_INTERFACES = 0

# Set custom exception handler
from traits.api import push_exception_handler

# Local imports
import cc_config as conf
from splash_screen import splash
from main_ui import MainUi
from exception_handler import tgx_exception_handler, excepthook

log_format = '%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s'
log_file = conf.log_file_url()

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    # datefmt='%m-%d %H:%M',
    filename=log_file,
    filemode='w')

print("Messages is writen to logfile: {0}".format(log_file))

## console = logging.StreamHandler()
## console.setLevel(logging.WARNING)
## console_formatter = logging.Formatter(log_format)
## console.setFormatter(console_formatter)
## # add the handler to the root logger
## logging.getLogger('').addHandler(console)

cc_logger = logging.getLogger('tgxnet.nofima.cc')
cc_logger.info('Starting ConsumerCheck')

# Set exception handlers
sys.excepthook = excepthook
push_exception_handler(tgx_exception_handler,
                       reraise_exceptions=False,
                       main=True,
                       locked=True)
# Do nothing and forward exception to excepthook handler
#push_exception_handler(handler=lambda o,t,ov,nv: None,
#                       reraise_exceptions=True)


# FIXME: Global var hack
__builtin__.cc_base_dir = op.dirname(op.abspath(__file__))


def main():
    # Open splashscreen
    splash.open()

    mother = MainUi(
        splash = splash,
        )
    mother.configure_traits()


if __name__ == '__main__':
    with np.errstate(invalid='ignore'):
        main()
