
import pytest

# To be tested
from conjoint_machine import ConjointMachine

# Test sharing of same R env
# How to compare results


# Test all three structures
@pytest.mark.parametrize("structure", [1, 2, 3])
def test_all_struct(conjoint_dsc, structure):
    consAttr = conjoint_dsc.get_by_id('consumerattributes')
    odflLike = conjoint_dsc.get_by_id('odour-flavour_liking')
    consistencyLike = conjoint_dsc.get_by_id('consistency_liking')
    overallLike = conjoint_dsc.get_by_id('overall_liking')
    designVar = conjoint_dsc.get_by_id('design')
    selected_structure = structure
    selected_consAttr = ['Sex']
    selected_designVar = ['Flavour', 'Sugarlevel']

    cm = ConjointMachine()
    res = cm.synchronous_calculation(
        selected_structure, consAttr, selected_consAttr,
        designVar, selected_designVar, odflLike, True)
    
    print(res.keys())



def test_r_data_merge(conjoint_dsc):
    consAttr = conjoint_dsc.get_by_id('consumerattributes')
    odflLike = conjoint_dsc.get_by_id('odour-flavour_liking')
    consistencyLike = conjoint_dsc.get_by_id('consistency_liking')
    overallLike = conjoint_dsc.get_by_id('overall_liking')
    designVar = conjoint_dsc.get_by_id('design')
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
    # assert 0


def test_category_strings(conjoint_dsc):
    e_attr = conjoint_dsc.get_by_id('bb_e_consattr')
    e_liking = conjoint_dsc.get_by_id('bb_e_liking')
    design = conjoint_dsc.get_by_id('bb_design')
    selected_structure = 1
    # [u'Sex', u'Age', u'WB', u'BB', u'Edu', u'Health']
    selected_consAttr = ['Sex', 'Age']
    # [u'Barley', u'Salt']
    selected_designVar = ['Barley', 'Salt']

    cm = ConjointMachine()
    res = cm.synchronous_calculation(
        selected_structure, e_attr, selected_consAttr,
        design, selected_designVar, e_liking, True)
    
    print(res['lsmeansTable']['rowNames'])
    print(res['lsmeansTable']['colNames'])


# test async calculation
@pytest.mark.parametrize("merge", [True, False])
def test_async_calc(conjoint_dsc, merge):
    from time import sleep

    class RunState(object):
        def __init__(self):
            self.is_done = True
            self.messages = ''

    run_state = RunState()

    consAttr = conjoint_dsc.get_by_id('consumerattributes')
    odflLike = conjoint_dsc.get_by_id('odour-flavour_liking')
    consistencyLike = conjoint_dsc.get_by_id('consistency_liking')
    overallLike = conjoint_dsc.get_by_id('overall_liking')
    designVar = conjoint_dsc.get_by_id('design')
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
    # assert 0
