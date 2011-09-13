#!/usr/bin/python
# stdlib imports
# import os
import logging
import optparse

# Enthought imports
from enthought.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'wx'
# ETSConfig.toolkit = 'qt4'
#from enthought.pyface.api import GUI

# Local imports
# Set path to local R distribution
import rpyLocate
rpyLocate.set_rpy_env()

from main_ui import MainUi
from ui_tab_pca import PcaModel, PcaModelViewHandler
from ui_tab_prefmap import PrefmapModel, PrefmapModelViewHandler

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
    logging_level = LOGGING_LEVELS.get(options.logging_level, logging.NOTSET)
    logging.basicConfig(
        level=logging_level,
        filename=options.logging_file,
        format='%(asctime)s %(levelname)s: %(message)s %(pathname)s:%(lineno)d',
        datefmt='%Y-%m-%d %H:%M:%S'
        )
    logging.info('Starting ConsumerCheck')
    mother = MainUi(
        pca = PcaModelViewHandler(PcaModel()),
        prefmap = PrefmapModelViewHandler(PrefmapModel()),
        )
    mother.configure_traits()


if __name__ == '__main__':
    main()

#### EOF ######################################################################