# Utility functions for options


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
			info = contractSymbolToData(symbolGroup[0])
		except:
			raise ValueError("Couldn't parse the contract symbols")

		value += info['lastPrice'] * 100 * symbolGroup[1]
		change += info['change'] * 100 * symbolGroup[1]
		percentChange += info['percentChange']
	return round(value, 2), round(change, 2), round(percentChange, 2)