# Utility functions for options
import urllib.request
import json
from datetime import datetime
import messageParser as mp





# the base URL
baseURL = "https://query1.finance.yahoo.com/v7/finance/options/"



# loadFrom(String url)
# loads the data from the given URL
def loadFrom(url):
	with urllib.request.urlopen(url) as thisUrl:
		return json.loads(thisUrl.read().decode())





# stocksPortfolioValue (list[String] array)
# Calculates the total portfolio value and changes
def stocksPortfolioValue(array):
	value = 0
	change = 0
	percentChange = 0
	for stockGroup in array:
		try:
			info = getStockInfo(stockGroup[0])
		except:
			raise ValueError("Couldn't parse the ticker")

		value += info['postMarketPrice'] * stockGroup[1]
		change += info['postMarketChange'] *  stockGroup[1]
		percentChange += info['postMarketChangePercent']

	return round(value, 2), round(change, 2), round(percentChange, 2)





# optionsPortfolioValue (list[String] array)
# Calculates the total portfolio value and changes
def optionsPortfolioValue(array):
	value = 0
	change = 0
	percentChange = 0
	for symbolGroup in array:
		try:
			info = mp.contractSymbolToData(symbolGroup[0])
		except:
			raise ValueError("Couldn't parse the contract symbols")

		value += info['lastPrice'] * 100 * symbolGroup[1]
		change += info['change'] * 100 * symbolGroup[1]
		percentChange += info['percentChange']
	return round(value, 2), round(change, 2), round(percentChange, 2)




# getStrikeRange(List[int] strikes, int lastPrice, int num)
# Returns "num" strike prices both above and below the lastPrice
def getStrikeRange(strikes, lastPrice, num=5):
	# Finds the strikes closest to the lastPrice
	for i in range(5, len(strikes)-1):
		if strikes[i] >= lastPrice:
			strikesRange = [strikes[j] for j in range(i - num, i + num + 1)]
			break

	return strikesRange





# getChainAtDate(String ticker, int timestamp)
# Takes a ticker and a timestamp, and gets 5 options above and below the strike price
def getChainAtDate(ticker, timestamp):
	url = baseURL + ticker + "?date=" + str(timestamp)

	# Loads all the data
	try: 
		data = loadFrom(url)['optionChain']['result'][0]
		options, strikes, lastPrice = data['options'][0], data['strikes'], data['quote']['regularMarketPreviousClose']
	except:
		raise ValueError("No data found")

	strikesRange = getStrikeRange(strikes, lastPrice)

	# Grabs all the options with the aforementioned strikesRange
	calls = [option for option in options['calls'] if option['strike'] in strikesRange]
	puts = [option for option in options['puts'] if option['strike'] in strikesRange]

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
	return thisOption







# getStockInfo(String ticker)
# Given a string, it parses it and returns the corresponding stock
def getStockInfo(ticker):
	url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=" + ticker
	return loadFrom(url)['quoteResponse']['result'][0]






# getChartInfo (String string)
# given a stirng as input, it splits and parses it using parseDurationInfo and getOptionInfo
def getChartInfo(string):
	string = string.upper()
	time = string.split(" ")[-1]

	if time[-1:].isalpha():
		try:
			num = mp.parseDurationInfo(time)
		except:
			raise ValueError("Couldn't parse the option info")

	else: 
		num = int(time[-1:])
	try:
		contractInfo = string.replace(time, '')
		t, d, o, s, cS = mp.parseContractInfo(contractInfo)
		optionsInfo = getOptionInfo(t, d, o, s, cS)
	except:
		raise ValueError("Couldn't parse the option info")

	return num, optionsInfo





# getChainDates (String ticker)
# Given the database, formats and prints the optionchain
def getChainDates(ticker):
	url = baseURL + ticker
	try:
		data = loadFrom(url)['optionChain']['result'][0]['expirationDates']
	except:
		raise ValueError("Could not load data from URL")

	result = ""
	year = datetime.now().year

	for datum in data:
		date = datetime.utcfromtimestamp(datum)
		if date.year == year:
			date = date.strftime('%b %d')
		else:
			date = date.strftime('%m/%d/%y')
		result += str(date) + ", "

	return result


# printChain(String ticker, int timestamp, Embed embed)
# Adds the given chain to the given embed, and returns the altered embed
def printChain(ticker, timestamp, embed):
	try:
		calls, puts = getChainAtDate(ticker, timestamp)
	except:
		raise ValueError("No data found for input")

	for i in range(0, len(calls)-1):
		# Formats the information displayed for each option
		value = ""
		for type in [calls, puts]:
			price = "**__Price__**: ${0}".format(round(type[i]['lastPrice'], 2))
			change = "{0}%".format(round(type[i]['percentChange'], 2))
			vol = "**__Vol / OI__**: {0} / {1}".format(type[i]['volume'], type[i]['openInterest'])

			value += "{0} ({1}),  {2}\n".format(price, change, vol)

		embed.add_field(name = "Strike: {}".format(calls[i]['strike']), value=value, inline=False)

	return embed