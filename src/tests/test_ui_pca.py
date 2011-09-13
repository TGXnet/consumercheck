
import unittest
import test_tools

# ConsumerCheck imports
from ui_tab_pca import PcaModel, PcaModelViewHandler, pca_tree_view

class TestUiTabPCA(unittest.TestCase):
    def setUp(self):
        # Show the plot?
        self.show = True
        pmvh = PcaModelViewHandler( PcaModel() )
        self.test_main = test_tools.TestMain( to_be_tested=pmvh )

    ## def test1PlotScores(self):
    ##      test_main = test_tools.TestMain( to_be_tested=PcaModel() )
    ##      test_main.to_be_tested.plot_scores('polser', self.show)

    ## def test2PlotLoadings(self):
    ##      test_main = test_tools.TestMain( to_be_tested=PcaModel() )
    ##      test_main.to_be_tested.plot_loadings('polser', self.show)

    ## def test3PlotCorrLoadings(self):
    ##      test_main = test_tools.TestMain( to_be_tested=PcaModel() )
    ##      test_main.to_be_tested.plot_corr_loading('polser', self.show)

    ## def test4PlotExplaindedVariance(self):
    ##      test_main = test_tools.TestMain( to_be_tested=PcaModel() )
    ##      test_main.to_be_tested.plot_expl_var('polser', self.show)

    ## def test5PlotOverview(self):
    ##      test_main = test_tools.TestMain( to_be_tested=PcaModel() )
    ##      test_main.to_be_tested.plot_overview(['polser', 'ost'], self.show)

    def test6treeUI(self):
        self.test_main.to_be_tested.configure_traits( view=pca_tree_view )
        # self.test_main.to_be_tested.configure_traits()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
