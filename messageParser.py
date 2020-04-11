# A bot for parsing text into options data
from datetime import datetime
from dateutil import parser, tz
import urllib.request
import json
import re
import unittest

'''
Quick documentation:

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

 - getAllOptions(String)
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


# Parses the given string into the relevant terms
def stringParse(string):
	string = string.upper()
	split = string.split()
	if len(split) == 3:
		ticker = split[0]
		dateAndType = split[1]
		strike = split[2]
	else:
		raise ValueError('String is not properly formatted')

	# gets the bare ticker value
	onlyAlpha = re.compile('[^a-zA-Z]')
	ticker = onlyAlpha.sub('', ticker)

	#gets the date, and the option type
	date = dateAndType[:-1]
	date = parser.parse(date, tzinfos={None: 0})
	dateAsString = date.strftime('%y%m%d')

	optionType = dateAndType[-1:]

	#gets the bare stock price
	numAndDec = re.compile("[^0-9.]")
	strike = numAndDec.sub('', strike)

	if "." in strike:
		if len(strike.split(".")[1]) > 3:
			strike = strike + "." + strike.split(".")[1][:3]
		elif len(strike.split(".")[1]) == 2:
			strike += "0"	
		elif len(strike.split(".")[1]) == 1:
			strike += "00"
		elif len(strike.split(".")[1]) == 0:
			strike += "000"
		else:
			strike = strike
	else:
		strike += ".000"

	strikeAsString = re.sub("[^0-9]", "", strike)
	for i in range(len(strikeAsString), 8):
		strikeAsString = "0" + strikeAsString


	string = ticker + dateAsString + optionType + strikeAsString

	return ticker, date, optionType, strike, string

def getAllOptions(string):
	# Four types of calls
	# just the ticker
	# the ticker and a date
	# the ticker and a type
	# and the ticker and a date/type

	string = string.upper()
	split = string.split()
	ticker = re.sub('[^a-zA-Z]', '', split[0])

	if len(split) == 1:
		date = None
		optionType = None
	elif len(split) == 2:
		second = split[1]
		potentialTypes = ["C", "P", "CALLS", "CALL", "PUTS", "PUT"]
		if second in potentialTypes:
			optionType = second
			date = None
		elif second[-1:] in potentialTypes:
			optionType = second[-1:]
			date = parser.parse(second[:-1], tzinfos={None: 0})
		else:
			date = parser.parse(second, tzinfos={None: 0})
			optionType = None
	else:
		raise ValueError('String is not properly formatted')

	# We now have a ticker, and might have an optionType and a date
	return ticker, date, optionType
	

def getAllOptionsAtDate(ticker, ts, option=None):

	url = baseURL + ticker + "?date=" + str(ts)
	with urllib.request.urlopen(url) as thisUrl:
		data = json.loads(thisUrl.read().decode())
		data = data['optionChain']['result'][0]['options'][0]
	
	if option != None:
		optionTypeStr = {'C': 'calls', 'P': 'puts'}[option]
		options = data[optionTypeStr]
	else:
		options = data['calls'] + data['puts']

	return options

def getOptionInfo(string):
	ticker, date, optionType, strike, contractString = stringParse(string)
	timestamp = int(date.timestamp())

	url = baseURL + ticker + "?date=" + str(timestamp)
	with urllib.request.urlopen(url) as thisUrl:
		data = json.loads(thisUrl.read().decode())
		data = data['optionChain']['result'][0]

	optionTypeStr = {'C': 'calls', 'P': 'puts'}[optionType]
	options = data['options'][0][optionTypeStr]

	for option in options:
		if option['contractSymbol'] == contractString:
			thisOption = option

	return thisOption

def getChartInfo(string):
	string = string.upper()
	time = string.split(" ")[-1]
	if time[-1:].isalpha():
		num = int(time[:-1])
		mult = {"D": 1, "M": 30}[time[-1:]]
		num = min(num * mult, 60)

	optionsInfo = getOptionInfo(string.replace(time, ''))
	return num, optionsInfo


def contractStringToInfo(string):
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
	

def contractStringToData(string):
	ticker, date, optionType, strike = contractStringToInfo(string)

	timestamp = int(date.timestamp())

	url = baseURL + ticker + "?date=" + str(timestamp)

	with urllib.request.urlopen(url) as thisUrl:
		data = json.loads(thisUrl.read().decode())
		data = data['optionChain']['result'][0]['options'][0]

	for option in data[optionType]:
		if option['contractSymbol'] == string:
			return option


def portfolioValue(array):
	value = 0
	change = 0
	percentChange = 0
	for symbol in array:
		info = contractStringToData(symbol)
		value += info['lastPrice'] * 100
		change += info['change'] * 100
		percentChange += info['percentChange']
	return value, change, percentChange





#main("aapl 4/17c 105")
#print(contractStringToInfo("AAPL200424C00257500"))




#########
# TESTS #
#########

class TestStringMethods(unittest.TestCase):
	def initExamples(self, option):
		return stringParse(option)


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


#unittest.main()