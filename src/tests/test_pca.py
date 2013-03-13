'''Things to test:
 * Check max_pc
 * calc_n_pc to max_pc
 * Results sets and shapes
 * Check zero variance test
 * Check that res is a new copy each time (unique id?)
 * Calculation with missing data
'''
import pytest
from tests.conftest import imp_ds

# Local imports
from pca_model import Pca, InComputeable
from pca_gui import PcaController, TestOnePcaTree, PcaPlugin, PcaPluginController, pca_plugin_view


@pytest.mark.model
def test_pca_results():
    # Folder, File name, Display name, DS type
    ds_meta = ('Vine', 'A_labels.txt', 'Vine set A', 'Consumer liking')
    ds = imp_ds(ds_meta)
    print(ds.mat)
    pca = Pca(ds=ds)
    assert pca.calc_n_pc == pca.max_pc == 3
    res = pca.pca_res
    # Check if all expected result sets is in res
    expected_sets = ['scores', 'loadings', 'expl_var', 'corr_loadings']
    attrs = dir(res)
    assert all([s in attrs for s in expected_sets])
    # Check row and column headings
    for dsn in expected_sets:
        ds  = getattr(res, dsn)
        print(ds.display_name, 'var', ds.var_n)
        print(ds.display_name, 'obj', ds.obj_n)


@pytest.mark.model
def test_zero_var(zero_var_ds):
    pca = Pca(ds=zero_var_ds)
    pca.standardise = True
    print(zero_var_ds.mat)
    with pytest.raises(InComputeable):
        res = pca.pca_res


@pytest.mark.gui
def test_one_pca_tree(simple_ds):
    pca = Pca(ds=simple_ds)
    pc = PcaController(pca)
    one_pca = TestOnePcaTree(one_pca=pc)
    one_pca.configure_traits()


@pytest.mark.gui
def test_pca_gui_update(synth_dsc):
    pcap = PcaPlugin(dsc=synth_dsc)
    ppc = PcaPluginController(pcap)
    ppc.configure_traits(view=pca_plugin_view)
