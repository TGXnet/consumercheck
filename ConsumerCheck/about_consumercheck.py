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

# Std lib imports
import codecs

# ETS imports
from traits.api import HasTraits, HTML
from traitsui.api import View, Item

# Local imports
import ConsumerCheck



def about_html():
    ver = ConsumerCheck.__version__
    with codecs.open('about.tmpl', encoding='utf-8') as fh:
        uabout_tmpl = fh.read()
    return uabout_tmpl.format(ver)



class ConsumerCheckAbout(HasTraits):

    about_render = HTML(about_html())
    traits_view = View(
        Item('about_render', show_label=False),
        title="About",
        height=430,
        width=400,
        buttons=['OK'],
    )



if __name__ == '__main__':
    cca = ConsumerCheckAbout()
    cca.configure_traits()
