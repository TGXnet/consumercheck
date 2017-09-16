'''
https://setuptools.readthedocs.io/en/latest/setuptools.html#extending-and-reusing-setuptools

It can be hard to add new commands or setup arguments to the distutils. But the setuptools package makes it a bit easier, by allowing you to distribute a distutils extension as a separate project, and then have projects that need the extension just refer to it in their setup_requires argument.

Commands is implemented in:
python2.7/distutils/command/

Some are modified and added in:
python2.7/site-packages/setuptools/command/

Commands to implement:
 + clean project folder
 + build install packages
 + run tests
 + build documentation
 + run pylint

'''
import os
import sys
import subprocess

import distutils.log
from setuptools import Command

import PyInstaller.log
import PyInstaller.building.makespec
import PyInstaller.building.build_main



class PylintCommand(Command):
    """A custom command to run Pylint on all Python source files."""

    description = 'run Pylint on Python source files'
    user_options = [
        # The format is (long option, short option, description).
        ('pylint-rcfile=', None, 'path to Pylint config file'),
    ]


    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.pylint_rcfile = 'pylint.rc'


    def finalize_options(self):
        """Post-process options."""
        if self.pylint_rcfile:
            assert os.path.exists(self.pylint_rcfile), "Pylint config file does not exist."


    def run(self):
        """Run command."""
        command = ['/usr/bin/pylint']
        if self.pylint_rcfile:
            command.append('--rcfile=%s' % self.pylint_rcfile)
        command.append(os.path.join(os.getcwd(), 'ConsumerCheck'))
        self.announce(
            'Running command: %s' % str(command),
            level=distutils.log.INFO)
        subprocess.check_call(command)



class PyInstallerCommand(Command):
    """setuptools Command"""

    description = "Create pyinstaller package"
    user_options = [
        # The format is (long option, short option, description).
        ('pylint-rcfile=', None, 'path to Pylint config file'),
    ]


    def initialize_options(self):
        """init options"""
        pass


    def finalize_options(self):
        """finalize options"""
        pass


    def run(self):
        """Run command."""
        command = ['pyinstaller']
        # DEBUG, INFO, WARN, ERROR, CRITICAL (default: INFO)
        # command.append('--log-level=WARN')
        # command.append('--debug')
        # command.append('--clean')
        command.append('--onedir')
        # command.append('--distpath=dist-pyi-1.5.1')
        # command.append('--workpath=build')
        # command.append('--specpath=build')
        # A path to search for imports
        # command.append('--paths DIR')
        # command.append('--hiddenimport MODULENAME')
        # command.append('-exclude-module EXCLUDES')
        command.append('--add-data=ConsumerCheck/*.png:.')
        command.append('--add-data=ConsumerCheck/*.svg:.')
        command.append('--add-data=ConsumerCheck/graphics:graphics')
        command.append('--runtime-hook=pyi-rthook_pyqt4.py')
        command.append('--console')
        # command.append('--windowed')
        # command.append('--icon <FILE.ico or FILE.exe,ID or FILE.icns>')
        # command.append('--version-file FILE')
        # command.append('--manifest <FILE or XML>')
        # command.append('--resource RESOURCE')
        # command.append('--name=""')
        command.append(os.path.join('ConsumerCheck', 'cc_start.py'))
        print(os.getcwd(), command)
        subprocess.check_call(command)


    def run_code(self):
        # Check platform
        # Select specfile
        # run_build(pyi_config, spec_file, **vars(args))
        logger = PyInstaller.log.getLogger(__name__)
        pyi_config = None
        # spec_file = '/home/thomas/workspace/cc-dev/cc-linux.spec'
        kwargs = {
            'workpath': '/home/thomas/workspace/cc-dev/build',
            'noupx': True,
            'hookspath': [],
            'bundle_identifier': None,
            'specpath': 'build',
            'icon_file': None,
            'clean_build': True,
            'strip': False,
            'ascii': False,
            'excludes': [],
            'console': True,
            'version_file': None,
            'uac_admin': False,
            'upx_dir': None,
            'win_private_assemblies': False,
            'resources': [],
            'onefile': False,
            'runtime_hooks': ['pyi-rthook_pyqt4.py'],
            'uac_uiaccess': False,
            'filenames': ['ConsumerCheck/cc_start.py'],
            'distpath': 'dist-pyi-1.5.1',
            'key': None,
            'noconfirm': False,
            'name': 'cc-linux',
            'hiddenimports': [],
            'pathex': [],
            'manifest': None,
            'loglevel': 'INFO',
            'win_no_prefer_redirects': False,
            'upx': False,
            'debug': False,
            'binaries': [],
            'datas': [
                ('ConsumerCheck/*.png', '.'),
                ('ConsumerCheck/*.svg', '.'),
                ('ConsumerCheck/graphics', 'graphics')
            ]
        }
        spec_file = run_makespec(**kwargs)
        logger.info('wrote %s' % spec_file)
        PyInstaller.building.build_main.main(pyi_config, spec_file, **kwargs)
        # build(); Adds stuff to CONF dict, runs the code i spec file



def run_makespec(filenames, **opts):
    # Split pathex by using the path separator
    temppaths = opts['pathex'][:]
    pathex = opts['pathex'] = []
    for p in temppaths:
        pathex.extend(p.split(os.pathsep))

    spec_file = PyInstaller.building.makespec.main(filenames, **opts)
    return spec_file
