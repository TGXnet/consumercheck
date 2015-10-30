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

import os

from pyface.image_resource import ImageResource
from pyface.api import SplashScreen

# Local imports
import cc_config as conf


img = ImageResource(
    'ConsumerCheckLogo.png',
    search_path=[conf.graphics_path()],
    )
splash = SplashScreen(image=img)

if __name__ == '__main__':
    from time import sleep
    splash.open()
    sleep(4)
    splash.close()
