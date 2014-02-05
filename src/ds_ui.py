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

# Enthought imports
from traits.api import Button
from traitsui.api import Handler, View, Item
from traitsui.menu import OKButton, CancelButton

# Local imports
from dataset import DataSet
from ds_slicer_view import ds_slicer_view


class DSListTabHandler(Handler):
    show_slicer = Button('Variables and objects selection')


    def handler_show_slicer_changed(self, info):
        info.object.edit_traits(view=ds_slicer_view)


ds_list_tab = View(
    Item('display_name'),
    Item('kind'),
    # Item('n_objs', style='readonly'),
    # Item('n_vars', style='readonly'),
    Item('handler.show_slicer'),
    handler=DSListTabHandler(),
    )


if __name__ == '__main__':
    from importer_main import ImporterMain
    fi = ImporterMain()
    ds = fi.import_data('./datasets/Vine/A_labels.txt', True, True)
    ds.configure_traits(view=ds_list_tab)
