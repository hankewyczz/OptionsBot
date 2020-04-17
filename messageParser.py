# A bot for parsing text into options data
from datetime import datetime
from dateutil import parser, tz
import urllib.request
import json
import re
import unittest

import stringFormat as sf

'''
##############
## OVERVIEW ##
##############

parseContractInfo(String string)
	Parses the given string into the relevant contract terms

parseChainInfo(String string)
	Given an option chain request, this returns the parsed ticker and date (if exists)

parseChainInfoAtDate(String ticker, int timestamp)
	Takes a ticker and a timestamp, and gets 5 options above and below the strike price

getOptionInfo(String ticker, datetime date, String optionType, float optionType, string contractSymbol)
	Given a string, it parses it and returns the corresponding option

getDurationInfo(String time, maxDur int)
	Takes a string of the duration and converts it into an integer

getChartInfo (String string)
	given a stirng as input, it splits and parses it using getDurationInfo and getOptionInfo

contractSymbolToInfo(String cSymbol)
	Given a contract symbol, it parses it into seperate pieces of information

contractSymbolToData (String cSymbol)
	Converts a contractSymbol to data

optionsPortfolioValue (list[String] array)
	Calculates the total portfolio value and changes

'''


# the base URL
baseURL = "https://query1.finance.yahoo.com/v7/finance/options/"

# loadFrom(String url)
# loads the data from the given URL
def loadFrom(url):
	with urllib.request.urlopen(url) as thisUrl:
		return json.loads(thisUrl.read().decode())





# parseContractInfo(String string)
# Parses the given string into the relevant terms
def parseContractInfo(string):
	split = string.upper().split() # Standardizes and splits the string

	if len(split) == 3: # Check for validity
		ticker, dateAndType, strike = split
	else:
		raise ValueError('String is not properly formatted')

	# Cleans the ticker, date, optionType, and strike
	ticker = re.sub('[^a-zA-Z]', '', ticker)
	date = parser.parse(dateAndType[:-1], tzinfos={None: 0})
	dateAsString = date.strftime('%y%m%d') 

	optionType = dateAndType[-1:]
	strike = re.sub('[^0-9.]', '', strike)
	strike, strikeAsString = sf.formatStrike(strike)

	# Concatenates the strings to form the contract symbol
	contractSymbol = "{0}{1}{2}{3}".format(ticker, dateAsString, optionType, strikeAsString)

	# Returns the ticker, the date, the option type, the strike, and the symbol
	return ticker, date, optionType, strike, contractSymbol



	

# parseChainInfo(String string)
# Given an option chain request, this returns the parsed ticker and date (if exists)
def parseChainInfo(string):
	# Two types of requests
	# just the ticker, or a ticker and a date

	string = string.upper() # Formats the string
	split = string.split() 

	ticker = re.sub('[^a-zA-Z]', '', split[0]) # Cleans the ticker

	# Checks if the date is included
	if len(split) == 1:
		date = None
	elif len(split) == 2:
		date = parser.parse(split[1], tzinfos={None: 0})
	else:
		raise ValueError('String is not properly formatted')

	# We now have a ticker, and might have a date
	return ticker, date





# parseChainInfoAtDate(String ticker, int timestamp)
# Takes a ticker and a timestamp, and gets 5 options above and below the strike price
def parseChainInfoAtDate(ticker, timestamp):
	url = baseURL + ticker + "?date=" + str(timestamp)
	print(url)

	# Loads all the data
	try: 
		data = loadFrom(url)['optionChain']['result'][0]
		allOptions = data['options'][0]
		strikes = data['strikes']
		lastPrice = data['quote']['regularMarketPreviousClose']
	except:
		raise ValueError("No data found")
		return

	# Finds the strikes closest to the lastPrice
	for i in range(5, len(strikes)-1):
		if strikes[i] >= lastPrice:
			strikesRange = [strikes[j] for j in range(i-5, i+6)]
			break

	# Grabs all the options with the aforementioned strikesRange
	calls = [option for option in allOptions['calls'] if option['strike'] in strikesRange]
	puts = [option for option in allOptions['puts'] if option['strike'] in strikesRange]

	return calls, puts





