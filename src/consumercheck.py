# stdlib imports
# import os
import logging
import optparse
import numpy as np

# Enthought imports
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

import traits.has_traits
# 0: no check, 1: log warings, 2: error
traits.has_traits.CHECK_INTERFACES = 0

# Set custom exception handler
from traits.api import push_exception_handler

# Local imports
from splash_screen import splash
from main_ui import MainUi
from exception_handler import tgx_exception_handler


# Setup logging
LOGGING_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
    }
LOG_FILENAME = 'cc.log'


def main():
    parser = optparse.OptionParser()
    parser.add_option('-l', '--logging-level', help='Logging level')
    parser.add_option('-f', '--logging-file', help='Logging file name')
    (options, args) = parser.parse_args()

    # Configure logging
    logging_level = LOGGING_LEVELS.get(options.logging_level, logging.DEBUG)
    logging.basicConfig(
        level=logging_level,
        # filename=options.logging_file,
        filename=LOG_FILENAME,
        # format='%(asctime)s %(levelname)s: %(message)s %(pathname)s:%(lineno)d',
        # datefmt='%Y-%m-%d %H:%M:%S'
        filemode='w',
        )
    logger = logging.getLogger('tgxnet.nofima.cc')
    logger.info('Starting ConsumerCheck')

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

#### EOF ######################################################################
