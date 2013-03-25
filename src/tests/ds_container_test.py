
import pytest


# Local imports
from dataset import DataSet, DS_TYPES
from dataset_container import DatasetContainer


@pytest.fixture
def dsc3():
    dsl = []
    for i in range(3):
        name = "Dataset{index}".format(index=i)
        dtype = DS_TYPES[i%2]
        ds = DataSet(display_name=name, kind=dtype)
        dsl.append(ds)
    dst = tuple(dsl)
    dsc = DatasetContainer()
    dsc.add(*dst)
    return dsc


def test_add(dsc3):
    assert len(dsc3) == 3


def test_get_ds(dsc3):
    idn = dsc3.get_id_name_map()
    pick = idn[0][0]
    ds = dsc3[pick]
    assert ds.id == pick


def test_del_ds(dsc3):
    idn_map = dsc3.get_id_name_map()
    did = idn_map[0][0]
    del dsc3[did]
    with pytest.raises(ValueError):
        del dsc3['unlikelyid']
    with pytest.raises(ValueError):
        ds = dsc3[did]


def test_kind(dsc3):
    assert len(dsc3.get_id_name_map('Design variable')) == 2
    assert len(dsc3.get_id_name_map('Sensory profiling')) == 1
    assert len(dsc3.get_id_name_map('Consumer liking')) == 0
    with pytest.raises(ValueError):
        dsc3.get_id_name_map('No type')


dsl_changes = 0
ds_changes = 0

def dsl_poke():
    global dsl_changes
    dsl_changes += 1


def ds_poke():
    global ds_changes
    ds_changes += 1


def test_events(dsc3):
    global dsl_changes
    global ds_changes
    dsc3.on_trait_event(dsl_poke, 'dsl_changed')
    dsc3.on_trait_event(ds_poke, 'ds_changed')
    assert dsl_changes == 0
    dsc3.add(DataSet())
    assert dsl_changes == 1
    idn = dsc3.get_id_name_map()
    del dsc3[idn[0][0]]
    assert dsl_changes == 2

    assert ds_changes == 0
    ds = dsc3[idn[1][0]]
    ds.display_name = "New name"
    assert ds_changes == 1
    ds.kind = "Consumer characteristics"
    assert ds_changes == 2
