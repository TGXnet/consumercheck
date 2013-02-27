import pytest

# FIXME: To be tested
# * One premap model
# * different datasets and settings
# * Test expected failures


@pytest.fixture
def mock_contaner():
    import traits.api as traits

    class MockContainer(traits.HasTraits):
        standardise = traits.Bool(False)
        pc_to_calc = traits.Int(4)

    return MockContainer()



def test_one_pca(iris_ds, mock_contaner):
    from pca_mvc import APCAModel
    pca = APCAModel(mother_ref=mock_contaner, ds=iris_ds)
    res = pca.result
    print(type(res))
    print(dir(res))
    print("Results")
    print(res.calExplVar())
    print(res.means())
    assert True


def test_tull(dsc_mock):
    dsc_mock.print_traits()
    assert 0
