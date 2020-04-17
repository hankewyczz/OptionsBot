import messageParser as mp
import stringFormat as sf
import unittest

#########
# TESTS #
#########

class TestStringMethods(unittest.TestCase):
	def setUp(self):
		self.t1, self.d1, self.o1, self.s1, self.str1 = mp.parseContractInfo("$SPY 4/17c $300")
		self.t2, self.d2, self.o2, self.s2, self.str2 = mp.parseContractInfo("spy 4/17c 300")
		self.t3, self.d3, self.o3, self.s3, self.str3 = mp.parseContractInfo("$spy 4/17C $300.00")
		self.t4, self.d4, self.o4, self.s4, self.str4 = mp.parseContractInfo("spy 4-17c 300")

	
	def testTickerFormatting(self):
		self.setUp()
		self.assertEqual(self.t1, self.t2)
		self.assertEqual(self.t1, self.t3)
		self.assertEqual(self.t1, self.t4)

	def testDateFormatting(self):
		self.setUp()
		self.assertEqual(self.d1, self.d2)
		self.assertEqual(self.d1, self.d3)
		self.assertEqual(self.d1, self.d4)

	def testOptionTypeFormatting(self):
		self.setUp()
		self.assertEqual(self.o1, self.o2)
		self.assertEqual(self.o1, self.o3)
		self.assertEqual(self.o1, self.o4)

	def testStrikeFormatting(self):
		self.setUp()
		self.assertEqual(self.s1, self.s2)
		self.assertEqual(self.s1, self.s3)
		self.assertEqual(self.s1, self.s4)

	def testSymbolFormatting(self):
		self.setUp()
		self.assertEqual(self.str1, self.str2)
		self.assertEqual(self.str1, self.str3)
		self.assertEqual(self.str1, self.str4)


if __name__ == "__main__":
    unittest.main()