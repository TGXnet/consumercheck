# -*- coding: utf-8 -*-
"""
Created on Sat Apr 04 11:32:56 2015

@author: thomas
"""

from hookutils import collect_submodules, collect_data_files

wx = collect_submodules('enable.wx')
qt = collect_submodules('enable.qt4')
trait_defs_ui_wx = collect_submodules('enable.trait_defs.ui.wx')
trait_defs_ui_qt = collect_submodules('enable.trait_defs.ui.qt4')
savage_trait_defs_ui_wx = collect_submodules('enable.savage.trait_defs.ui.wx')
savage_trait_defs_ui_qt = collect_submodules('enable.savage.trait_defs.ui.qt4')

hiddenimports = wx + qt + trait_defs_ui_wx + trait_defs_ui_qt + savage_trait_defs_ui_wx + savage_trait_defs_ui_qt

img = collect_data_files('enable')
datas = img 
