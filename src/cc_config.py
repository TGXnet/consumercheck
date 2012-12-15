
import sys as _sys
import os.path as _op
from os import environ as _environ
import ConfigParser as _CP

# __all__ = []

APP_NAME = "ConsumerCheck"

# option name: (section, default value, datatype)
options_map = {
    'plot_height': ('UI', '800', ''),
    'plot_width': ('UI', '800', ''),
    'adv_options': ('UI', 'false', 'boolean'),
    'work_dir': ('RuntimeSettings', '.', ''),
    }


class UnknownOptionError(_CP.Error):
    """Raised when no section matches a requested option."""

    def __init__(self, option):
        _CP.Error.__init__(self, 'No option: %r' % (option,))
        self.option = option
        self.args = (option, )


class CCConf(_CP.SafeConfigParser):

    def __init__(self, defaults):
        _CP.RawConfigParser.__init__(self, defaults)
        print("Config init")
        self.cfg_file_name = self._get_conf_file_name()
        try:
            fp = open(self.cfg_file_name, 'r')
            self.readfp(fp)
            fp.close()
        except (IOError):
            self._init_conf_file()


    def get(self, section, option):
        try:
            return _CP.RawConfigParser.get(self, section, option)
        except _CP.NoSectionError:
            return _CP.RawConfigParser.get(self, 'DEFAULT', option)


    def set_and_write(self, section, option, value):
        try:
            _CP.RawConfigParser.set(self, section, option, value)
        except _CP.NoSectionError:
            self.add_section(section)
            _CP.RawConfigParser.set(self, section, option, value)
        with open(self.cfg_file_name, 'w') as fp:
            self.write(fp)


    def _init_conf_file(self):
        with open(self.cfg_file_name, 'w+') as fp:
            self.write(fp)


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


_defaults = {option: data[1] for option, data in options_map.iteritems()}
_conf = CCConf(_defaults)


def get_option(option):
    try:
        section  = options_map[option][0]
        return _conf.get(section, option)
    except KeyError:
        raise UnknownOptionError(option)


def set_option(option, value):
    section  = options_map[option][0]
    _conf.set_and_write(section, option, value)


def list_options():
    options = []
    for sdt in list(set(options_map.values())):
        options += _conf.items(sdt[0])
    return options
