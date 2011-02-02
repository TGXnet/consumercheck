# -*- coding: utf-8 -*-

import unittest
import test_tools

#ConsumerCheck imports
from dsl_check_list import CheckListController, check_view


class TestSelectionListUi(unittest.TestCase):

	def setUp(self):
		self.show = True
		self.test_main = test_tools.TestMain()

	def testTull(self):
		chief = CheckListController( model=self.test_main.dsl )
		chief.print_traits()
		chief.model.print_traits()
		self.test_main.dsl.configure_traits( view=check_view, handler=chief, kind='nonmodal' )


if __name__ == '__main__':
	unittest.main()
