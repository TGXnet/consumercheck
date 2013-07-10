# stdlib imports
import logging
import os.path as op
import numpy as np
import __builtin__

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
from exception_handler import tgx_exception_handler

log_format = '%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s'

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    # datefmt='%m-%d %H:%M',
    filename=conf.log_file_url(),
    filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.WARNING)
console_formatter = logging.Formatter(log_format)
console.setFormatter(console_formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

cc_logger = logging.getLogger('tgxnet.nofima.cc')
cc_logger.info('Starting ConsumerCheck')


# FIXME: Global var hack
__builtin__.cc_base_dir = op.dirname(op.abspath(__file__))


def main():
    # Open splashscreen
    splash.open()

    # Set exception handler
    push_exception_handler(tgx_exception_handler)
    mother = MainUi(
        splash = splash,
        )
    mother.configure_traits()


if __name__ == '__main__':
    with np.errstate(invalid='ignore'):
        main()
