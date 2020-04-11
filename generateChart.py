from datetime import datetime, timedelta
import urllib.request
import json
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as mtick
import numpy as np
import messageParser as mp


'''
##############
## OVERVIEW ##
##############

getData(String symbol, int length, int interval)
	Takes the ticker/contract symbol and the duration of the chart

extrapolateData(list[X] data, X prev, boolean append)
	Fills any blank spots in the data by extrapolating 

drawGraph(list[int] x, list[float] y, list[int] vol, String title, int length)
	Takes lists of x, y, and volume data, and draws a graph

generateChart(String string, String symbol, int length)
	Takes the given string, the contract symbol, and the length of data to be viewed)

'''

# The base URL for fetching the chart data. (Replace here if/when yahoo gets tired of people mooching off  their API
baseURL = "https://query1.finance.yahoo.com/v8/finance/chart/"

# (String symbol, int length, int interval)
# Takes the ticker/contract symbol and the duration of the chart
def getData(symbol, length, interval):
	# Gets the start and end dates of the chart based on the arg length
	endDate = datetime.now()
	startDate = endDate - timedelta(days=length)

	# Calculates the unix timestamps for the start/end dates
	period1 = int(startDate.timestamp())
	period2 = int(endDate.timestamp())
	
	# All the URL arguments
	# "interval" MUST be 2m. No clue why, but Yahoo throws a hissy fit if we try using other intervals, 
	# even though it lists [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo] as valid intervals
	urlArgs = {"period1": str(period1), "period2": str(period2), "interval": interval, "includePrePost": "true"}

	urlArgsString = ""
	for key in urlArgs.keys():
		urlArgsString = "{0}{1}={2}&".format(urlArgsString, key, urlArgs[key])

	# Oh yeah, it's all coming together
	url = "{0}{1}?{2}".format(baseURL, symbol, urlArgsString)
	print(url)

	# Grab the data from the URL
	data = mp.loadFrom(url)

	try:
		# Using time as the bellwether here - everything else, we can extrapolate
		time = data['chart']['result'][0]['timestamp']
	except:
		raise ValueError("Not enough data for a graph")

	price = data['chart']['result'][0]['indicators']['quote'][0]['close']
	volume = data['chart']['result'][0]['indicators']['quote'][0]['volume']
	try:
		prevClose = data['chart']['result'][0]['meta']['previousClose']
	except: 
		prevClose = data['chart']['result'][0]['meta']['chartPreviousClose']
	
	# Extrapolates data to fit every point (Yahoo has some [many] blind spots for some [most] contracts)
	price = extrapolateData(price, prevClose, True)
	volume = extrapolateData(volume, 0, False)

	# returns a list[int], list[float], list[int]
	return time, price, volume


# (list[X] data, X prev, boolean append)
# Fills any blank spots in the data by extrapolating 
def extrapolateData(data, prev, updatePrev):
	new = []
	for d in data:
		if d == None:
			new.append(prev)
		else:
			new.append(d)
			# Checks if the prev value should be updated (false for volume)
			if updatePrev:
				prev = d
	return new


# (list[int] x, list[float] y, list[int] vol, String title, int length)
# Takes lists of x, y, and volume data, and draws a graph
def drawGraph(x, y, vol, symbol, title, length):

	# Calculates the min and max of the y-axis (for price)
	# We don't want the max to be 0, so we take the max of (2 and the real max)
	yMax = int(max(2, np.max(y)))
	yMin = int(np.min(y))
	yRange = int((yMax - yMin) / 2)

	# Init
	fig, ax1 = plt.subplots()

	# Converts the timestamps in x into date objects
	dates = [datetime.fromtimestamp(date) for date in x]

	# Sets the max and min for the x-axis
	ax1.set_xlim(xmin = np.min(dates), xmax = np.max(dates))
	# Sets min/max for pricing. Min can never go below 0.
	ax1.set_ylim(ymin = max(0, yMin - yRange), ymax = yMax + yRange)

	# Sets the tick formatting for the prices y-axis
	yAxisPriceFormt = mtick.StrMethodFormatter('${x:,.0f}')
	ax1.yaxis.set_major_formatter(yAxisPriceFormt)

	# Initializes axes2 with identical xAxis
	ax2 = ax1.twinx()
	ax2.set_ylim(ymin = 0, ymax = max(vol) * 2) # So volume occupies the bottom half of the graph
	
	# Sets the tick formatting for the x-axis
	formatting = {1: ["%H:%M", 1, "%H:%M", 8], 2: ["%m/%d", 24, "%H:%M", 4], 5: ["%m/%d", 24, "%H:%M", 12], 10: ["%m/%d", 24, "%H:%M", 48]}

	# handles the smalle cases
	if length <= 10:
		if length > 5 and length < 10:
			length = 5
		elif length < 5 and length > 2:
			length = 2
		majF, majL, minF, minL = formatting[length][0], formatting[length][1], formatting[length][2], formatting[length][3]

	# long-term cases
	elif length > 10:
		length = round(length/10) * 10
		majF, majL, minF, minL = formatting[10][0], 24 * int(length/10), formatting[10][2], 48 * int(length/10)
	
	# Sets the x-axis date formats
	ax2.xaxis.set_major_formatter(md.DateFormatter(majF))
	ax2.xaxis.set_major_locator(md.HourLocator(interval=majL))
	ax2.xaxis.set_minor_formatter(md.DateFormatter(minF))
	ax2.xaxis.set_minor_locator(md.HourLocator(interval=minL))

	# Plots the volume
	ax2.plot(dates, vol, "#B2DCCB")
	l2 = ax2.fill_between(dates, vol, facecolor="#B2DCCB")

	# Plots the prices
	ax1.plot(dates, y, "#00A95D")
	l1 = ax1.fill_between(dates, y, facecolor="#00A95D")

	# Meta
	plt.title(title)
	plt.legend([l1, l2], ["Price", "Volume"]) # Legend for both
	name = "charts/" + symbol + '.png'
	plt.savefig(name)

	# Returns the filename
	return name

# (String string, String symbol, int length)
# Takes the given string, the contract symbol, and the length of data to be viewed
def generateChart(string, symbol, length, interval="2m"):
	time, price, volume = getData(symbol, length, interval)
	cleanTitle = string.upper()
	cleanTitle = cleanTitle.replace("$", "\$")

	return drawGraph(time, price, volume, symbol, cleanTitle, length)
