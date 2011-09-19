
from os.path import abspath, dirname

from enthought.traits.ui.api import ImageEditor
from enthought.pyface.image_resource import ImageResource
from enthought.pyface.api import SplashScreen, GUI

path = [ abspath(dirname(__file__ ))]
img = ImageResource(
    'ConsumerCheckLogo.png',
    search_path=path
    )
splash = SplashScreen(image=img)

if __name__ == '__main__':
    from time import sleep
    print("Kjorer")
#    gui = GUI()
#    gui.start_event_loop()
    splash.open()
    sleep(10)
    splash.close()
