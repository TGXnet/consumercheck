'''What to test:
 * iterating
 * boundaries
'''

import pytest


# Local imports
from plugin_tree_helper import WindowLauncher, ViewNavigator


def func_one(res, parms):
    class One(object):
        def __init__(self, res, parms):
            self.res = res
            self.parms = parms
        def hello(self):
            return (self.parms[0] + " say " + self.res)

    return One(res, parms)


def func_two(res, parms):
    class Two(object):
        def __init__(self, res, parms):
            self.res = res
            self.parms = parms
        def hello(self):
            return (self.parms[0] + " say " + self.res)

    return Two(res, parms)


def func_three(res, parms):
    class Three(object):
        def __init__(self, res, parms):
            self.res = res
            self.parms = parms
        def hello(self):
            return (self.parms[0] + " say " + self.res)

    return Three(res, parms)


def test_en():
    wl1 = WindowLauncher(node_name='Ones',
                         view_creator=func_one,
                         func_parms=("One",),
                         )
    wl2 = WindowLauncher(node_name='Twos',
                         view_creator=func_two,
                         func_parms=("Two",),
                         )
    wl3 = WindowLauncher(node_name='Threes',
                         view_creator=func_three,
                         func_parms=("Three",),
                         )
    vn = ViewNavigator(res='Hello')
    vn.view_loop.append(wl1)
    vn.view_loop.append(wl2)
    vn.view_loop.append(wl3)
    pto = vn.show_next()
    ptre = vn.show_next()
    pen = vn.show_next()
    ptre = vn.show_previous()
    pto = vn.show_previous()
    assert pto.hello() == 'Two say Hello'
