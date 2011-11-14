
import sys
import os.path
from os import getcwd, environ

from ConfigParser import RawConfigParser, MissingSectionHeaderError, NoSectionError


class AppConf(RawConfigParser):

    def __init__(self, app_name):
        RawConfigParser.__init__(self)
        self.app_name = app_name
        self.fs = 'FoldersAndFiles'
        try:
            with open(self._get_conf_file_name(), 'r') as fp:
                self.readfp(fp)
        except (MissingSectionHeaderError, IOError):
            self._init_conf_file()

    def read_work_dir(self):
        try:
            return self.get(self.fs, 'workdir')
        except NoSectionError:
            self._init_conf_file()
            return self.get(self.fs, 'workdir')

    def save_work_dir(self, workdir):
        self.set(self.fs, 'workdir', workdir)
        with open(self._get_conf_file_name(), 'w') as fp:
            self.write(fp)

    def _init_conf_file(self):
        self.add_section(self.fs)
        self.set(self.fs, 'workdir', getcwd())
        with open(self._get_conf_file_name(), 'w') as fp:
            self.write(fp)

    def _get_conf_file_name(self):
        if sys.platform == 'darwin':
            from AppKit import NSSearchPathForDirectoriesInDomains
            # http://developer.apple.com
            # /DOCUMENTATION/Cocoa/Reference/Foundation/Miscellaneous
            # /Foundation_Functions/Reference/reference.html#
            # //apple_ref/c/func/NSSearchPathForDirectoriesInDomains
            # NSApplicationSupportDirectory = 14
            # NSUserDomainMask = 1
            # True for expanding the tilde into a fully qualified path
            appdata = os.path.join(NSSearchPathForDirectoriesInDomains(
                14, 1, True)[0], self.app_name + '.cfg')
        elif sys.platform == 'win32':
            appdata = os.path.join(environ['APPDATA'], self.app_name + '.cfg')
        else:
            appdata = os.path.expanduser(os.path.join("~", ".config", self.app_name + '.cfg'))
        return appdata



if __name__ == '__main__':
    conf = AppConf("QPCPrefmap")
    print conf.read_work_dir()
