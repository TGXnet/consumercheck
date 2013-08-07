'''Generate color variations in the L*a*b* color space
'''
# import numpy as _np
from colormath.color_objects import LCHabColor


COLOR_PALETTE = [
    (0.65, 0.81, 0.89, 1.0),
    (0.12, 0.47, 0.71, 1.0),
    (0.70, 0.87, 0.54, 1.0),
    (0.21, 0.63, 0.17, 1.0),
    (0.98, 0.60, 0.59, 1.0),
    (0.89, 0.10, 0.11, 1.0),
    (0.99, 0.75, 0.43, 1.0),
    (1.00, 0.50, 0.00, 1.0),
    (0.79, 0.70, 0.84, 1.0),
    (0.41, 0.24, 0.60, 1.0)
    ]

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
    step = (hue_hi - hue_lo)/n

    cr = []
    for i in range(n+1):
        lch = LCHabColor(l, c, hue_lo+i*step)
        rgb = lch.convert_to('rgb')
        r, g, b = rgb.get_value_tuple()
        f_rgb = (1.0*r/255, 1.0*g/255, 1.0*b/255)
        cr.append(f_rgb)

    return cr


def value_span(n):
    l_lo = 20
    l_hi = 100
    h = 270
    c = 80
    step = (l_hi - l_lo)/n

    cr = []
    for i in range(n+1):
        lch = LCHabColor(l_lo+i*step, c, h)
        rgb = lch.convert_to('rgb')
        r, g, b = rgb.get_value_tuple()
        f_rgb = (1.0*r/255, 1.0*g/255, 1.0*b/255)
        cr.append(f_rgb)

    return cr


if __name__ == '__main__':
    print("Hello")
    li = hue_span(20)
    print(li)
