
import pytest

# To be tested
from conjoint_machine import ConjointMachine
from conjoint_model import Conjoint
from dataset_container import get_ds_by_name

# Test sharing of same R env
# How to compare results


# Test all three structures
@pytest.mark.slow
@pytest.mark.parametrize("structure", [1, 2, 3])
def test_all_struct(conjoint_dsc, structure):
    consAttr = get_ds_by_name('Consumers', conjoint_dsc)
    odflLike = get_ds_by_name('Odour-flavor', conjoint_dsc)
    # consistencyLike = get_ds_by_name('Consistency', conjoint_dsc)
    # overallLike = get_ds_by_name('Overall', conjoint_dsc)
    designVar = get_ds_by_name('Tine yogurt design', conjoint_dsc)
    selected_structure = structure
    selected_consAttr = ['Sex']
    selected_designVar = ['Flavour', 'Sugarlevel']

    cm = ConjointMachine()
    res = cm.synchronous_calculation(
        selected_structure, consAttr, selected_consAttr,
        designVar, selected_designVar, odflLike, True)
    
    print(res.keys())


@pytest.mark.slow
def test_r_data_merge(conjoint_dsc):
    consAttr = get_ds_by_name('Consumers', conjoint_dsc)
    odflLike = get_ds_by_name('Odour-flavor', conjoint_dsc)
    # consistencyLike = get_ds_by_name('Consistency', conjoint_dsc)
    # overallLike = get_ds_by_name('Overall', conjoint_dsc)
    designVar = get_ds_by_name('Tine yogurt design', conjoint_dsc)
    selected_structure = 1
    selected_consAttr = ['Sex']
    # selected_consAttr = ['Sex', 'Age']
    selected_designVar = ['Flavour', 'Sugarlevel']
    # selected_designVar = ['Flavour']

    cm = ConjointMachine()
    res = cm.synchronous_calculation(
        selected_structure, consAttr, selected_consAttr,
        designVar, selected_designVar, odflLike, False)
    
    print(res.keys())
    assert True


@pytest.mark.slow
def test_category_strings(conjoint_dsc):
    e_attr = get_ds_by_name('Estland consumers', conjoint_dsc)
    e_liking = get_ds_by_name('Estland liking data', conjoint_dsc)
    design = get_ds_by_name('Barley bread design', conjoint_dsc)

    selected_structure = 1
    selected_consAttr = ['Sex', 'Age']
    # [u'Barley', u'Salt']
    selected_designVar = ['Barley', 'Salt']

    cm = ConjointMachine()
    res = cm.synchronous_calculation(
        selected_structure, e_attr, selected_consAttr,
        design, selected_designVar, e_liking, True)
    
    print(res['lsmeansTable']['rowNames'])
    print(res['lsmeansTable']['colNames'])


def test_completeness(conjoint_dsc):
    e_attr = get_ds_by_name('Estland consumers', conjoint_dsc)
    e_liking = get_ds_by_name('Estland liking data', conjoint_dsc)
    design = get_ds_by_name('Barley bread design', conjoint_dsc)

    selected_structure = 1
    # [u'Sex', u'Age', u'WB', u'BB', u'Edu', u'Health']
    selected_consAttr = ['Sex', 'Age', 'Edu']
    # [u'Barley', u'Salt']
    selected_designVar = ['Barley', 'Salt']

    cm = ConjointMachine(start_r=False)
    cm._prepare_data(
        selected_structure, e_attr, selected_consAttr,
        design, selected_designVar, e_liking, False)


# test async calculation
@pytest.mark.slow
@pytest.mark.parametrize("merge", [True, False])
def test_async_calc(conjoint_dsc, merge):
    from time import sleep

    class RunState(object):
        def __init__(self):
            self.is_done = True
            self.messages = ''

    run_state = RunState()

    consAttr = get_ds_by_name('Consumers', conjoint_dsc)
    odflLike = get_ds_by_name('Odour-flavor', conjoint_dsc)
    # consistencyLike = get_ds_by_name('Consistency', conjoint_dsc)
    # overallLike = get_ds_by_name('Overall', conjoint_dsc)
    designVar = get_ds_by_name('Tine yogurt design', conjoint_dsc)

    selected_structure = 1
    selected_consAttr = ['Sex']
    selected_designVar = ['Flavour', 'Sugarlevel']

    cm = ConjointMachine(run_state)
    cm.schedule_calculation(
        selected_structure, consAttr, selected_consAttr,
        designVar, selected_designVar, odflLike, merge)

    while(not run_state.is_done):
        print("Waiting for result")
        sleep(1)
    sleep(1)
    res = cm.get_result()
    print(run_state.messages)
    print(res.keys())
    assert True


def test_model(conjoint_dsc):
    design = get_ds_by_name('Tine yogurt design', conjoint_dsc)
    liking = get_ds_by_name('Odour-flavor', conjoint_dsc)
    consumers = get_ds_by_name('Consumers', conjoint_dsc)
    cj = Conjoint(design_set=design, cons_liking=liking, consumer_attr_set=consumers)
    cj.chosen_design_vars = ['Flavour', 'Sugarlevel']
    cj.chosen_consumer_attr_vars = ['Sex']
    # cj.print_traits()
    # cj_res = cj.res
    # print(cj_res)
    assert True
