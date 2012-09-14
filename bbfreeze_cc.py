import os
# import os.path
import shutil

from bbfreeze import Freezer

FREEZE_VERSION = '0.7.0'
R_VER = '2.15.1'
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
div_lib = ['twisted', 'PIL', 'mercurial', 'nose',
           'win32com', 'reportlab', 'setuptools', 'doctest', 'pygments',
           'pyreadline', 'email']
new_out = []

includes = tuple(['traitsui.wx.tabular_editor', 'traitsui.wx.table_editor', 'enable.savage.trait_defs.ui.wx.svg_button_editor'])
excludes = tuple(qt_lib + ets_lib + gui_lib + num_lib + sci_lib + std_lib + div_lib + new_out)

freeze = Freezer(ff, includes=includes, excludes=excludes)
freeze.addScript("src/consumercheck.py", gui_only=False)
freeze.use_compression = False
freeze.include_py = True
freeze()    # starts the freezing process

# Copy testdata
ds_source = os.path.abspath(os.path.join('src', 'datasets'))
ds_dest = os.path.abspath(os.path.join(ff, 'datasets'))
shutil.copytree(ds_source, ds_dest)

# Copy images
cc_imgs = ['ConsumerCheckLogo.png', 'reset_xy.svg', 'save.svg', 'x_down.svg', 'x_up.svg', 'y_down.svg', 'y_up.svg']
for img in cc_imgs:
    ip = os.path.join('src', img)
    shutil.copy2(ip, ff)

# Copy unzipable packages
# Renember to delete these from library.zip
ets_pack = ['pyface', 'enable', 'traitsui']
for pack in ets_pack:
    pp = os.path.join(os.path.dirname(os.path.dirname(hf)), 'CCDev', 'ETSpackages', pack)
    dst = os.path.join(ff, pack)
    shutil.copytree(pp, dst)

# R dist
rsource = os.path.join(os.path.dirname(os.path.dirname(hf)), 'CCDev', 'Rdist', rf)
rdst = os.path.join(ff, rf)
shutil.copytree(rsource, rdst)

# Conjoint R scripts
rss = os.path.join(hf, 'src', 'pgm')
rsdst = os.path.join(ff, 'pgm')
shutil.copytree(rss, rsdst)


# Dependency investigation
#gr = freeze.mf.graph
# Dumps dependencies graph dot file to dep.dot
# dot -Granksep=4.0 -Tpdf -O dep.dot
#freeze.dump_dot()
# Open browser
#freeze.showxref()
