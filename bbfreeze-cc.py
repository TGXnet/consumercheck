import os.path
import shutil

from bbfreeze import Freezer

FREEZE_VERSION = '0.6.0'
R_VERSION = '2.11.1'
# freeze folder
ff = "consumercheck-" + FREEZE_VERSION
# R folder
rf = "R-" + R_VERSION

exclude1 = ['pydoc', 'pydoc_topics', 'pkg_resources', 'doctest', 'difflib',
            'cookielib', 'urllib', 'urllib2' 'acb', 'anydbm', 'ast', 'base64',
            'pstats', 'TiffImagePlugin', 'uuid', 'modulefinder', 'xml', 'PIL']

#includes = pyface + pyface_action + traitsui + enable
includes = []
excludes = []

freeze = Freezer(ff, includes=includes, excludes=excludes)
freeze.addScript("src/consumercheck.py", gui_only=False)
freeze.use_compression = False
freeze.include_py = True
freeze()    # starts the freezing process

# xcopy src\datasets consumercheck-0.5.2\datasets\ /S /Q
ds_source = os.path.abspath(os.path.join('src', 'datasets'))
ds_dest = os.path.abspath(os.path.join(ff, 'datasets'))
shutil.copytree(ds_source, ds_dest)

# xcopy src\R-2.11.1 consumercheck-0.5.2\R-2.11.1\ /S /Q
#r_source = os.path.abspath(os.path.join('src', rf))
#r_dest = os.path.abspath(os.path.join(ff, rf))
#shutil.copytree(r_source, r_dest)

to_delete = [
    'QtWebKit4.dll', 'QtGui4.dll', 'PyQt4.QtGui.pyd', 'QtCore4.dll',
    'PyQt4.QtCore.pyd', 'QtNetwork4.dll', 'PyQt4.QtWebKit.pyd',
    '_ssl.pyd', 'PIL._imaging.pyd',
    ]
#for file in to_delete:
#    os.remove(os.path.abspath(os.path.join(ff, file)))
