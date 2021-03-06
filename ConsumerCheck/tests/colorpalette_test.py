'''Test color utilities
'''

import pytest
# import warnings


from ..utilities import COLOR_PALETTE, hue_span, value_span


def test_span():
    hs = hue_span(3)
    assert len(hs) == 4
    assert hs == [
        (1.0, 0.5391945751704449, 0.590140480411356),
        (0.8429725599279243, 0.706887320227698, 0.26357896745424747),
        (0.2610992423945111, 0.8196136554124752, 0.5066966292546654),
        (0.0, 0.821137810737985, 0.9856934617090666)]


def test_value():
    vs = value_span(3)
    assert len(vs) == 4
    assert vs == [
        (0.0, 0.2179041208570784, 0.6732349196914583),
        (0.0, 0.45043438565458355, 0.9648039717394253),
        (0.0, 0.7135096969968451, 1.0),
        (0.5498008407365998, 0.998210551838877, 1.0)]
