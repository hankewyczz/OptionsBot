import optionsUtil as ou
import unittest


'''
For the purposes of testing here, we use 4 tickers:
SPY, SPX, DJIA, COMP

Seeing as I don't foresee a complete global economic collapse in the next couple of years, 
if the tests fail, it is more than likely due to the Yahoo API changing (or me breaking a method).
(ie. these tickers should always work)
'''

class TestLoadFrom(unittest.TestCase):
	def setUp(self):
		self.d1 = ou.loadFrom("https://query1.finance.yahoo.com/v7/finance/quote?symbols=SPY")
		self.d2 = ou.loadFrom("https://query1.finance.yahoo.com/v7/finance/quote?symbols=SPX")
		self.d3 = ou.loadFrom("https://query1.finance.yahoo.com/v7/finance/quote?symbols=DJIA")
		self.d4 = ou.loadFrom("https://query1.finance.yahoo.com/v7/finance/quote?symbols=COMP")
		
	def testLoad(self):
		self.setUp()
		self.assertEqual(self.d1['quoteResponse']['result'][0]['symbol'], "SPY")
		self.assertEqual(self.d2['quoteResponse']['result'][0]['symbol'], "SPX")
		self.assertEqual(self.d3['quoteResponse']['result'][0]['symbol'], "DJIA")
		self.assertEqual(self.d4['quoteResponse']['result'][0]['symbol'], "COMP")




if __name__ == "__main__":
    unittest.main()