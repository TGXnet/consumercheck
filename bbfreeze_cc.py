import os
# import os.path
import shutil

from bbfreeze import Freezer

FREEZE_VERSION = '1.1.2'
R_VER = '3.0.2'
# freeze folder
ff = "consumercheck-" + FREEZE_VERSION
# R folder
rf = "R-" + R_VER
# Home folder for source
hf = os.path.dirname(os.path.abspath(__file__))

# Modules I have tried to exclude:
# unittest: "numpy/testing/__init__.py"
# ditutils: pyface\toolkit.py -> NotImplementedError
#

qt_lib = ['traitsui.qt4', 'pyface.ui.qt4', 'pyface.qt', 'PyQt4', 'PySide']
xw_lib = []
ets_lib = ['pyface.workbench', 'etsdevtools', 'apptools']
gui_lib = ['Tkinter', 'vtk', 'tvtk']
num_lib = ['numpy.f2py', 'numpy.distutils']
sci_lib = ['IPython', 'matplotlib', 'scimath']
std_lib = []
div_lib = ['twisted', 'mercurial', 'nose',
           'win32com', 'reportlab', 'setuptools', 'doctest', 'pygments',
           'pyreadline', 'email']
test_out = []

includes = tuple(['traitsui.wx.tabular_editor',
                  'traitsui.wx.table_editor',
                  'enable.savage.trait_defs.ui.wx.svg_button_editor'])
excludes = tuple(qt_lib + ets_lib + gui_lib + num_lib +
                 sci_lib + std_lib + div_lib + test_out)

freeze = Freezer(ff, includes=includes, excludes=excludes)
freeze.addScript("ConsumerCheck/cc_start.py", gui_only=False)
freeze.use_compression = False
freeze.include_py = True
freeze()    # starts the freezing process

# Copy testdata
#ds_source = os.path.abspath(os.path.join('src', 'datasets'))
#ds_dest = os.path.abspath(os.path.join(ff, 'datasets'))
#shutil.copytree(ds_source, ds_dest)

# Copy images
cc_imgs = ['ConsumerCheckLogo.png', 'reset_xy.svg', 'save.svg', 'x_down.svg',
           'x_up.svg', 'y_down.svg', 'y_up.svg']
for img in cc_imgs:
    ip = os.path.join('ConsumerCheck', img)
    shutil.copy2(ip, ff)

gsource = os.path.join(hf, 'ConsumerCheck', 'graphics')
gdst = os.path.join(ff, 'graphics')
shutil.copytree(gsource, gdst)

# Copy unzipable packages
# Renember to delete these from library.zip
ets_pack = ['pyface', 'enable', 'traitsui']
for pack in ets_pack:
    pp = os.path.join(hf, 'ETSpackages', pack)
    dst = os.path.join(ff, pack)
    shutil.copytree(pp, dst)

# R dist
rsource = os.path.join(hf, 'Rdist', rf)
rdst = os.path.join(ff, rf)
shutil.copytree(rsource, rdst)

# Conjoint R scripts
rss = os.path.join(hf, 'ConsumerCheck', 'rsrc')
rsdst = os.path.join(ff, 'rsrc')
shutil.copytree(rss, rsdst)

# User documentation
doc_source = os.path.join(hf, 'docs-user', 'build', 'html')
doc_dest = os.path.join(ff, 'help-docs')
shutil.copytree(doc_source, doc_dest)

# Dependency investigation
#gr = freeze.mf.graph
# Dumps dependencies graph dot file to dep.dot
# dot -Granksep=4.0 -Tpdf -O dep.dot
#freeze.dump_dot()
# Open browser
#freeze.showxref()
