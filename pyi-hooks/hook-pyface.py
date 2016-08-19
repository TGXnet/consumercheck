# -*- coding: utf-8 -*-
"""
Created on Fri Apr 03 20:33:21 2015

@author: thomas
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# wx = collect_submodules('pyface.wx')
qt = collect_submodules('pyface.qt')
# ui_wx = collect_submodules('pyface.ui.wx')
ui_qt = collect_submodules('pyface.ui.qt4')

hiddenimports = qt + ui_qt

img = collect_data_files('pyface')
datas = img 
