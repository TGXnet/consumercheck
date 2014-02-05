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
#  (at your option) any later version.
#
#  ConsumerCheck is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ConsumerCheck.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------

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
        self.cfg_file_name = self._get_conf_file_name()
        try:
            fp = open(self.cfg_file_name, 'r')
            self.readfp(fp)
            fp.close()
        except (IOError, _CP.ParsingError):
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
        path = self._get_app_data_dir()
        return _op.join(path, APP_NAME + '.cfg')


    def _get_log_file_name(self):
        path = self._get_app_data_dir()
        return _op.join(path, APP_NAME + '.log')


    def _get_pkl_file_name(self):
        path = self._get_app_data_dir()
        return _op.join(path, APP_NAME + '.pkl')


    def _get_app_data_dir(self):
        if _sys.platform == 'darwin':
            from AppKit import NSSearchPathForDirectoriesInDomains
            # http://developer.apple.com
            # /DOCUMENTATION/Cocoa/Reference/Foundation/Miscellaneous
            # /Foundation_Functions/Reference/reference.html#
            # //apple_ref/c/func/NSSearchPathForDirectoriesInDomains
            # NSApplicationSupportDirectory = 14
            # NSUserDomainMask = 1
            # True for expanding the tilde into a fully qualified path
            path = NSSearchPathForDirectoriesInDomains(14, 1, True)[0]
        elif _sys.platform == 'win32':
            path = _environ['APPDATA']
        else:
            path = _op.expanduser(_op.join("~", ".config"))

        return path



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


def log_file_url():
    return _conf._get_log_file_name()


def pkl_file_url():
    return _conf._get_pkl_file_name()
