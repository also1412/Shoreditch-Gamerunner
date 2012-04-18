# Just ensure the test suite runs

import unittest

class TestTest(unittest.TestCase):
	def test_test(self):
		assert 1 + 2 == 3, "Maths is broken!"