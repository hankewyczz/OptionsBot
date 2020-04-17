import messageParser as mp
import stringFormat as sf
import unittest

#########
# TESTS #
#########

# messageParser tests

class TestParseContractInfo(unittest.TestCase): # also tests contractSymbolToInfo(cSymbol)
	def setUp(self):
		self.t1, self.d1, self.o1, self.s1, self.str1 = mp.parseContractInfo("$SPY 4/17c $300")
		self.t2, self.d2, self.o2, self.s2, self.str2 = mp.parseContractInfo("spy 4/17c 300")
		self.t3, self.d3, self.o3, self.s3, self.str3 = mp.parseContractInfo("$spy 4/17C $300.00")
		self.t4, self.d4, self.o4, self.s4, self.str4 = mp.parseContractInfo("spy 4-17c 300")

		self.ct1, self.cd1, self.co1, self.cs1 = mp.contractSymbolToInfo(self.str1)
		self.ct2, self.cd2, self.co2, self.cs2 = mp.contractSymbolToInfo(self.str2)
		self.ct3, self.cd3, self.co3, self.cs3 = mp.contractSymbolToInfo(self.str3)
		self.ct4, self.cd4, self.co4, self.cs4 = mp.contractSymbolToInfo(self.str4)
	
	def testTickerFormatting(self):
		self.setUp()
		self.assertEqual(self.t1, self.ct1)
		self.assertEqual(self.t2, self.ct2)
		self.assertEqual(self.t3, self.ct3)
		self.assertEqual(self.t4, self.ct4)

		self.assertEqual(self.t1, self.t2)
		self.assertEqual(self.t1, self.t3)
		self.assertEqual(self.t1, self.t4)

	def testDateFormatting(self):
		self.setUp()
		self.assertEqual(self.d1, self.cd1)
		self.assertEqual(self.d2, self.cd2)
		self.assertEqual(self.d3, self.cd3)
		self.assertEqual(self.d4, self.cd4)

		self.assertEqual(self.d1, self.d2)
		self.assertEqual(self.d1, self.d3)
		self.assertEqual(self.d1, self.d4)

	def testOptionTypeFormatting(self):
		self.setUp()
		self.assertEqual(self.o1, self.co1)
		self.assertEqual(self.o2, self.co2)
		self.assertEqual(self.o3, self.co3)
		self.assertEqual(self.o4, self.co4)

		self.assertEqual(self.o1, self.o2)
		self.assertEqual(self.o1, self.o3)
		self.assertEqual(self.o1, self.o4)

	def testStrikeFormatting(self):
		self.setUp()
		self.assertEqual(self.s1, self.cs1)
		self.assertEqual(self.s2, self.cs2)
		self.assertEqual(self.s3, self.cs3)
		self.assertEqual(self.s4, self.cs4)

		self.assertEqual(self.s1, self.s2)
		self.assertEqual(self.s1, self.s3)
		self.assertEqual(self.s1, self.s4)

	def testSymbolFormatting(self):
		self.setUp()
		self.assertEqual(self.str1, self.str2)
		self.assertEqual(self.str1, self.str3)
		self.assertEqual(self.str1, self.str4)

class TestParseChainInfo(unittest.TestCase):
	def setUp(self):
		self.t1, self.d1 = mp.parseChainInfo("spy 6/19")
		self.t2, self.d2 = mp.parseChainInfo("spy")
		self.t3, self.d3 = mp.parseChainInfo("$SPY")
		self.t4, self.d4 = mp.parseChainInfo("$spy 06-19")

	def testTickerFormatting(self):
		self.setUp()
		self.assertEqual(self.t1, self.t2)
		self.assertEqual(self.t1, self.t3)
		self.assertEqual(self.t1, self.t4)

	def testDateFormatting(self):
		self.setUp()
		self.assertEqual(self.d1, self.d4)
		self.assertEqual(self.d2, self.d3)

class TestParseDurationInfo(unittest.TestCase):
	def setUp(self):
		self.n1 = mp.parseDurationInfo("7d")
		self.n2 = mp.parseDurationInfo("7D")
		self.n3 = mp.parseDurationInfo("1w")
		self.n4 = mp.parseDurationInfo("1m", maxDur=7)

	def testDuration(self):
		self.setUp()
		self.assertEqual(self.n1, self.n2)
		self.assertEqual(self.n1, self.n3)
		self.assertEqual(self.n1, self.n4)


## stringFormat tests
class TestFormatStrikeAsString(unittest.TestCase):
	def setUp(self):
		self.s1 = sf.formatStrikeAsString("300.000")
		self.s2 = sf.formatStrikeAsString("00300000")
		self.s3 = sf.formatStrikeAsString("25.100")

	def testFormatStrikeAsString(self):
		self.setUp()
		self.assertEqual(self.s1, "00300000")
		self.assertEqual(self.s2, "00300000")
		self.assertEqual(self.s3, "00025100")

class TestFormatStrike(unittest.TestCase):
	def setUp(self):
		self.s1, self.ss1 = sf.formatStrike("300")
		self.s2, self.ss2 = sf.formatStrike("300.00")
		self.s3, self.ss3 = sf.formatStrike("300.000")
		self.s4, self.ss4 = sf.formatStrike("300.0000")
		self.s5, self.ss5 = sf.formatStrike("300.")

	def testStrike(self):
		self.setUp()
		self.assertEqual(self.s1, self.s2)
		self.assertEqual(self.s1, self.s3)
		self.assertEqual(self.s1, self.s4)
		self.assertEqual(self.s1, self.s5)

	def testStrikeAsString(self):
		self.setUp()
		self.assertEqual(self.ss1, self.ss2)
		self.assertEqual(self.ss1, self.ss3)
		self.assertEqual(self.ss1, self.ss4)
		self.assertEqual(self.ss1, self.ss5)
		
if __name__ == "__main__":
    unittest.main()