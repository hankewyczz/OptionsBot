# A bot for parsing text into options data
from datetime import datetime
from dateutil import parser
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

parseDurationInfo(String time, maxDur int)
	Takes a string of the duration and converts it into an integer

contractSymbolToInfo(String cSymbol)
	Given a contract symbol, it parses it into seperate pieces of information

contractSymbolToData (String cSymbol)
	Converts a contractSymbol to data

optionsPortfolioValue (list[String] array)
	Calculates the total portfolio value and changes

'''

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

	split = string.upper().split() # Formats the string

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






# parseDurationInfo(String time, maxDur int)
# Takes a string of the duration and converts it into an integer
def parseDurationInfo(durationAsStr, maxDur=60):
	number = int(durationAsStr[:-1]) # gets everything but the character denoting the multiplier
	multiplier = {"D": 1, "W": 7, "M": 30, "Y": 365}[durationAsStr[-1:]]
	return min(number * multiplier, maxDur)

def test():
	return("Test")




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