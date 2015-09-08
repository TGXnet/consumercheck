# -*- coding: utf-8 -*-
# The content here is taken from spyderlib
"""
Copyright (C) 2014 Thomas Graff <thomas.graff@tgxnet.no>

This file is part of ConsumerCheck.

ConsumerCheck is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

ConsumerCheck is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ConsumerCheck.  If not, see <http://www.gnu.org/licenses/>.
"""

__version__ = '1.3.1'
__license__ = __doc__
__project_url__ = 'http://sourceforge.net/projects/consumercheck/'
__forum_url__   = 'http://consumercheck.co/'

# Dear (Debian, RPM, ...) package makers, please feel free to customize the
# following path to module's data (images) and translations:
DATAPATH = LOCALEPATH = DOCPATH = ''
DATAPATH = '/usr/share/consumercheck/images'
DOCPATH = '/usr/share/doc/python-consumercheck-doc/html'


import os
# Directory of the current file
__dir__ = os.path.dirname(os.path.abspath(__file__))


# def add_to_distribution(dist):
#     """Add package to py2exe/cx_Freeze distribution object
#     Extension to guidata.disthelpers"""
#     try:
#         dist.add_qt_bindings()
#     except AttributeError:
#         raise ImportError("This script requires guidata 1.5+")
#     for _modname in ('consumercheck'):
#         dist.add_module_data_files(_modname, ("", ),
#                                    ('.png', '.svg', '.html', '.png', '.txt',
#                                     '.js', '.inv', '.ico', '.css', '.doctree',
#                                     '.qm', '.py',),
#                                    copy_to_root=False)


def get_versions(reporev=True):
    """Get version information for components used by Spyder"""
    import sys
    import platform
    # Hack to let IPython set QT_API, in case it's installed
    try:
        from IPython.external import qt
    except ImportError:
        pass
    # import spyderlib.qt
    # import spyderlib.qt.QtCore

    revision = None
    # if reporev:
    #     from spyderlib.utils import vcs
    #     full, short, branch = vcs.get_hg_revision(os.path.dirname(__dir__))
    #     if full:
    #         revision = '%s:%s' % (full, short)

    if not sys.platform == 'darwin':  # To avoid a crash with our Mac app
        system = platform.system()
    else:
        system = 'Darwin'

    return {
        'consumercheck': __version__,
        'python': platform.python_version(),  # "2.7.3"
        'bitness': 64 if sys.maxsize > 2**32 else 32,
        # 'qt': spyderlib.qt.QtCore.__version__,
        # 'qt_api': spyderlib.qt.API_NAME,      # PySide or PyQt4
        # 'qt_api_ver': spyderlib.qt.__version__,
        'system': system,   # Linux, Windows, ...
        'revision': revision,  # '9fdf926eccce+:2430+'
    }
