import os

from pyface.image_resource import ImageResource
from pyface.api import SplashScreen

img = ImageResource(
    'ConsumerCheckLogo.png',
    search_path=[os.getcwd()],
    )
splash = SplashScreen(image=img)

if __name__ == '__main__':
    from time import sleep
    splash.open()
    sleep(4)
    splash.close()
