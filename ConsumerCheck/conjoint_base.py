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

# ETS imports
import traits.api as _traits
import traitsui.api as _traitsui

# Local imports
from plugin_tree_helper import WindowLauncher
from plugin_base import ModelController


class PluginController(_traitsui.Controller):
    update_tree = _traits.Event()
    selected_object = _traits.Any()
    edit_node = _traits.Instance(ModelController)
    win_handle = _traits.Any()

    def init(self, info):
        self.selected_object = self.model
        self.win_handle = info.ui.control
        # self.edit_node = self.model.calculator
        return True

    @_traits.on_trait_change('selected_object')
    def _tree_selection_made(self, obj, name, new):
        if isinstance(new, ModelController):
            self.edit_node = new
        elif isinstance(new, WindowLauncher):
            self.edit_node = new.owner_ref
        else:
            self.edit_node = self.dummy_model_controller

    @_traits.on_trait_change('update_tree')
    def _tree_update(self, info):
        print("Tree update")
