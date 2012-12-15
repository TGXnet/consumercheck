
import sys as _sys
import os.path as _op
from os import environ as _environ
import ConfigParser as _CP

# __all__ = []

APP_NAME = "ConsumerCheck"

NEW_CFG_TEMPLATE = """
[UI]
plot_height: 800
plot_width: 800
adv_options: false

[RuntimeSettings]
work_dir: .
"""

options_map = {
    'plot_height': 'UI',
    'plot_width': 'UI',
    'adv_options': 'UI',
    'work_dir': 'RuntimeSettings',
    }


class CCConf(_CP.RawConfigParser):

    def __init__(self):
        _CP.RawConfigParser.__init__(self)
        print("Config init")
        self.cfg_file_name = self._get_conf_file_name()
        try:
            fp = open(self.cfg_file_name, 'r')
            self.readfp(fp)
            fp.close()
        except (IOError):
            self._init_conf_file()


    def set_and_write(self, section, option, value):
        _CP.RawConfigParser.set(self, section, option, value)
        with open(self.cfg_file_name, 'w') as fp:
            self.write(fp)


    def _init_conf_file(self):
        with open(self.cfg_file_name, 'w+') as fp:
            fp.write(NEW_CFG_TEMPLATE)
            fp.seek(0)
            self.readfp(fp)


    def _get_conf_file_name(self):
        if _sys.platform == 'darwin':
            from AppKit import NSSearchPathForDirectoriesInDomains
            # http://developer.apple.com
            # /DOCUMENTATION/Cocoa/Reference/Foundation/Miscellaneous
            # /Foundation_Functions/Reference/reference.html#
            # //apple_ref/c/func/NSSearchPathForDirectoriesInDomains
            # NSApplicationSupportDirectory = 14
            # NSUserDomainMask = 1
            # True for expanding the tilde into a fully qualified path
            appdata = _op.join(NSSearchPathForDirectoriesInDomains(
                14, 1, True)[0], APP_NAME + '.cfg')
        elif _sys.platform == 'win32':
            appdata = _op.join(_environ['APPDATA'], APP_NAME + '.cfg')
        else:
            appdata = _op.expanduser(
                _op.join("~", ".config", APP_NAME + '.cfg'))

        return appdata


_conf = CCConf()


def get_option(option):
    section  = options_map[option]
    return _conf.get(section, option)


def set_option(option, value):
    section  = options_map[option]
    _conf.set_and_write(section, option, value)


def list_options():
    options = []
    for section in list(set(options_map.values())):
        options += _conf.items(section)
    return options
