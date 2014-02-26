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

from traits.api import HasTraits, HTML
from traitsui.api import View, Item


class ConsumerCheckAbout(HasTraits):
    about_html = '''
    <body text="#404040" bgcolor="#f0f0f0">
    <div align="center"><font size="7">About ConsumerCheck</font></div>
    <p align="center">ConsumerCheck is a program for statistical analysis and visualization.</p>
    <p align="center">ConsumerCheck development:<br />Thomas Graff, <a href="http://www.tgxnet.no">TGXnet</a></p>
    <p align="center">Python wrapping of R code and software development management:<br /><a href="http://www.nofima.no/en/person/oliver.tomic">Oliver Tomic</a>, <a href="http://www.nofima.no">Nofima</a></p>
    <p align="center">Version: 1.0.1</p>
    <p align="center">ConsumerCheck is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    ConsumerCheck is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ConsumerCheck.  If not, see
    <a href="http://www.gnu.org/licenses/">http://www.gnu.org/licenses/</a>.</p>
    </body>
    '''
    about_render = HTML(about_html)
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
