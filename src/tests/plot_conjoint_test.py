
import pytest

# Scipy lib imports
import numpy as np

import plot_conjoint
import conjoint_gui


def test_main_effect_slice(conj_res):
    labels = ['Flavour', 'Sugarlevel', 'Sex']
    res_ds = conjoint_gui.cj_res_ds_adapter(conj_res.lsmeansTable)
    print(res_ds.mat.head())
    ref_res = plot_conjoint.slice_main_effect_data(conj_res.lsmeansTable, labels[2])
    test_res = plot_conjoint.slice_main_effect_ds(res_ds, labels[2])
    print("Ref set")
    print(ref_res)
    print("Test set")
    print(test_res)
    assert np.array_equal(ref_res.values, test_res.values)


def test_interaction_slice(conj_res):
    labels = ['Flavour', 'Sugarlevel', 'Sex']
    res_ds = conjoint_gui.cj_res_ds_adapter(conj_res.lsmeansTable)
    print(res_ds.mat.head())
    ref_res = plot_conjoint.slice_interaction_data(conj_res.lsmeansTable, labels[1], labels[2])
    test_res = plot_conjoint.slice_interaction_ds(res_ds, labels[1], labels[2])
    print("Ref set")
    print(ref_res)
    print("Test set")
    print(test_res)
    assert np.array_equal(ref_res.values, test_res.values)


def test_main_p_value(conj_res):
    labels = ['Flavour', 'Sugarlevel', 'Sex']
    res_ds = conjoint_gui.cj_res_ds_adapter(conj_res.anovaTable)
    print(res_ds.mat.head())
    ref_p = plot_conjoint.old_get_main_p_value(conj_res.anovaTable, labels[2])
    test_p = plot_conjoint.get_main_p_value(res_ds, labels[2])
    print(ref_p)
    print(test_p)
    assert test_p == ref_p



def test_interaction_p_value(conj_res):
    labels = ['Flavour', 'Sugarlevel', 'Sex']
    res_ds = conjoint_gui.cj_res_ds_adapter(conj_res.anovaTable)
    print(res_ds.mat.head())
    ref_p = plot_conjoint.old_get_interaction_p_value(conj_res.anovaTable, labels[0], labels[1])
    test_p = plot_conjoint.get_interaction_p_value(res_ds, labels[0], labels[1])
    print(ref_p)
    print(test_p)
    assert test_p == ref_p






