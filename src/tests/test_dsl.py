
import pytest


def test_dsl(dsl_data):
    assert dsl_data.get_id_list_by_type('Sensory profiling') == ['c_labels', 'sensorydata']
    assert dsl_data.get_id_list_by_type('Consumer liking') == ['a_labels', 'consumerliking']
