"""Test PCA plugin

"""
import pytest

# Stdlib imports
import numpy as np

# Local imports
from ui_tab_pca import PCAPlugin


def test_ui_mock(plugin_mother_mock):
    plugin_mother_mock.test_subject = PCAPlugin(plugin_mother_mock)
    # To force populating selection list
    plugin_mother_mock.ds_event = True
    with np.errstate(invalid='ignore'):
        plugin_mother_mock.test_subject.configure_traits()
