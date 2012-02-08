"""Test PCA plugin

"""

import pytest
import numpy as np
from ui_tab_pca import PcaModel, PcaModelViewHandler, pca_tree_view


def test_ui_mock(test_container):
    test_container.test_subject = PcaModelViewHandler(PcaModel())
    with np.errstate(invalid='ignore'):
        ui = test_container.test_subject.configure_traits(view=pca_tree_view)
