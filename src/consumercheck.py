# stdlib imports
# import os
import logging
import optparse
import numpy as np

# Enthought imports
## from traits.etsconfig.api import ETSConfig
## ETSConfig.toolkit = 'wx'
# ETSConfig.toolkit = 'qt4'
import traits.has_traits

# 0: no check, 1: log warings, 2: error
traits.has_traits.CHECK_INTERFACES = 0

# Local imports
from splash_screen import splash
from main_ui import MainUi


LOGGING_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
    }

def main():
    parser = optparse.OptionParser()
    parser.add_option('-l', '--logging-level', help='Logging level')
    parser.add_option('-f', '--logging-file', help='Logging file name')
    (options, args) = parser.parse_args()
    logging_level = LOGGING_LEVELS.get(options.logging_level, logging.WARNING)
    logging.basicConfig(
        level=logging_level,
        filename=options.logging_file,
        format='%(asctime)s %(levelname)s: %(message)s %(pathname)s:%(lineno)d',
        datefmt='%Y-%m-%d %H:%M:%S'
        )
    logging.info('Starting ConsumerCheck')
    splash.open()
    mother = MainUi(
        splash = splash,
        )
    mother.configure_traits()


if __name__ == '__main__':
    with np.errstate(invalid='ignore'):
        main()

#### EOF ######################################################################
