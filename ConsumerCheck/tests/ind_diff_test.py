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
import ind_diff_gui as idg
import ind_diff_model as idm
import dataset_container as dc


def test_one():
    one_branch = False

    # Folder, File name, Display name, DS type
    cheese_L_meta = ('Cheese', 'ConsumerLiking.txt',
                     'Cheese liking', 'Consumer liking')
    cheese_A_meta = ('Cheese', 'ConsumerValues.txt',
                     'Consumer values', 'Consumer characteristics')
    ham_L_meta = ('HamData', 'Ham_consumer_liking_categories.csv',
                  'Ham linking - categories', 'Consumer liking')
    ham_A_meta = ('HamData', 'Ham_consumer_attributes_categories.csv',
                  'Ham attributes - categories', 'Consumer characteristics')
    CL = imp_ds(*cheese_L_meta)
    CA = imp_ds(*cheese_A_meta)
    # HL = imp_ds(*ham_L_meta)
    # HA = imp_ds(*ham_A_meta)

    if one_branch:
        ind_diff = idm.IndDiff(ds_L=CL, ds_A=CA)
        # pc = IndDiffController(ind_diff)
        # test = pb.TestOneNode(one_model=pc)
        # test.configure_traits(view=pb.dummy_view(ind_diff_nodes))
    else:
        dsc = dc.DatasetContainer()
        dsc.add(imp_ds(*ham_L_meta))
        dsc.add(imp_ds(*ham_A_meta))
        dsc.add(imp_ds(*cheese_L_meta))
        dsc.add(imp_ds(*cheese_A_meta))
        ind_diff = idg.IndDiffCalcContainer(dsc=dsc)
        ppc = idg.IndDiffPluginController(ind_diff)
        ppc.configure_traits(
            view=idg.ind_diff_plugin_view)
