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

import os
import codecs
import sys as _sys
import os.path as _op
import configparser as _CP


# __all__ = []

APP_NAME = "ConsumerCheck"

# option name: (section, default value, datatype)
options_map = {
    'plot_height': ('UI', '800', ''),
    'plot_width': ('UI', '800', ''),
    'adv_options': ('UI', 'false', 'boolean'),
    'work_dir': ('RuntimeSettings', '.', ''),
}


class CCConf(_CP.ConfigParser):

    def __init__(self, defaults):
        super(CCConf, self).__init__(defaults)
        self.cfg_file_name = self._get_conf_file_name()
        try:
            fp = codecs.open(self.cfg_file_name, 'r', 'utf-8')
            self.read_file(fp)
            fp.close()
        except (IOError, _CP.ParsingError):
            self._init_conf_file()


    def get(self, section, option):
        try:
            return super(CCConf, self).get(section, option)
        except _CP.NoSectionError:
            return super(CCConf, self).get('DEFAULT', option)


    def set_and_write(self, section, option, value):
        try:
            super(CCConf, self).set(section, option, value)
        except _CP.NoSectionError:
            self.add_section(section)
            super(CCConf, self).set(section, option, value)
        with codecs.open(self.cfg_file_name, 'w', 'utf-8') as fp:
            self.write(fp)


    def _init_conf_file(self):
        with codecs.open(self.cfg_file_name, 'w', 'utf-8') as fp:
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


    def _get_graphics_path(self):
        return _op.dirname(_op.realpath(__file__))


    def _get_app_data_dir(self):
        '''Find path for storing configuration file on the different platforms

        OS X: I was not able to install the AppKit package
        '''
        if _sys.platform == 'darwin':
            path = _op.expanduser(_op.join("~", ".config"))
            if not _op.isdir(path):
                os.mkdir(path, 0755)

            # from AppKit import NSSearchPathForDirectoriesInDomains
            # http://developer.apple.com
            # /DOCUMENTATION/Cocoa/Reference/Foundation/Miscellaneous
            # /Foundation_Functions/Reference/reference.html#
            # //apple_ref/c/func/NSSearchPathForDirectoriesInDomains
            # NSApplicationSupportDirectory = 14
            # NSUserDomainMask = 1
            # True for expanding the tilde into a fully qualified path
            # path = NSSearchPathForDirectoriesInDomains(14, 1, True)[0]
        elif _sys.platform == 'win32':
            path = os.environ['APPDATA']
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
        raise _CP.NoOptionError(option, section)


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


def graphics_path():
    return _conf._get_graphics_path()
