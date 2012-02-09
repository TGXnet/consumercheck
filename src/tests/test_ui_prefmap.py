"""Test Prefmap plugin

"""

# Stdlib imports
import pytest
import numpy as np

# Local imports
from ui_tab_prefmap import PrefmapModel, PrefmapModelViewHandler, prefmap_tree_view


def test_ui_mock(test_container):
    test_container.test_subject = PrefmapModelViewHandler(PrefmapModel())
    with np.errstate(invalid='ignore'):
        ui = test_container.test_subject.configure_traits(view=prefmap_tree_view)
