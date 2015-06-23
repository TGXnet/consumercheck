
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
    assert len(dsc3.get_id_name_map('Product design')) == 2
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


''' Test persistence

Populate the container with real DataSets from file to verify that it can handle pandas data

1. Create empty dsc, pickle it, read back and verify that it is empty
2. Populate dsc with data sets, pickle it ,read back and verify that it is the same data

Use py.test tempdir for filestorage.

pickle.dump(obj, file[, protocol])
or pickle.dumps(obj[, protocol])
pickle.load(file)
or pickle.loads(string)

Check that ds new_id initiazed correctly

'''
f_name = 'tull.pkl'


def test_save_empty():
    dsc = DatasetContainer()
    dsc.save_datasets(f_name)
    dsto = DatasetContainer()
    dsto.read_datasets(f_name)
    assert len(dsto) == 0
    dsnext = DataSet()
    with pytest.raises(ValueError):
        dsdummy = dsto[dsnext.id]


def test_save_tree(dsc3):
    dsc3.save_datasets(f_name)
    dsto = DatasetContainer()
    dsto.read_datasets(f_name)
    assert len(dsto) == 3
    dsnext = DataSet()
    with pytest.raises(ValueError):
        dsdummy = dsto[dsnext.id]


def test_save_matrixes(all_dsc):
    all_dsc.save_datasets(f_name)
    dsto = DatasetContainer()
    dsto.read_datasets(f_name)
    nm = dsto.get_id_name_map()
    mat_ds = dsto[nm[0][0]]
    print(mat_ds.values)



# def test_create_file(tmpdir):
#     '''http://pytest.org/latest/tmpdir.html'''
#     p = tmpdir.mkdir("sub").join("hello.txt")
#     p.write("content")
#     assert p.read() == "content"
#     print(type(p))
#     assert len(tmpdir.listdir()) == 1
#     assert 0
