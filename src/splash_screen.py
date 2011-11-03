
from os.path import abspath, dirname

from enthought.pyface.image_resource import ImageResource
from enthought.pyface.api import SplashScreen

path = [ abspath(dirname(__file__ ))]
img = ImageResource(
    'ConsumerCheckLogo.png',
    search_path=path
    )
splash = SplashScreen(image=img)

if __name__ == '__main__':
    from time import sleep
    splash.open()
    sleep(10)
    splash.close()
