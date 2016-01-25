# -*- coding: utf-8 -*-
"""
Created on Fri Apr 03 21:12:50 2015

@author: thomas
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# wx = collect_submodules('traitsui.wx')
qt = collect_submodules('traitsui.qt4')

hiddenimports = qt

img = collect_data_files('traitsui')
datas = img 
