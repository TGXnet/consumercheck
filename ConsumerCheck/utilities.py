'''Generate color variations in the L*a*b* color space
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

import random
from colormath.color_objects import LCHabColor, sRGBColor
from colormath.color_conversions import convert_color


# a6cee3 (0.65, 0.81, 0.89, 1.0)
# 1f78b4 (0.12, 0.47, 0.71, 1.0)
# b2df8a (0.7, 0.87, 0.54, 1.0)
# 33a02c (0.2, 0.63, 0.17, 1.0)
# fb9a99 (0.98, 0.6, 0.6, 1.0)
# e31a1c (0.89, 0.1, 0.11, 1.0)
# fdbf6f (0.99, 0.75, 0.44, 1.0)
# ff7f00 (1.0, 0.5, 0.0, 1.0)
# cab2d6 (0.79, 0.7, 0.84, 1.0)

# Dark color palette for plot lines
# R, G, B
COLOR_PALETTE = [
    (0.65, 0.81, 0.89, 1.0),
    (0.12, 0.47, 0.71, 1.0),
    (0.7, 0.87, 0.54, 1.0),
    (0.2, 0.63, 0.17, 1.0),
    (0.98, 0.6, 0.6, 1.0),
    (0.89, 0.1, 0.11, 1.0),
    (0.99, 0.75, 0.44, 1.0),
    (1.0, 0.5, 0.0, 1.0),
    (0.79, 0.7, 0.84, 1.0),
]


# 66C2A5 (0.4, 0.76, 0.65, 1.0)
# FC8D62 (0.99, 0.55, 0.38, 1.0)
# 8DA0CB (0.55, 0.63, 0.8, 1.0)
# E78AC3 (0.91, 0.54, 0.76, 1.0)
# A6D854 (0.65, 0.85, 0.33, 1.0)
# FFD92F (1.0, 0.85, 0.18, 1.0)
# E5C494 (0.9, 0.77, 0.58, 1.0)
# B3B3B3 (0.7, 0.7, 0.7, 1.0)

COLOR_PALETTE2 = [
    (0.4, 0.76, 0.65, 1.0),
    (0.99, 0.55, 0.38, 1.0),
    (0.55, 0.63, 0.8, 1.0),
    (0.91, 0.54, 0.76, 1.0),
    (0.65, 0.85, 0.33, 1.0),
    (1.0, 0.85, 0.18, 1.0),
    (0.9, 0.77, 0.58, 1.0),
    (0.7, 0.7, 0.7, 1.0),
]

cpidx = -1


def from_palette(CP=COLOR_PALETTE):
    global cpidx
    cpidx += 1
    return CP[cpidx % len(CP)]


def h2f(hs):
    r = float(format(int(hs[0:2], 16)/255.0, '.2f'))
    g = float(format(int(hs[2:4], 16)/255.0, '.2f'))
    b = float(format(int(hs[4:6], 16)/255.0, '.2f'))
    return (r, g, b, 1.0)


# Based on Munsell color system
# span/interplo func: lin, log, golden, random
# hue_span(start, stop, span_func, n)
# value_span()
# chroma_span()
# hue_value_2d_span()
#
# There are three axes; L* , c* and h*(deg).

'''
FIXME: New ideas for nicer colors
HSL and HSV
https://stackoverflow.com/questions/43044/algorithm-to-randomly-generate-an-aesthetically-pleasing-color-palette
https://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/
https://en.wikipedia.org/wiki/HSL_and_HSV#Converting_to_RGB
http://devmag.org.za/2012/07/29/how-to-choose-colours-procedurally-algorithms/
https://en.wikipedia.org/wiki/Color_difference#CIE94
https://softwareengineering.stackexchange.com/questions/44929/color-schemes-generation-theory-and-algorithms
https://arstechnica.com/information-technology/2017/05/an-ai-invented-a-bunch-of-new-paint-colors-that-are-hilariously-wrong/
https://en.wikipedia.org/wiki/Color_quantization
https://www.technologyreview.com/s/604026/the-algorithm-expanding-the-science-of-color/
http://www.vandelaydesign.com/ui-design-colors/
https://github.com/google/palette.js/tree/master
'''


def hue_span(n):
    hue_lo = 20
    hue_hi = 220
    l = 75
    c = 60
    step = (hue_hi - hue_lo) / n

    def c_conv(i):
        h = hue_lo + i * step
        rgb = convert_color(LCHabColor(l, c, h), sRGBColor)
        return (rgb.clamped_rgb_r, rgb.clamped_rgb_g, rgb.clamped_rgb_b)

    cr = [c_conv(i) for i in range(n + 1)]
    return cr


def value_span(n):
    l_lo = 20
    l_hi = 100
    h = 270
    c = 80
    step = (l_hi - l_lo) / n

    def c_conv(i):
        l = l_lo + i * step
        rgb = convert_color(LCHabColor(l, c, h), sRGBColor)
        return (rgb.clamped_rgb_r, rgb.clamped_rgb_g, rgb.clamped_rgb_b)

    cr = [c_conv(i) for i in range(n + 1)]
    return cr


def rnd_color(palette=(1.0, 1.0, 1.0, 1.0)):
    ''' Return a random color
    palette: an rgba tuple. A for alpha transparency
    '''
    # rndrgb = tuple([random.random() for _ in range(3)])
    # outrgb = ((palette[0]+rndrgb[0])/2, (palette[1]+rndrgb[1])/2, (palette[2]+rndrgb[2])/2, 1.0)
    # return outrgb
    return tuple([random.random() for _ in range(3)])


if __name__ == '__main__':
    print("Hello")
    li = hue_span(20)
    print(li)
