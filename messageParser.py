# A bot for parsing text into options data
from datetime import datetime
from dateutil import parser, tz
import urllib.request
import json
import re
import unittest

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




##################### FIX
Main methods:
 - getOptionInfo(String)
 	Returns option info specific to ONE option (mainly used for price checks)

 	Takes in a string formatted as such: "^\$*[a-zA-Z] [0-9]\/*[0-9][[0-9]\/]* \$*[0-9][.[0-9]]*"
 		In other words, the string is divided into 3 parts:
 			The ticker, which is case insensitive and may or may not be prefixed with an "$"
 				(eg. SPY, $SPY, spy, $spy, sPy, etc are all valid)
			The date and option type, which have no space in between. 
				The date can be formatted MM/DD (most commonly), or, in case of LEAPS, MM/DD/YYYY
				The option type can be formatted as a "C" or a "P" (calls and puts, respectivly), and is case insensitive
				(eg. 4/17c, 4-17C, 04/17/20C, 2020-04-17c, 04/17C are all valid [and equal])
			The strike price, which may or may not be prefixed by "$", and may or may not have trailing decimals
				(eg. $105, 105, $105.00, 105.00, 105., 105.0, 105.000, etc. are all valid)
				Note: the strike price will accept at most 3 decimals (eg. XX.XXX). Any extras will be truncated

 - parseChainInfo(String)
 	Returns ALL options which pass the filter 

 	Takes in a string which can be formatted in one of four ways:
 		With just the ticker (eg. SPY, $SPY, etc)

 		With the ticker and a date (eg. SPY 4-17, spy 4/17, $spy 2020-04-17)

 		With the ticker and an option type (eg. spy c, SPY C, $SPY c)

 		With the ticker, date, and option type (eg. spy 4/17c, $SPY 4-17C, etc)

 - portfolioValue(Array)
 	Takes an array of contract symbols, and returns the total value, change, and percent change (respectivly)

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
	string = string.upper() # Standardizes the string
	split = string.split() # Splits it on all spaces

	if len(split) == 3:
		ticker = split[0]
		dateAndType = split[1]
		strike = split[2]
	else:
		raise ValueError('String is not properly formatted')

	# Strips the ticker of any other characters (should only be $)
	ticker = re.sub('[^a-zA-Z]', '', ticker)

	#gets the date, and the option type
	date = dateAndType[:-1]
	date = parser.parse(date, tzinfos={None: 0})
	dateAsString = date.strftime('%y%m%d')

	# Gets the option type
	optionType = dateAndType[-1:]

	#gets the bare stock price
	strike = re.sub('[^0-9.]', '', strike)

	# Formats the decimals of the stock price
	if "." in strike:
		length = len(strike.split(".")[1])
		if length > 3:
			strike += "." + length[:3] # Truncates it
		else:
			for i in range(length, 3):
				strike += "0"
	else:
		strike += ".000"

	# Gets the stock price as a string
	strikeAsString = re.sub('[^0-9]', '', strike)
	for i in range(len(strikeAsString), 8):
		strikeAsString = "0" + strikeAsString # Adds leading 0s to fill the string

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





# getOptionInfo(String string)
# Given a string, it parses it and returns the corresponding option

def getOptionInfo(string):
	# parses the string
	ticker, date, optionType, strike, contractSymbol = parseContractInfo(string)
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




def getDurationInfo(time, maxDur=60):
	num = int(time[:-1])
	mult = {"D": 1, "M": 30, "Y": 365}[time[-1:]]
	return min(num * mult, maxDur)

def getChartInfo(string):
	string = string.upper()
	time = string.split(" ")[-1]
	if time[-1:].isalpha():
		num = getDurationInfo(time)

	optionsInfo = getOptionInfo(string.replace(time, ''))
	return num, optionsInfo


def contractSymbolToInfo(string):
	tickerAndDate = string[:-8]
	ticker = re.match("^[a-zA-Z]+", tickerAndDate).group()

	date = re.sub("[^0-9]", "", tickerAndDate)

	dateSplit = string.split(date)[1]

	strike = dateSplit[1:6] + "." + dateSplit[6:]

	optionType = dateSplit[0:1]
	optionType = {"C": "calls", "P": "puts"}[optionType]

	date = date[2:4] + "/" + date[4:] + "/20" + date[:2]
	date = parser.parse(date, tzinfos={None: 0})

	

	return ticker, date, optionType, strike
	

def contractSymbolToData(string):
	ticker, date, optionType, strike = contractSymbolToInfo(string)

	timestamp = int(date.timestamp())

	url = baseURL + ticker + "?date=" + str(timestamp)

	data = loadFrom(url)['optionChain']['result'][0]['options'][0]

	for option in data[optionType]:
		if option['contractSymbol'] == string:
			return option


def portfolioValue(array):
	value = 0
	change = 0
	percentChange = 0
	for symbol in array:
		info = contractSymbolToData(symbol)
		value += info['lastPrice'] * 100
		change += info['change'] * 100
		percentChange += info['percentChange']
	return value, change, percentChange





#main("aapl 4/17c 105")
#print(contractSymbolToInfo("AAPL200424C00257500"))




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