# getOptionInfo(String ticker, datetime date, String optionType, float optionType, string contractSymbol)
# Given a string, it parses it and returns the corresponding option
def getOptionInfo(ticker, date, optionType, strike, contractSymbol):
	timestamp = int(date.timestamp())

	url = baseURL + ticker + "?date=" + str(timestamp)
	data = loadFrom(url)['optionChain']['result'][0]

	# Gets the corresponding option type
	optionTypeStr = {'C': 'calls', 'P': 'puts'}[optionType]
	options = data['options'][0][optionTypeStr]

	thisOption = [option for option in options if option['contractSymbol'] == contractSymbol]

	try:
		thisOption = thisOption[0]
	except:
		raise ValueError("Could not find corresponding option")
		return

	return thisOption




# getStockInfo(String ticker)
# Given a string, it parses it and returns the corresponding stock
def getStockInfo(ticker):
	url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=" + ticker
	return loadFrom(url)['quoteResponse']['result'][0]






# getDurationInfo(String time, maxDur int)
# Takes a string of the duration and converts it into an integer
def getDurationInfo(durationAsStr, maxDur=60):
	number = int(durationAsStr[:-1]) # gets everything but the character denoting the multiplier
	multiplier = {"D": 1, "W": 7, "M": 30, "Y": 365}[durationAsStr[-1:]]
	return min(number * multiplier, maxDur)





# getChartInfo (String string)
# given a stirng as input, it splits and parses it using getDurationInfo and getOptionInfo
def getChartInfo(string):
	string = string.upper()
	time = string.split(" ")[-1]

	if time[-1:].isalpha():
		num = getDurationInfo(time)
	else: 
		num = int(time[-1:])
	try:
		contractInfo = string.replace(time, '')
		optionsInfo = getOptionInfo(parseContractInfo(contractInfo))
	except:
		raise ValueError("Couldn't parse the option info")
		return

	return num, optionsInfo




# contractSymbolToInfo(String cSymbol)
# Given a contract symbol, it parses it into seperate pieces of information
def contractSymbolToInfo(cSymbol):
	tickerAndDate = cSymbol[:-8] # Last 8 are always reserved for the strike price
	ticker = re.sub("[^a-zA-Z]", "", tickerAndDate[:-1]) # removes any non-alpha characters

	date = re.sub("[^0-9]", "", tickerAndDate)  # removes any non-numberic

	dateSplit = cSymbol.split(date)[1] # splits the string on the date (ie. returns the strike)

	strike = dateSplit[1:6] + "." + dateSplit[6:] # adds the deminal
 
	optionType = dateSplit[0:1] # parses the option type

	date = date[2:4] + "/" + date[4:] + "/20" + date[:2] # Formats the date
	date = parser.parse(date, tzinfos={None: 0}) # Creates the datetime object

	return ticker, date, optionType, strike
	




# contractSymbolToData (String cSymbol)
# Converts a contractSymbol to data
def contractSymbolToData(cSymbol):
	ticker, date, optionType, strike = contractSymbolToInfo(cSymbol)
	return getOptionInfo(ticker, date, optionType, strike, cSymbol)











#########
# TESTS #
#########

class TestStringMethods(unittest.TestCase):
	def initExamples(self, option):
		return parseContractInfo(option)


	def test_parse(self):
		t1, d1, o1, s1, str1 = self.initExamples("$SPY 4/17c $300")
		t2, d2, o2, s2, str2 = self.initExamples("spy 4/17c 300")
		t3, d3, o3, s3, str3 = self.initExamples("$spy 4/17C $300.00")
		t4, d4, o4, s4, str4 = self.initExamples("spy 4-17c 300")
		
		self.assertEqual(t1, t2)
		self.assertEqual(t1, t3)
		self.assertEqual(t1, t4)

		self.assertEqual(d1, d2)
		self.assertEqual(d1, d3)
		self.assertEqual(d1, d4)

		self.assertEqual(o1, o2)
		self.assertEqual(o1, o3)
		self.assertEqual(o1, o4)

		self.assertEqual(s1, s2)
		self.assertEqual(s1, s3)
		self.assertEqual(s1, s4)

		self.assertEqual(str1, str2)
		self.assertEqual(str1, str3)
		self.assertEqual(str1, str4)


if __name__ == "__main__":
    unittest.main()