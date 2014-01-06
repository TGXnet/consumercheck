
import pytest
from tests.conftest import imp_ds

# Local imports
from prefmap_model import Prefmap
from prefmap_gui import (PrefmapController, PrefmapPluginController,
                         prefmap_nodes, prefmap_plugin_view)
from plugin_base import (CalcContainer, TestOneNode, dummy_view)


@pytest.mark.model
def test_prefmap_results():
    # Folder, File name, Display name, DS type
    ds_C_meta = ('Cheese', 'ConsumerLiking.txt', 'Cheese liking', 'Consumer liking')
    ds_S_meta = ('Cheese', 'SensoryData.txt', 'Cheese profiling', 'Sensory profiling')
    C = imp_ds(ds_C_meta)
    S = imp_ds(ds_S_meta)
    print('C', C.mat.shape)
    print('S', S.mat.shape)
    prefmap = Prefmap(ds_C=C, ds_S=S,
                      int_ext_mapping='External'
                      )
    prefmap.print_traits()
    result = prefmap.res
    print(result.corr_loadings_y.mat)
    assert True


@pytest.mark.ui
def test_one_prefmap_tree(simple_ds):
    prefmap = Prefmap(ds=simple_ds)
    pc = PrefmapController(prefmap)
    test = TestOneNode(one_model=pc)
    test.configure_traits(view=dummy_view(prefmap_nodes))


@pytest.mark.ui
def test_prefmap_gui_update(prefmap_dsc):
    prefmap = CalcContainer(dsc=prefmap_dsc)
    ppc = PrefmapPluginController(prefmap)
    ppc.configure_traits(view=prefmap_plugin_view)
