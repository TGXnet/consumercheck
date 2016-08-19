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

from colormath.color_objects import LCHabColor, sRGBColor
from colormath.color_conversions import convert_color


# Dark color palette for plot lines
COLOR_PALETTE = [
    (0.00, 0.00, 0.00, 1.0),
    (0.99, 0.00, 0.00, 1.0),
    (0.00, 0.00, 0.00, 1.0),
    (0.99, 0.00, 0.00, 1.0)]

# Based on Munsell color system
# span/interplo func: lin, log, golden, random
# hue_span(start, stop, span_func, n)
# value_span()
# chroma_span()
# hue_value_2d_span()
#
# There are three axes; L* , c* and h*(deg).


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


if __name__ == '__main__':
    print("Hello")
    li = hue_span(20)
    print(li)
